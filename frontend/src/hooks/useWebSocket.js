import { useState, useEffect, useRef, useCallback } from 'react';

/**
 * useWebSocket — Custom hook for WebSocket connections with auto-reconnect and heartbeat.
 * 
 * Auth is handled via the HttpOnly cookie (sent automatically by the browser).
 * No tokens in URL params — prevents leaking in server logs.
 */
export default function useWebSocket(url) {
  const [messages, setMessages] = useState([]);
  const [isConnected, setIsConnected] = useState(false);
  const [isTyping, setIsTyping] = useState(false);
  const wsRef = useRef(null);
  const reconnectTimeoutRef = useRef(null);
  const heartbeatRef = useRef(null);
  const reconnectAttemptsRef = useRef(0);
  const MAX_RECONNECT_ATTEMPTS = 5;
  const RECONNECT_DELAY_BASE = 1000; // ms

  const connect = useCallback(function connect() {
    if (wsRef.current && wsRef.current.readyState === WebSocket.OPEN) {
      return;
    }

    const ws = new WebSocket(url);
    wsRef.current = ws;

    ws.onopen = () => {
      setIsConnected(true);
      reconnectAttemptsRef.current = 0;

      // Start heartbeat (ping every 30s to keep connection alive)
      heartbeatRef.current = setInterval(() => {
        if (ws.readyState === WebSocket.OPEN) {
          ws.send(JSON.stringify({ type: 'ping' }));
        }
      }, 30000);
    };

    ws.onmessage = (event) => {
      try {
        const data = JSON.parse(event.data);

        if (data.type === 'typing') {
          setIsTyping(true);
          return;
        }

        setIsTyping(false);

        if (data.type === 'response' || data.type === 'system' || data.type === 'error') {
          setMessages((prev) => [
            ...prev,
            {
              id: data.chat_id || crypto.randomUUID(),
              sender: 'bot',
              text: data.message,
              type: data.type,
              timestamp: new Date(),
            },
          ]);
        }
      } catch {
        // Ignore non-JSON messages (e.g. pong)
      }
    };

    ws.onclose = (event) => {
      setIsConnected(false);
      setIsTyping(false);
      clearInterval(heartbeatRef.current);

      // Auto-reconnect with exponential backoff (unless auth failure)
      if (event.code !== 4001 && reconnectAttemptsRef.current < MAX_RECONNECT_ATTEMPTS) {
        const delay = RECONNECT_DELAY_BASE * Math.pow(2, reconnectAttemptsRef.current);
        reconnectAttemptsRef.current += 1;
        reconnectTimeoutRef.current = setTimeout(connect, delay);
      }
    };

    ws.onerror = () => {
      // onclose will fire after onerror, which handles reconnection
    };
  }, [url]);

  const sendMessage = useCallback((text) => {
    if (wsRef.current && wsRef.current.readyState === WebSocket.OPEN) {
      // Add user message to local state immediately
      setMessages((prev) => [
        ...prev,
        {
          id: crypto.randomUUID(),
          sender: 'user',
          text,
          type: 'message',
          timestamp: new Date(),
        },
      ]);

      wsRef.current.send(JSON.stringify({ message: text }));
    }
  }, []);

  const disconnect = useCallback(() => {
    clearTimeout(reconnectTimeoutRef.current);
    clearInterval(heartbeatRef.current);
    if (wsRef.current) {
      wsRef.current.close();
    }
  }, []);

  useEffect(() => {
    connect();
    return () => disconnect();
  }, [connect, disconnect]);

  return { messages, isConnected, isTyping, sendMessage, disconnect };
}
