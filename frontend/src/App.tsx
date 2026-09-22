import React, { useState, useEffect } from 'react';
import { Sidebar } from './components/Sidebar';
import { ChatPane } from './components/ChatPane';
import { ArtifactViewer } from './components/ArtifactViewer';
import { SourceInspector } from './components/SourceInspector';
import {
  Session,
  Message,
  Artifact,
  SourceCitation,
  fetchSessions,
  createSession,
  fetchSessionDetails,
  deleteSession,
  fetchArtifacts,
  streamChat
} from './lib/api';

export const App: React.FC = () => {
  const [sessions, setSessions] = useState<Session[]>([]);
  const [activeSessionId, setActiveSessionId] = useState<string | null>(null);
  const [activeSessionTitle, setActiveSessionTitle] = useState<string>('New Conversation');
  const [messages, setMessages] = useState<Message[]>([]);
  const [activeArtifact, setActiveArtifact] = useState<Artifact | null>(null);
  const [inspectedSource, setInspectedSource] = useState<SourceCitation | null>(null);
  const [currentProvider, setCurrentProvider] = useState<string>('ollama');
  const [isFallback, setIsFallback] = useState<boolean>(false);
  const [isStreaming, setIsStreaming] = useState<boolean>(false);
  const [retrievalStatus, setRetrievalStatus] = useState<string | null>(null);

  // Load sessions on mount
  useEffect(() => {
    loadSessions();
  }, []);

  const loadSessions = async () => {
    try {
      const data = await fetchSessions();
      setSessions(data);
      if (data.length > 0 && !activeSessionId) {
        selectSession(data[0].id);
      }
    } catch (e) {
      console.error('Failed to fetch sessions:', e);
    }
  };

  const selectSession = async (id: string) => {
    setActiveSessionId(id);
    try {
      const details = await fetchSessionDetails(id);
      setActiveSessionTitle(details.title);
      setMessages(details.messages || []);

      // Check if session has artifacts
      const arts = await fetchArtifacts(id);
      if (arts && arts.length > 0) {
        setActiveArtifact(arts[0]);
      } else {
        setActiveArtifact(null);
      }
    } catch (e) {
      console.error('Failed to load session details:', e);
    }
  };

  const handleNewChat = async () => {
    try {
      const newSess = await createSession('New Conversation');
      setSessions([newSess, ...sessions]);
      setActiveSessionId(newSess.id);
      setActiveSessionTitle(newSess.title);
      setMessages([]);
      setActiveArtifact(null);
    } catch (e) {
      console.error('Failed to create new session:', e);
    }
  };

  const handleDeleteSession = async (id: string) => {
    try {
      await deleteSession(id);
      const updated = sessions.filter((s) => s.id !== id);
      setSessions(updated);
      if (activeSessionId === id) {
        if (updated.length > 0) {
          selectSession(updated[0].id);
        } else {
          setActiveSessionId(null);
          setActiveSessionTitle('New Conversation');
          setMessages([]);
          setActiveArtifact(null);
        }
      }
    } catch (e) {
      console.error('Failed to delete session:', e);
    }
  };

  const handleSendMessage = async (text: string) => {
    if (!text.trim() || isStreaming) return;

    // Optimistically add user message
    const userMsg: Message = {
      id: `user-${Date.now()}`,
      session_id: activeSessionId || '',
      role: 'user',
      content: text,
      created_at: new Date().toISOString()
    };
    setMessages((prev) => [...prev, userMsg]);
    setIsStreaming(true);
    setRetrievalStatus('Scanning Lenny podcast knowledge base...');
    setIsFallback(false);

    let assistantMsgId = `asst-${Date.now()}`;
    let streamedContent = '';

    await streamChat(text, activeSessionId, currentProvider, {
      onStatus: (statusData) => {
        if (statusData.status === 'searching') {
          setRetrievalStatus('Searching Lenny transcript archive...');
        } else if (statusData.status === 'retrieved') {
          setRetrievalStatus(`Found ${statusData.chunk_count} verified transcript passages.`);
        }
      },
      onProvider: (prov) => {
        if (prov.provider) setCurrentProvider(prov.provider);
        if (prov.fallback) setIsFallback(true);
      },
      onText: (token) => {
        streamedContent += token;
        setMessages((prev) => {
          const filtered = prev.filter((m) => m.id !== assistantMsgId);
          return [
            ...filtered,
            {
              id: assistantMsgId,
              session_id: activeSessionId || '',
              role: 'assistant',
              content: streamedContent,
              created_at: new Date().toISOString()
            }
          ];
        });
      },
      onArtifact: (art) => {
        setActiveArtifact(art);
      },
      onDone: (doneData) => {
        setIsStreaming(false);
        setRetrievalStatus(null);
        if (doneData.session_id && !activeSessionId) {
          setActiveSessionId(doneData.session_id);
          loadSessions();
        }
        // Update final sources on message
        setMessages((prev) =>
          prev.map((m) =>
            m.id === assistantMsgId ? { ...m, sources: doneData.sources } : m
          )
        );
      },
      onError: (err) => {
        setIsStreaming(false);
        setRetrievalStatus(null);
        setMessages((prev) => [
          ...prev,
          {
            id: `err-${Date.now()}`,
            session_id: activeSessionId || '',
            role: 'assistant',
            content: `Error: Unable to complete request (${err.message}). Please check backend status.`,
            created_at: new Date().toISOString()
          }
        ]);
      }
    });
  };

  return (
    <div style={{ display: 'flex', width: '100vw', height: '100vh', overflow: 'hidden' }}>
      {/* Left Sidebar */}
      <Sidebar
        sessions={sessions}
        activeSessionId={activeSessionId}
        onSelectSession={selectSession}
        onNewChat={handleNewChat}
        onDeleteSession={handleDeleteSession}
      />

      {/* Center Chat Pane */}
      <ChatPane
        messages={messages}
        activeSessionTitle={activeSessionTitle}
        isStreaming={isStreaming}
        retrievalStatus={retrievalStatus}
        currentProvider={currentProvider}
        onSelectProvider={setCurrentProvider}
        isFallback={isFallback}
        onSendMessage={handleSendMessage}
        onCitationClick={(src) => setInspectedSource(src)}
        onOpenArtifact={(art) => setActiveArtifact(art)}
        activeArtifact={activeArtifact}
      />

      {/* Right Claude-style Artifact Viewer Pane (Collapsible) */}
      {activeArtifact && (
        <div style={{ width: '48%', minWidth: '380px', height: '100%' }}>
          <ArtifactViewer
            artifact={activeArtifact}
            onClose={() => setActiveArtifact(null)}
          />
        </div>
      )}

      {/* Verifiable Citation Source Inspector Modal */}
      <SourceInspector
        source={inspectedSource}
        onClose={() => setInspectedSource(null)}
      />
    </div>
  );
};
