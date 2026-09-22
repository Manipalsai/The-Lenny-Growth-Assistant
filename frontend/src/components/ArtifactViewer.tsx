import React, { useState } from 'react';
import { Eye, Code, Copy, Download, X, Check, FileText, Layout } from 'lucide-react';
import { Artifact } from '../lib/api';

interface ArtifactViewerProps {
  artifact: Artifact | null;
  onClose: () => void;
}

export const ArtifactViewer: React.FC<ArtifactViewerProps> = ({ artifact, onClose }) => {
  const [activeTab, setActiveTab] = useState<'preview' | 'code'>('preview');
  const [copied, setCopied] = useState(false);

  if (!artifact) return null;

  const handleCopy = async () => {
    await navigator.clipboard.writeText(artifact.content);
    setCopied(true);
    setTimeout(() => setCopied(false), 2000);
  };

  const handleDownload = () => {
    const ext = artifact.type === 'html' ? 'html' : 'md';
    const blob = new Blob([artifact.content], { type: 'text/plain;charset=utf-8' });
    const url = URL.createObjectURL(blob);
    const link = document.createElement('a');
    link.href = url;
    link.download = `${artifact.title.toLowerCase().replace(/\s+/g, '-')}.${ext}`;
    link.click();
    URL.revokeObjectURL(url);
  };

  return (
    <div style={{
      width: '100%',
      height: '100%',
      display: 'flex',
      flexDirection: 'column',
      background: '#0d131f',
      borderLeft: '1px solid #1e293b'
    }}>
      {/* Top Controls Header */}
      <div style={{
        padding: '12px 18px',
        borderBottom: '1px solid #1e293b',
        display: 'flex',
        alignItems: 'center',
        justifyContent: 'space-between',
        background: '#0f172a'
      }}>
        {/* Title & Badge */}
        <div style={{ display: 'flex', alignItems: 'center', gap: '8px', overflow: 'hidden' }}>
          {artifact.type === 'html' ? (
            <Layout size={16} color="#38bdf8" />
          ) : (
            <FileText size={16} color="#a855f7" />
          )}
          <span style={{
            fontSize: '13px',
            fontWeight: 600,
            color: '#f8fafc',
            whiteSpace: 'nowrap',
            overflow: 'hidden',
            textOverflow: 'ellipsis',
            maxWidth: '220px'
          }}>
            {artifact.title}
          </span>
          <span style={{
            fontSize: '10px',
            fontWeight: 700,
            textTransform: 'uppercase',
            padding: '2px 6px',
            borderRadius: '4px',
            background: artifact.type === 'html' ? 'rgba(56, 189, 248, 0.15)' : 'rgba(168, 85, 247, 0.15)',
            color: artifact.type === 'html' ? '#38bdf8' : '#c084fc',
            border: artifact.type === 'html' ? '1px solid rgba(56, 189, 248, 0.3)' : '1px solid rgba(168, 85, 247, 0.3)'
          }}>
            {artifact.type}
          </span>
        </div>

        {/* Tab & Action Controls */}
        <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
          <div style={{
            display: 'flex',
            background: '#1e293b',
            borderRadius: '6px',
            padding: '2px',
            border: '1px solid #334155'
          }}>
            <button
              onClick={() => setActiveTab('preview')}
              style={{
                display: 'flex',
                alignItems: 'center',
                gap: '4px',
                padding: '4px 8px',
                fontSize: '11px',
                fontWeight: 600,
                borderRadius: '4px',
                border: 'none',
                cursor: 'pointer',
                background: activeTab === 'preview' ? '#38bdf8' : 'transparent',
                color: activeTab === 'preview' ? '#0f172a' : '#94a3b8'
              }}
            >
              <Eye size={12} />
              Preview
            </button>
            <button
              onClick={() => setActiveTab('code')}
              style={{
                display: 'flex',
                alignItems: 'center',
                gap: '4px',
                padding: '4px 8px',
                fontSize: '11px',
                fontWeight: 600,
                borderRadius: '4px',
                border: 'none',
                cursor: 'pointer',
                background: activeTab === 'code' ? '#38bdf8' : 'transparent',
                color: activeTab === 'code' ? '#0f172a' : '#94a3b8'
              }}
            >
              <Code size={12} />
              Code
            </button>
          </div>

          <button
            onClick={handleCopy}
            title="Copy artifact code"
            style={{
              display: 'flex',
              alignItems: 'center',
              gap: '4px',
              padding: '5px 8px',
              background: '#1e293b',
              border: '1px solid #334155',
              borderRadius: '6px',
              color: copied ? '#10b981' : '#cbd5e1',
              cursor: 'pointer',
              fontSize: '11px'
            }}
          >
            {copied ? <Check size={12} /> : <Copy size={12} />}
            {copied ? 'Copied' : 'Copy'}
          </button>

          <button
            onClick={handleDownload}
            title="Download file"
            style={{
              display: 'flex',
              alignItems: 'center',
              padding: '5px 7px',
              background: '#1e293b',
              border: '1px solid #334155',
              borderRadius: '6px',
              color: '#cbd5e1',
              cursor: 'pointer'
            }}
          >
            <Download size={13} />
          </button>

          <button
            onClick={onClose}
            title="Close viewer"
            style={{
              display: 'flex',
              alignItems: 'center',
              padding: '5px 7px',
              background: 'transparent',
              border: 'none',
              color: '#94a3b8',
              cursor: 'pointer'
            }}
          >
            <X size={15} />
          </button>
        </div>
      </div>

      {/* Main Display Pane */}
      <div style={{ flex: 1, overflow: 'hidden', position: 'relative' }}>
        {activeTab === 'preview' ? (
          artifact.type === 'html' ? (
            /* Sandboxed isolated iframe with allow-scripts (NO allow-same-origin) */
            <iframe
              title="Artifact Preview Sandbox"
              sandbox="allow-scripts"
              srcDoc={artifact.content}
              style={{
                width: '100%',
                height: '100%',
                border: 'none',
                background: '#0f172a'
              }}
            />
          ) : (
            /* Rendered Markdown Preview */
            <div style={{
              height: '100%',
              overflowY: 'auto',
              padding: '24px',
              background: '#090d16',
              color: '#cbd5e1'
            }} className="markdown-body">
              <div dangerouslySetInnerHTML={{
                __html: artifact.content
                  .replace(/^# (.*$)/gim, '<h1>$1</h1>')
                  .replace(/^## (.*$)/gim, '<h2>$1</h2>')
                  .replace(/^### (.*$)/gim, '<h3>$1</h3>')
                  .replace(/^\> (.*$)/gim, '<blockquote>$1</blockquote>')
                  .replace(/\*\*(.*)\*\*/gim, '<strong>$1</strong>')
                  .replace(/\*(.*)\*/gim, '<em>$1</em>')
                  .replace(/`([^`]+)`/gim, '<code>$1</code>')
                  .replace(/^\- (.*$)/gim, '<li>$1</li>')
                  .replace(/\n\n/gim, '<p></p>')
              }} />
            </div>
          )
        ) : (
          /* Raw Source View */
          <pre style={{
            margin: 0,
            padding: '20px',
            height: '100%',
            overflowY: 'auto',
            background: '#050811',
            color: '#7dd3fc',
            fontFamily: '"JetBrains Mono", monospace',
            fontSize: '12px',
            lineHeight: '1.6'
          }}>
            <code>{artifact.content}</code>
          </pre>
        )}
      </div>
    </div>
  );
};
