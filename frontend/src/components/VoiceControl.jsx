import React, { useEffect, useRef } from 'react';
import { Mic, MicOff } from 'lucide-react';

export default function VoiceControl({
  isListening,
  appState,
  onToggleMic,
  partialTranscript
}) {
  const silenceTimerRef = useRef(null);
  const getStatusText = () => {
    switch (appState) {
      case 'LISTENING':
        return 'Listening... speak now';

      case 'PROCESSING':
        return 'Lyra is processing...';

      case 'RESPONDING':
      case 'SPEAKING':
        return 'Lyra is responding...';

      default:
        return 'Ready for voice input';
    }
  };
    useEffect(() => {
    if (!isListening) {
      if (silenceTimerRef.current) {
        clearTimeout(silenceTimerRef.current);
        silenceTimerRef.current = null;
      }
      return;
    }

    // Start a 3-second silence timer when listening begins
    if (silenceTimerRef.current) {
      clearTimeout(silenceTimerRef.current);
    }

    silenceTimerRef.current = setTimeout(() => {
      if (isListening) {
        onToggleMic();
      }
    }, 7000);

    return () => {
      if (silenceTimerRef.current) {
        clearTimeout(silenceTimerRef.current);
        silenceTimerRef.current = null;
      }
    };
  }, [isListening, partialTranscript, onToggleMic]);

  return (
    <div className="voice-control-container">
      <div className={`voice-center-control ${isListening ? 'active' : ''} ${appState?.toLowerCase() || ''}`}>
        
        <button
          className={`mic-main-btn ${isListening ? 'listening' : ''}`}
          onClick={onToggleMic}
          title={isListening ? 'Stop listening' : 'Click to speak'}
          aria-label={isListening ? 'Stop listening' : 'Click to speak'}
        >
          <span className="mic-pulse-ring ring-one"></span>
          <span className="mic-pulse-ring ring-two"></span>

          <span className="mic-icon">
            {isListening ? (
              <MicOff size={30} strokeWidth={1.8} />
            ) : (
              <Mic size={30} strokeWidth={1.8} />
            )}
          </span>
        </button>

        <div className="voice-status-info">
          <span className="voice-label">
            {isListening ? 'Listening...' : 'Click to speak'}
          </span>

          <span className="voice-state-subtitle">
            {getStatusText()}
          </span>
        </div>

      </div>
    </div>
  );
}