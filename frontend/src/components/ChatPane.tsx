import React, { useState, useRef, useEffect } from 'react';
import { Send, Sparkles, BookOpen, ExternalLink, Bot, User as UserIcon, Layout } from 'lucide-react';
import { Message, SourceCitation, Artifact } from '../lib/api';
import { ProviderBadge } from './ProviderBadge';

interface ChatPaneProps {
  messages: Message[];
  activeSessionTitle: string;
  isStreaming: boolean;
  retrievalStatus: string | null;
  currentProvider: string;
  onSelectProvider: (provider: string) => void;
  isFallback: boolean;
  onSendMessage: (text: string) => void;
  onCitationClick: (source: SourceCitation) => void;
  onOpenArtifact: (artifact: Artifact) => void;
  activeArtifact: Artifact | null;
}

export const ChatPane: React.FC<ChatPaneProps> = ({
  messages,
  activeSessionTitle,
  isStreaming,
  retrievalStatus,
  currentProvider,
  onSelectProvider,
  isFallback,
  onSendMessage,
  onCitationClick,
  onOpenArtifact,
  activeArtifact
}) => {
  const [input, setInput] = useState('');
  const messagesEndRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages, isStreaming, retrievalStatus]);

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    if (!input.trim() || isStreaming) return;
    onSendMessage(input.trim());
    setInput('');
  };

  const samplePrompts = [
    "What did Brian Chesky say about Founder Mode and Airbnb's product reviews?",
    "Explain Shreyas Doshi's LNO Framework and how PMs should prioritize tasks.",
    "What are Elena Verna's golden rules for B2B Product-Led Growth loops?",
    "Write a Ship 30 for 30 essay on finding Product-Market Fit based on Gustaf Alströmer's advice.",
    "Create an interactive HTML dashboard summarizing growth levers from the podcast."
  ];

  return (
    <div style={{
      flex: 1,
      height: '100%',
      display: 'flex',
      flexDirection: 'column',
      background: '#090d16',
      position: 'relative'
    }}>
      {/* Top Header */}
      <div style={{
        padding: '14px 20px',
        borderBottom: '1px solid #1e293b',
        display: 'flex',
        alignItems: 'center',
        justifyContent: 'space-between',
        background: '#0c1222'
      }}>
        <div>
          <h2 style={{ fontSize: '14px', fontWeight: 600, color: '#f8fafc' }}>
            {activeSessionTitle}
          </h2>
          <span style={{ fontSize: '11px', color: '#64748b' }}>
            Lenny Podcast Grounded Q&A
          </span>
        </div>

        <ProviderBadge
          currentProvider={currentProvider}
          onSelectProvider={onSelectProvider}
          isFallback={isFallback}
        />
      </div>

      {/* Message List */}
      <div style={{ flex: 1, overflowY: 'auto', padding: '24px 20px' }}>
        {messages.length === 0 ? (
          <div style={{ maxWidth: '640px', margin: '40px auto', textAlign: 'center' }}>
            <div style={{
              width: '48px',
              height: '48px',
              borderRadius: '12px',
              background: 'linear-gradient(135deg, #0284c7, #6366f1)',
              display: 'flex',
              alignItems: 'center',
              justifyContent: 'center',
              margin: '0 auto 16px auto',
              color: '#fff',
              boxShadow: '0 8px 24px rgba(2, 132, 199, 0.3)'
            }}>
              <Sparkles size={24} />
            </div>

            <h2 style={{ fontSize: '20px', fontWeight: 700, color: '#f8fafc', marginBottom: '8px' }}>
              Ask Lenny's Podcast Transcripts
            </h2>
            <p style={{ fontSize: '13px', color: '#94a3b8', lineHeight: 1.6, marginBottom: '24px' }}>
              Grounded product and growth insights strictly supported by verified interviews with Brian Chesky, Shreyas Doshi, Elena Verna, Gustaf Alströmer, and more.
            </p>

            <div style={{ display: 'flex', flexDirection: 'column', gap: '8px', textAlign: 'left' }}>
              <span style={{ fontSize: '11px', color: '#64748b', textTransform: 'uppercase', fontWeight: 700 }}>
                Suggested Prompts
              </span>
              {samplePrompts.map((p, idx) => (
                <button
                  key={idx}
                  onClick={() => onSendMessage(p)}
                  style={{
                    background: '#131d31',
                    border: '1px solid #1e293b',
                    borderRadius: '8px',
                    padding: '10px 14px',
                    color: '#e2e8f0',
                    fontSize: '13px',
                    textAlign: 'left',
                    cursor: 'pointer',
                    transition: 'all 0.15s ease'
                  }}
                  onMouseOver={(e) => {
                    e.currentTarget.style.borderColor = '#38bdf8';
                    e.currentTarget.style.background = '#1e293b';
                  }}
                  onMouseOut={(e) => {
                    e.currentTarget.style.borderColor = '#1e293b';
                    e.currentTarget.style.background = '#131d31';
                  }}
                >
                  {p}
                </button>
              ))}
            </div>
          </div>
        ) : (
          messages.map((m) => {
            const isUser = m.role === 'user';
            return (
              <div
                key={m.id}
                style={{
                  display: 'flex',
                  gap: '12px',
                  marginBottom: '20px',
                  maxWidth: '820px',
                  margin: '0 auto 20px auto'
                }}
              >
                {/* Avatar */}
                <div style={{
                  width: '32px',
                  height: '32px',
                  borderRadius: '8px',
                  background: isUser ? '#334155' : 'linear-gradient(135deg, #0284c7, #6366f1)',
                  display: 'flex',
                  alignItems: 'center',
                  justifyContent: 'center',
                  color: '#fff',
                  flexShrink: 0
                }}>
                  {isUser ? <UserIcon size={16} /> : <Bot size={16} />}
                </div>

                {/* Message Content */}
                <div style={{ flex: 1 }}>
                  <div style={{ fontSize: '12px', fontWeight: 600, color: isUser ? '#94a3b8' : '#38bdf8', marginBottom: '4px' }}>
                    {isUser ? 'You' : 'Lenny Assistant'}
                  </div>

                  <div
                    className="markdown-body"
                    style={{
                      background: isUser ? '#1e293b' : '#0e1626',
                      padding: '14px 16px',
                      borderRadius: '10px',
                      border: '1px solid #1e293b',
                      fontSize: '14px',
                      lineHeight: '1.6',
                      color: '#e2e8f0',
                      whiteSpace: 'pre-wrap'
                    }}
                  >
                    {m.content}
                  </div>

                  {/* Grounded Citations Bar */}
                  {m.sources && m.sources.length > 0 && (
                    <div style={{ display: 'flex', flexWrap: 'wrap', gap: '6px', marginTop: '8px', alignItems: 'center' }}>
                      <span style={{ fontSize: '11px', color: '#64748b', fontWeight: 600 }}>Sources:</span>
                      {m.sources.map((src, i) => (
                        <button
                          key={i}
                          className="citation-badge"
                          onClick={() => onCitationClick(src)}
                        >
                          <BookOpen size={11} />
                          {src.guest}: {src.topic || 'Key Insight'}
                        </button>
                      ))}
                    </div>
                  )}

                  {/* Suggested Follow-up Actions for assistant messages */}
                  {!isUser && !isStreaming && (
                    <div style={{ display: 'flex', flexWrap: 'wrap', gap: '6px', marginTop: '10px' }}>
                      <button
                        onClick={() => onSendMessage(`Turn this into a Ship 30 for 30 essay based on ${m.sources?.[0]?.guest || 'the podcast insights'}`)}
                        style={{
                          background: 'rgba(99, 102, 241, 0.1)',
                          border: '1px solid rgba(99, 102, 241, 0.3)',
                          color: '#a5b4fc',
                          fontSize: '11px',
                          fontWeight: 500,
                          borderRadius: '6px',
                          padding: '4px 10px',
                          cursor: 'pointer'
                        }}
                      >
                        ✍️ Create Ship 30 Essay
                      </button>

                      <button
                        onClick={() => onSendMessage(`Create an HTML dashboard visualizing this framework`)}
                        style={{
                          background: 'rgba(56, 189, 248, 0.1)',
                          border: '1px solid rgba(56, 189, 248, 0.3)',
                          color: '#7dd3fc',
                          fontSize: '11px',
                          fontWeight: 500,
                          borderRadius: '6px',
                          padding: '4px 10px',
                          cursor: 'pointer'
                        }}
                      >
                        📊 Build HTML Dashboard
                      </button>

                      <button
                        onClick={() => onSendMessage(`Generate a 1-page execution checklist from this`)}
                        style={{
                          background: 'rgba(16, 185, 129, 0.1)',
                          border: '1px solid rgba(16, 185, 129, 0.3)',
                          color: '#6ee7b7',
                          fontSize: '11px',
                          fontWeight: 500,
                          borderRadius: '6px',
                          padding: '4px 10px',
                          cursor: 'pointer'
                        }}
                      >
                        📋 1-Page Framework
                      </button>
                    </div>
                  )}
                </div>
              </div>
            );
          })
        )}

        {/* Retrieval Transparency Status */}
        {retrievalStatus && (
          <div style={{
            maxWidth: '820px',
            margin: '0 auto 12px auto',
            padding: '8px 14px',
            background: '#131d31',
            border: '1px solid #1e293b',
            borderRadius: '8px',
            fontSize: '12px',
            color: '#38bdf8',
            display: 'flex',
            alignItems: 'center',
            gap: '8px'
          }}>
            <Sparkles size={14} className="animate-pulse-subtle" />
            <span>{retrievalStatus}</span>
          </div>
        )}

        <div ref={messagesEndRef} />
      </div>

      {/* Input Bar */}
      <div style={{
        padding: '14px 20px',
        borderTop: '1px solid #1e293b',
        background: '#0a0f1d'
      }}>
        <form onSubmit={handleSubmit} style={{ maxWidth: '820px', margin: '0 auto', display: 'flex', gap: '8px' }}>
          <input
            type="text"
            value={input}
            onChange={(e) => setInput(e.target.value)}
            placeholder="Ask a product or growth question, or generate an artifact/essay..."
            disabled={isStreaming}
            style={{
              flex: 1,
              background: '#131d31',
              border: '1px solid #334155',
              borderRadius: '8px',
              padding: '10px 14px',
              fontSize: '14px',
              color: '#f8fafc',
              outline: 'none',
              transition: 'border-color 0.15s ease'
            }}
            onFocus={(e) => (e.target.style.borderColor = '#38bdf8')}
            onBlur={(e) => (e.target.style.borderColor = '#334155')}
          />
          <button
            type="submit"
            disabled={isStreaming || !input.trim()}
            style={{
              background: isStreaming || !input.trim() ? '#1e293b' : '#0284c7',
              border: 'none',
              borderRadius: '8px',
              color: '#fff',
              padding: '0 16px',
              display: 'flex',
              alignItems: 'center',
              justifyContent: 'center',
              cursor: isStreaming || !input.trim() ? 'not-allowed' : 'pointer',
              transition: 'background 0.15s ease'
            }}
          >
            <Send size={16} />
          </button>
        </form>
      </div>
    </div>
  );
};
