import React from 'react';
import { Plus, MessageSquare, Trash2, Database, Mic } from 'lucide-react';
import { Session } from '../lib/api';

interface SidebarProps {
  sessions: Session[];
  activeSessionId: string | null;
  onSelectSession: (id: string) => void;
  onNewChat: () => void;
  onDeleteSession: (id: string) => void;
}

export const Sidebar: React.FC<SidebarProps> = ({
  sessions,
  activeSessionId,
  onSelectSession,
  onNewChat,
  onDeleteSession
}) => {
  return (
    <div style={{
      width: '270px',
      height: '100%',
      background: '#0a0f1d',
      borderRight: '1px solid #1e293b',
      display: 'flex',
      flexDirection: 'column',
      flexShrink: 0
    }}>
      {/* Top Header */}
      <div style={{ padding: '16px', borderBottom: '1px solid #1e293b' }}>
        <div style={{ display: 'flex', alignItems: 'center', gap: '10px', marginBottom: '14px' }}>
          <div style={{
            width: '32px',
            height: '32px',
            borderRadius: '8px',
            background: 'linear-gradient(135deg, #0284c7, #6366f1)',
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'center',
            color: '#fff',
            boxShadow: '0 4px 12px rgba(2, 132, 199, 0.3)'
          }}>
            <Mic size={18} />
          </div>
          <div>
            <h1 style={{ fontSize: '14px', fontWeight: 700, color: '#f8fafc', letterSpacing: '-0.01em' }}>
              Lenny Assistant
            </h1>
            <span style={{ fontSize: '11px', color: '#38bdf8', fontWeight: 500 }}>
              Grounded Growth AI
            </span>
          </div>
        </div>

        <button
          onClick={onNewChat}
          style={{
            width: '100%',
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'center',
            gap: '8px',
            background: '#1e293b',
            border: '1px solid #334155',
            color: '#f8fafc',
            padding: '8px 14px',
            borderRadius: '8px',
            fontSize: '13px',
            fontWeight: 600,
            cursor: 'pointer',
            transition: 'all 0.15s ease'
          }}
          onMouseOver={(e) => (e.currentTarget.style.borderColor = '#38bdf8')}
          onMouseOut={(e) => (e.currentTarget.style.borderColor = '#334155')}
        >
          <Plus size={16} color="#38bdf8" />
          New Conversation
        </button>
      </div>

      {/* Session List */}
      <div style={{ flex: 1, overflowY: 'auto', padding: '12px 10px' }}>
        <div style={{ fontSize: '11px', color: '#64748b', textTransform: 'uppercase', fontWeight: 700, padding: '4px 8px', marginBottom: '6px' }}>
          Conversations
        </div>

        {sessions.length === 0 ? (
          <div style={{ padding: '16px 8px', textAlign: 'center', color: '#64748b', fontSize: '12px' }}>
            No previous chats
          </div>
        ) : (
          sessions.map((s) => {
            const isActive = s.id === activeSessionId;
            return (
              <div
                key={s.id}
                onClick={() => onSelectSession(s.id)}
                style={{
                  display: 'flex',
                  alignItems: 'center',
                  justifyContent: 'space-between',
                  padding: '8px 10px',
                  borderRadius: '8px',
                  marginBottom: '4px',
                  cursor: 'pointer',
                  background: isActive ? '#1e293b' : 'transparent',
                  border: isActive ? '1px solid #38bdf8' : '1px solid transparent',
                  transition: 'background 0.15s ease'
                }}
              >
                <div style={{ display: 'flex', alignItems: 'center', gap: '8px', overflow: 'hidden' }}>
                  <MessageSquare size={14} color={isActive ? '#38bdf8' : '#64748b'} />
                  <span style={{
                    fontSize: '12px',
                    color: isActive ? '#f8fafc' : '#94a3b8',
                    whiteSpace: 'nowrap',
                    overflow: 'hidden',
                    textOverflow: 'ellipsis',
                    maxWidth: '160px'
                  }}>
                    {s.title}
                  </span>
                </div>

                <button
                  onClick={(e) => {
                    e.stopPropagation();
                    onDeleteSession(s.id);
                  }}
                  style={{
                    background: 'transparent',
                    border: 'none',
                    color: '#64748b',
                    cursor: 'pointer',
                    padding: '3px',
                    display: 'flex',
                    opacity: 0.6
                  }}
                  onMouseOver={(e) => (e.currentTarget.style.opacity = '1')}
                  onMouseOut={(e) => (e.currentTarget.style.opacity = '0.6')}
                >
                  <Trash2 size={13} />
                </button>
              </div>
            );
          })
        )}
      </div>

      {/* Footer Knowledge Metadata Card */}
      <div style={{ padding: '14px', borderTop: '1px solid #1e293b', background: '#070b14' }}>
        <div style={{ display: 'flex', alignItems: 'center', gap: '8px', marginBottom: '6px' }}>
          <Database size={13} color="#10b981" />
          <span style={{ fontSize: '11px', fontWeight: 600, color: '#f8fafc' }}>
            Lenny Podcast Archive
          </span>
        </div>
        <p style={{ fontSize: '10px', color: '#64748b', lineHeight: 1.4 }}>
          Indexed Brian Chesky, Shreyas Doshi, Elena Verna, Gustaf Alströmer & more.
        </p>
      </div>
    </div>
  );
};
