import React, { useRef, useEffect } from 'react';
import Message from './Message';
import VoiceControl from './VoiceControl';

export default function ConversationPanel({
  transcript,
  partialTranscript,
  errorMessage,
  isListening,
  appState,
  onToggleMic
}) {
  const bottomRef = useRef(null);

  useEffect(() => {
    bottomRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [transcript, partialTranscript]);

  return (
    <section className="conversation-panel">
      <div className="panel-title-area">
        <h2 className="panel-main-title">LYRA</h2>
        <span className="panel-sub-title">
          Lyra - Intelligent Crowd Navigation Companion
        </span>
      </div>

      <div className="timeline-container">
        {errorMessage && (
          <div className="timeline-error-banner">
            <span>⚠ {errorMessage}</span>
          </div>
        )}

        {transcript.map((msg) => (
          <Message key={msg.id} message={msg} />
        ))}

        {partialTranscript && (
          <div className="timeline-item user-item partial-streaming">
            <div className="timeline-header">
              <span className="sender-label">
                USER (Speaking...)
              </span>
              <span className="timestamp">Live</span>
            </div>

            <div className="message-content partial">
              "{partialTranscript}"
            </div>
          </div>
        )}

        <div ref={bottomRef} />
      </div>

      <VoiceControl
  isListening={isListening}
  appState={appState}
  onToggleMic={onToggleMic}
  partialTranscript={partialTranscript}
/>
    </section>
  );
}