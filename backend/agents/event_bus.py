import json
import redis
import logging
import asyncio
from typing import Callable, Awaitable, Any
from django.conf import settings

logger = logging.getLogger(__name__)

class EventBus:
    """
    Redis Pub/Sub wrapper for Agent communication.
    Implements idempotency and basic retry logic.
    """
    def __init__(self):
        # We use a blocking client for publish (can be used synchronously in Django views)
        # and an async client for subscribe (used in the agent worker loop).
        self.redis_url = getattr(settings, 'REDIS_URL', 'redis://127.0.0.1:6379/0')
        self.sync_client = redis.Redis.from_url(self.redis_url, decode_responses=True)
        
    def publish(self, channel: str, event_data: dict) -> None:
        """Publish an event to the bus."""
        try:
            payload = json.dumps(event_data)
            self.sync_client.publish(channel, payload)
            logger.info(f"Published event to {channel}: {event_data.get('event_id', 'unknown')}")
        except Exception as e:
            logger.error(f"Failed to publish to {channel}: {str(e)}")
            raise e

    async def subscribe(self, channel: str, handler: Callable[[dict], Awaitable[Any]]) -> None:
        """
        Async subscriber loop. Connects to Redis, listens on channel, 
        and dispatches to the async handler.
        """
        import redis.asyncio as aioredis
        
        async_client = aioredis.from_url(self.redis_url, decode_responses=True)
        pubsub = async_client.pubsub()
        await pubsub.subscribe(channel)
        
        logger.info(f"Agent subscribed to channel: {channel}")
        
        try:
            async for message in pubsub.listen():
                if message['type'] == 'message':
                    try:
                        data = json.loads(message['data'])
                        event_id = data.get('event_id')
                        
                        # Idempotency check: Have we processed this event successfully?
                        # We use Redis SETNX with a 24h expiry
                        idempotency_key = f"processed_event:{channel}:{event_id}"
                        
                        # Use sync client for atomic SETNX check (could also use async, but sync is fine here)
                        if self.sync_client.setnx(idempotency_key, "1"):
                            self.sync_client.expire(idempotency_key, 86400) # 24h
                            
                            logger.info(f"Processing event from {channel}: {event_id}")
                            try:
                                await handler(data)
                            except Exception as handler_err:
                                # Processing failed, remove idempotency key so it can be retried
                                self.sync_client.delete(idempotency_key)
                                logger.error(f"Handler failed for {channel} event {event_id}: {str(handler_err)}")
                                # In a production system, we'd route to a dead-letter queue after N retries here
                        else:
                            logger.info(f"Skipping duplicate event {event_id} on {channel}")
                            
                    except json.JSONDecodeError:
                        logger.error(f"Malformed JSON on {channel}: {message['data']}")
                    except Exception as e:
                        logger.error(f"Error processing message on {channel}: {str(e)}")
        finally:
            await pubsub.unsubscribe(channel)
            await async_client.close()
