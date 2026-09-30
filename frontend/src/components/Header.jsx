import React from 'react';

export default function Header({ appState, backendStatus }) {
  const getStatusLabel = () => {
    switch (appState) {
      case 'LISTENING':
        return 'Listening';

      case 'PROCESSING':
        return 'Processing';

      case 'RESPONDING':
      case 'SPEAKING':
        return 'Responding';

      default:
        return 'Ready';
    }
  };

  return (
    <header className="console-header">
      <div className="header-left">
        <h1 className="brand-name">
          WALKJOURNEY AI
        </h1>

        <span className="brand-subtitle">
          AI - Based Crowd Navigation and Collision Prevention System
        </span>
      </div>

      <div className="header-right">
        <div className="agent-badge-group">

          <span className="agent-name">
            Lyra
          </span>

          <div
            className={`status-pill ${appState.toLowerCase()}`}
          >
            <span className="status-dot" />

            <span className="status-text">
              LIVE · {getStatusLabel()}
            </span>
          </div>

        </div>
      </div>
    </header>
  );
}