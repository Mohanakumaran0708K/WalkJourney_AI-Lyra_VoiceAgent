import React from 'react';

// Map raw tool names to short display labels for the tools badge
const TOOL_LABELS = {
  scene_understanding: 'Scene',
  crowd_analysis: 'Crowd',
  navigation_recommendation: 'Navigation',
  safety_check: 'Safety',
};

export default function Message({ message }) {
  const isUser = message.sender === 'user';
  const isFallback = message.status === 'fallback';

  return (
    <div className={`timeline-item ${isUser ? 'user-item' : 'lyra-item'}`}>
      <div className="timeline-header">
        <span className="sender-label">{isUser ? 'USER' : 'LYRA'}</span>
        <span className="timestamp">{message.timestamp}</span>
      </div>
      <div className="message-content">
        {message.text}

        {/* Tools used badge — shown only for Lyra responses with tool calls */}
        {!isUser && message.toolsUsed && message.toolsUsed.length > 0 && (
          <div className="tools-used-badge">
            <span className="tools-label">Tools:</span>
            <span className="tools-list">
              {message.toolsUsed
                .map((t) => TOOL_LABELS[t] || t)
                .join(' → ')}
            </span>
            {isFallback && (
              <span className="fallback-indicator" title="Lyra used local tools (LLM unavailable)">
                ⚡ local
              </span>
            )}
          </div>
        )}
      </div>
    </div>
  );
}
