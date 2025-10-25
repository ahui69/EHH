import React, { useState, useEffect, useRef } from 'react';
import { marked } from 'marked';
import DOMPurify from 'dompurify';
import { useChatStore } from '../store/chatStore';
import { chatAPI } from '../services/api';
import type { Message, ChatRequest } from '../types';

export const ChatArea: React.FC = () => {
  const {
    activeConversationId,
    conversations,
    addMessage,
    settings,
  } = useChatStore();

  const [input, setInput] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const messagesEndRef = useRef<HTMLDivElement>(null);

  const activeConversation = conversations.find(c => c.id === activeConversationId);

  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [activeConversation?.messages]);

  const handleSend = async () => {
    if (!input.trim() || !activeConversationId || isLoading) return;

    const userMessage: Message = {
      role: 'user',
      content: input.trim(),
      attachments: [],
    };

    addMessage(activeConversationId, userMessage);
    setInput('');
    setIsLoading(true);
    setError(null);

    try {
      const request: ChatRequest = {
        messages: [...(activeConversation?.messages || []), userMessage],
        user_id: settings.userId || 'default',
        use_memory: settings.useMemory,
        use_research: settings.useResearch,
        internet_allowed: settings.internetAccess,
        auto_learn: settings.autoLearn,
        use_batch_processing: settings.useBatchProcessing,
      };

      const response = await chatAPI.sendMessage(request);

      if (!response.ok) {
        throw new Error('Backend returned ok=false');
      }

      const assistantMessage: Message = {
        role: 'assistant',
        content: response.answer,
        attachments: response.sources || [],
      };

      addMessage(activeConversationId, assistantMessage);
    } catch (err) {
      const errorMsg = err instanceof Error ? err.message : 'Network error';
      setError(errorMsg);
      console.error('Chat error:', err);
    } finally {
      setIsLoading(false);
    }
  };

  const renderMessage = (msg: Message) => {
    const html = DOMPurify.sanitize(marked.parse(msg.content) as string);
    return (
      <div className={`message ${msg.role}`}>
        <div className="message-avatar">
          {msg.role === 'user' ? '👤' : '🤖'}
        </div>
        <div className="message-content" dangerouslySetInnerHTML={{ __html: html }} />
      </div>
    );
  };

  if (!activeConversationId) {
    return (
      <div className="chat-area empty">
        <p>Select a conversation or create a new one</p>
      </div>
    );
  }

  return (
    <div className="chat-area">
      <div className="messages">
        {activeConversation?.messages.map((msg, idx) => (
          <div key={idx}>{renderMessage(msg)}</div>
        ))}
        {isLoading && (
          <div className="message assistant loading">
            <div className="message-avatar">🤖</div>
            <div className="message-content">Thinking...</div>
          </div>
        )}
        {error && (
          <div className="error-banner">{error}</div>
        )}
        <div ref={messagesEndRef} />
      </div>

      <div className="input-area">
        <textarea
          value={input}
          onChange={(e) => setInput(e.target.value)}
          onKeyDown={(e) => {
            if (e.key === 'Enter' && !e.shiftKey) {
              e.preventDefault();
              handleSend();
            }
          }}
          placeholder="Type your message... (Shift+Enter for new line)"
          disabled={isLoading}
        />
        <button onClick={handleSend} disabled={isLoading || !input.trim()}>
          Send
        </button>
      </div>
    </div>
  );
};
export default ChatArea;
