import React from 'react';
import { X, BookOpen, User, Sparkles, ExternalLink } from 'lucide-react';
import { SourceCitation } from '../lib/api';

interface SourceInspectorProps {
  source: SourceCitation | null;
  onClose: () => void;
}

export const SourceInspector: React.FC<SourceInspectorProps> = ({ source, onClose }) => {
  if (!source) return null;

  const matchPercent = Math.min(Math.round(source.similarity * 100), 99);

  return (
    <div style={{
      position: 'fixed',
      inset: 0,
      background: 'rgba(0, 0, 0, 0.75)',
      backdropFilter: 'blur(4px)',
      display: 'flex',
      alignItems: 'center',
      justifyContent: 'center',
      zIndex: 1000,
      padding: '20px'
    }}>
      <div style={{
        background: '#0f172a',
        border: '1px solid #334155',
        borderRadius: '16px',
        width: '100%',
        maxWidth: '650px',
        boxShadow: '0 25px 50px -12px rgba(0, 0, 0, 0.5)',
        overflow: 'hidden',
        animation: 'fadeIn 0.15s ease-out'
      }}>
        {/* Header */}
        <div style={{
          padding: '16px 20px',
          borderBottom: '1px solid #1e293b',
          display: 'flex',
          justifyContent: 'space-between',
          alignItems: 'center',
          background: '#1e293b'
        }}>
          <div style={{ display: 'flex', alignItems: 'center', gap: '10px' }}>
            <BookOpen size={18} color="#38bdf8" />
            <h3 style={{ fontSize: '15px', fontWeight: 600, color: '#f8fafc' }}>
              Transcript Source Inspector
            </h3>
          </div>
          <button
            onClick={onClose}
            style={{
              background: 'transparent',
              border: 'none',
              color: '#94a3b8',
              cursor: 'pointer',
              display: 'flex',
              padding: '4px',
              borderRadius: '6px'
            }}
          >
            <X size={18} />
          </button>
        </div>

        {/* Body Content */}
        <div style={{ padding: '20px', maxHeight: '75vh', overflowY: 'auto' }}>
          {/* Metadata Grid */}
          <div style={{
            display: 'grid',
            gridTemplateColumns: 'repeat(auto-fit, minmax(180px, 1fr))',
            gap: '12px',
            marginBottom: '16px',
            padding: '12px',
            background: '#131d31',
            borderRadius: '10px',
            border: '1px solid #1e293b'
          }}>
            <div>
              <span style={{ fontSize: '11px', color: '#64748b', textTransform: 'uppercase', fontWeight: 600 }}>Speaker / Guest</span>
              <div style={{ display: 'flex', alignItems: 'center', gap: '6px', marginTop: '2px', color: '#38bdf8', fontWeight: 600, fontSize: '14px' }}>
                <User size={14} />
                {source.guest}
              </div>
            </div>

            <div>
              <span style={{ fontSize: '11px', color: '#64748b', textTransform: 'uppercase', fontWeight: 600 }}>Topic / Timestamp</span>
              <div style={{ marginTop: '2px', color: '#e2e8f0', fontWeight: 500, fontSize: '13px' }}>
                {source.topic || 'Episode Discussion'}
              </div>
            </div>

            <div>
              <span style={{ fontSize: '11px', color: '#64748b', textTransform: 'uppercase', fontWeight: 600 }}>Relevance Confidence</span>
              <div style={{ display: 'flex', alignItems: 'center', gap: '5px', marginTop: '2px', color: '#10b981', fontWeight: 600, fontSize: '13px' }}>
                <Sparkles size={14} />
                {matchPercent > 0 ? `${matchPercent}% Grounded` : 'Grounded Evidence'}
              </div>
            </div>
          </div>

          {/* Episode Title */}
          <div style={{ marginBottom: '14px' }}>
            <span style={{ fontSize: '11px', color: '#64748b', textTransform: 'uppercase', fontWeight: 600 }}>Episode</span>
            <h4 style={{ fontSize: '14px', color: '#f1f5f9', fontWeight: 600, marginTop: '2px' }}>
              {source.episode}
            </h4>
          </div>

          {/* Verbatim Passage */}
          <div style={{ marginBottom: '16px' }}>
            <span style={{ fontSize: '11px', color: '#64748b', textTransform: 'uppercase', fontWeight: 600 }}>Verbatim Transcript Passage</span>
            <div style={{
              marginTop: '6px',
              padding: '14px',
              background: '#090d16',
              border: '1px solid #1e293b',
              borderRadius: '8px',
              fontSize: '13px',
              lineHeight: '1.6',
              color: '#cbd5e1',
              fontStyle: 'italic',
              borderLeft: '4px solid #38bdf8'
            }}>
              "{source.passage}"
            </div>
          </div>

          {source.source_url && (
            <a
              href={source.source_url}
              target="_blank"
              rel="noopener noreferrer"
              style={{
                display: 'inline-flex',
                alignItems: 'center',
                gap: '6px',
                fontSize: '12px',
                color: '#38bdf8',
                textDecoration: 'none',
                fontWeight: 500
              }}
            >
              <ExternalLink size={13} />
              Listen to Episode on Lenny's Podcast
            </a>
          )}
        </div>
      </div>
    </div>
  );
};
