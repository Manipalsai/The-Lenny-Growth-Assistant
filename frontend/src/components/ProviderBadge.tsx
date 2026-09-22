import React from 'react';
import { Cpu, Cloud, ChevronDown } from 'lucide-react';

interface ProviderBadgeProps {
  currentProvider: string;
  onSelectProvider: (provider: string) => void;
  isFallback?: boolean;
}

export const ProviderBadge: React.FC<ProviderBadgeProps> = ({
  currentProvider,
  onSelectProvider,
  isFallback
}) => {
  const isOllama = currentProvider.toLowerCase() === 'ollama';

  return (
    <div style={{ display: 'inline-flex', alignItems: 'center', gap: '8px', background: '#1e293b', border: '1px solid #334155', borderRadius: '8px', padding: '4px 10px' }}>
      {isOllama ? (
        <Cpu size={14} color="#38bdf8" />
      ) : (
        <Cloud size={14} color="#a855f7" />
      )}
      <span style={{ fontSize: '12px', fontWeight: 500, color: '#94a3b8' }}>
        Provider:
      </span>
      <select
        value={currentProvider}
        onChange={(e) => onSelectProvider(e.target.value)}
        style={{
          background: 'transparent',
          border: 'none',
          color: isOllama ? '#38bdf8' : '#c084fc',
          fontSize: '12px',
          fontWeight: 600,
          cursor: 'pointer',
          outline: 'none'
        }}
      >
        <option value="ollama" style={{ background: '#1e293b', color: '#f8fafc' }}>Ollama (Local llama3.2:3b)</option>
        <option value="openai" style={{ background: '#1e293b', color: '#f8fafc' }}>OpenAI (Cloud gpt-4o-mini)</option>
        <option value="anthropic" style={{ background: '#1e293b', color: '#f8fafc' }}>Anthropic (Cloud Claude 3.5)</option>
      </select>
      {isFallback && (
        <span style={{ background: '#f59e0b', color: '#000', fontSize: '10px', padding: '1px 5px', borderRadius: '4px', fontWeight: 700 }}>
          FALLBACK ACTIVE
        </span>
      )}
    </div>
  );
};
