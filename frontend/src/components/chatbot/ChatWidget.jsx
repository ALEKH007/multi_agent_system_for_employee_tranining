import { useState, useRef, useEffect } from 'react';
import useWebSocket from '../../hooks/useWebSocket';
import './ChatWidget.css';

const WS_URL = import.meta.env.VITE_WS_BASE_URL
  ? `${import.meta.env.VITE_WS_BASE_URL}/chat/`
  : 'ws://localhost:8000/ws/chat/';

export default function ChatWidget() {
  const [isOpen, setIsOpen] = useState(false);
  const [inputValue, setInputValue] = useState('');
  const messagesEndRef = useRef(null);
  const inputRef = useRef(null);

  const { messages, isConnected, isTyping, sendMessage } = useWebSocket(WS_URL);

  // Auto-scroll to bottom on new messages
  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages, isTyping]);

  // Focus input when chat opens
  useEffect(() => {
    if (isOpen && inputRef.current) {
      inputRef.current.focus();
    }
  }, [isOpen]);

  const handleSend = () => {
    const trimmed = inputValue.trim();
    if (!trimmed) return;
    sendMessage(trimmed);
    setInputValue('');
  };

  const handleKeyDown = (e) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleSend();
    }
  };

  const formatTime = (date) => {
    return new Date(date).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' });
  };

  return (
    <>
      {/* Floating Action Button */}
      <button
        id="chat-toggle-btn"
        className={`chat-fab ${isOpen ? 'chat-fab--open' : ''}`}
        onClick={() => setIsOpen(!isOpen)}
        aria-label={isOpen ? 'Close chat' : 'Open chat assistant'}
      >
        {isOpen ? (
          <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
            <line x1="18" y1="6" x2="6" y2="18" />
            <line x1="6" y1="6" x2="18" y2="18" />
          </svg>
        ) : (
          <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
            <path d="M21 15a2 2 0 0 1-2 2H7l-4 4V5a2 2 0 0 1 2-2h14a2 2 0 0 1 2 2z" />
          </svg>
        )}
      </button>

      {/* Chat Window */}
      <div className={`chat-window ${isOpen ? 'chat-window--open' : ''}`} role="dialog" aria-label="Chat assistant">
        {/* Header */}
        <div className="chat-header">
          <div className="chat-header__info">
            <div className={`chat-header__status ${isConnected ? 'chat-header__status--online' : ''}`} />
            <div>
              <h3 className="chat-header__title">AI Training Assistant</h3>
              <span className="chat-header__subtitle">
                {isConnected ? 'Online' : 'Reconnecting...'}
              </span>
            </div>
          </div>
          <button
            id="chat-close-btn"
            className="chat-header__close"
            onClick={() => setIsOpen(false)}
            aria-label="Close chat"
          >
            <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
              <line x1="18" y1="6" x2="6" y2="18" />
              <line x1="6" y1="6" x2="18" y2="18" />
            </svg>
          </button>
        </div>

        {/* Messages */}
        <div className="chat-messages" id="chat-messages-container">
          {messages.length === 0 && (
            <div className="chat-empty">
              <div className="chat-empty__icon">💬</div>
              <p>Ask me anything about your training, onboarding, or company policies!</p>
            </div>
          )}

          {messages.map((msg) => (
            <div
              key={msg.id}
              className={`chat-bubble ${msg.sender === 'user' ? 'chat-bubble--user' : 'chat-bubble--bot'} ${msg.type === 'error' ? 'chat-bubble--error' : ''} ${msg.type === 'system' ? 'chat-bubble--system' : ''}`}
            >
              {/* Use textContent-equivalent (React's default) — NOT dangerouslySetInnerHTML (XSS prevention) */}
              <p className="chat-bubble__text">{msg.text}</p>
              <span className="chat-bubble__time">{formatTime(msg.timestamp)}</span>
            </div>
          ))}

          {isTyping && (
            <div className="chat-bubble chat-bubble--bot chat-bubble--typing">
              <div className="typing-indicator">
                <span></span>
                <span></span>
                <span></span>
              </div>
            </div>
          )}

          <div ref={messagesEndRef} />
        </div>

        {/* Input */}
        <div className="chat-input-area">
          <input
            id="chat-input"
            ref={inputRef}
            type="text"
            className="chat-input"
            placeholder={isConnected ? 'Type your message...' : 'Connecting...'}
            value={inputValue}
            onChange={(e) => setInputValue(e.target.value)}
            onKeyDown={handleKeyDown}
            disabled={!isConnected}
            maxLength={2000}
            autoComplete="off"
          />
          <button
            id="chat-send-btn"
            className="chat-send-btn"
            onClick={handleSend}
            disabled={!isConnected || !inputValue.trim()}
            aria-label="Send message"
          >
            <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
              <line x1="22" y1="2" x2="11" y2="13" />
              <polygon points="22 2 15 22 11 13 2 9 22 2" />
            </svg>
          </button>
        </div>
      </div>
    </>
  );
}
