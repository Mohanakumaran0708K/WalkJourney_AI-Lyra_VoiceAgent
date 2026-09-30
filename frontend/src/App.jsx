import React, { useState, useEffect, useRef } from 'react';
import Header from './components/Header';
import ConversationPanel from './components/ConversationPanel';
import SystemStatus from './components/SystemStatus';
import { AudioStreamer } from './utils/audioStreamer';
import './index.css';

const API_BASE_URL = 'http://localhost:8000/api/v1';

export default function App() {
  const [backendStatus, setBackendStatus] = useState('online');
  const [appState, setAppState] = useState('READY');
  const [isListening, setIsListening] = useState(false);
  const [partialTranscript, setPartialTranscript] = useState('');
  const [errorMessage, setErrorMessage] = useState('');

  const [transcript, setTranscript] = useState([
    {
      id: 'msg-1',
      sender: 'user',
      text: "What's ahead of me?",
      timestamp: '12:04 PM'
    },
    {
      id: 'msg-2',
      sender: 'agent',
      text: 'The path ahead is moderately crowded. I recommend moving slightly to your left.',
      timestamp: '12:04 PM'
    },
    {
      id: 'msg-3',
      sender: 'user',
      text: 'Is the left side clear?',
      timestamp: '12:05 PM'
    },
    {
      id: 'msg-4',
      sender: 'agent',
      text: 'Yes. The left side appears clearer. Continue slightly left.',
      timestamp: '12:05 PM'
    }
  ]);

  const audioStreamerRef = useRef(new AudioStreamer());

  // HARD LOCK:
  // true while Lyra is speaking.
  // Prevents Lyra's own voice from entering AssemblyAI.
  const lyraSpeakingRef = useRef(false);

  /* =========================================================
     LYRA TEXT-TO-SPEECH
     ========================================================= */

  const speakLyra = (text) => {
    if (!text || !('speechSynthesis' in window)) {
      return;
    }

    // =======================================================
    // HARD MICROPHONE LOCK
    // =======================================================

    lyraSpeakingRef.current = true;

    // Stop microphone immediately.
    try {
      audioStreamerRef.current.stop();
    } catch (error) {
      console.warn('Could not stop microphone:', error);
    }

    setIsListening(false);
    setPartialTranscript('');
    setAppState('SPEAKING');

    // Stop any previous speech.
    window.speechSynthesis.cancel();

    const utterance = new SpeechSynthesisUtterance(text);

    utterance.lang = 'en-US';
    utterance.rate = 0.95;
    utterance.pitch = 1.0;
    utterance.volume = 1.0;

    // Prefer natural English voice.
    const voices = window.speechSynthesis.getVoices();
    const preferredVoice =
  voices.find(
    (voice) =>
      voice.lang === 'en-US' &&
      /female|samantha|zira|jenny|aria|ava|susan|google us english/i.test(
        voice.name
      )
  ) ||
  voices.find(
    (voice) =>
      voice.lang.startsWith('en') &&
      /female|samantha|zira|jenny|aria|ava|susan/i.test(
        voice.name
      )
  ) ||
  voices.find(
    (voice) =>
      voice.lang === 'en-US' &&
      /Google|Microsoft|Natural/i.test(voice.name)
  ) ||
  voices.find((voice) =>
    voice.lang.startsWith('en')
  );

    if (preferredVoice) {
      utterance.voice = preferredVoice;
    }

    // =======================================================
    // TTS START
    // =======================================================

    utterance.onstart = () => {
      lyraSpeakingRef.current = true;

      // Make absolutely sure the microphone stays off.
      try {
        audioStreamerRef.current.stop();
      } catch (error) {
        console.warn('Could not stop microphone during TTS:', error);
      }

      setIsListening(false);
      setPartialTranscript('');
      setAppState('SPEAKING');
    };

    // =======================================================
    // TTS END
    // =======================================================

    utterance.onend = () => {
      lyraSpeakingRef.current = false;

      setIsListening(false);
      setPartialTranscript('');
      setAppState('READY');
    };

    // =======================================================
    // TTS ERROR
    // =======================================================

    utterance.onerror = (event) => {
      console.warn('Lyra TTS error:', event.error);

      lyraSpeakingRef.current = false;

      setIsListening(false);
      setPartialTranscript('');
      setAppState('READY');
    };

    window.speechSynthesis.speak(utterance);
  };

  /* =========================================================
     BACKEND HEALTH CHECK
     ========================================================= */

  useEffect(() => {
    const checkBackend = async () => {
      try {
        const response = await fetch(`${API_BASE_URL}/health`);

        if (response.ok) {
          setBackendStatus('online');
        } else {
          setBackendStatus('offline');
        }
      } catch {
        setBackendStatus('offline');
      }
    };

    checkBackend();

    const interval = setInterval(checkBackend, 5000);

    return () => clearInterval(interval);
  }, []);

  /* =========================================================
     AUDIO CLEANUP
     ========================================================= */

  useEffect(() => {
    return () => {
      audioStreamerRef.current.stop();

      if ('speechSynthesis' in window) {
        window.speechSynthesis.cancel();
      }

      lyraSpeakingRef.current = false;
    };
  }, []);

  /* =========================================================
     ASSEMBLYAI + LYRA EVENTS
     ========================================================= */

  const handleAssemblyAIEvent = (event) => {
    switch (event.type) {

      /* =====================================================
         SESSION STARTED
         ===================================================== */

      case 'session_started':

        // NEVER allow a new microphone session
        // while Lyra is speaking.
        if (lyraSpeakingRef.current) {
          try {
            audioStreamerRef.current.stop();
          } catch (error) {
            console.warn(
              'Blocked microphone session during Lyra speech:',
              error
            );
          }

          setIsListening(false);
          break;
        }

        setIsListening(true);
        setAppState('LISTENING');
        setPartialTranscript('');
        setErrorMessage('');

        break;

      /* =====================================================
         PARTIAL TRANSCRIPT
         ===================================================== */

      case 'partial_transcript':

        // Ignore anything captured while Lyra speaks.
        if (lyraSpeakingRef.current) {
          break;
        }

        if (event.text) {
          setAppState('LISTENING');
          setPartialTranscript(event.text);
        }

        break;

      /* =====================================================
         FINAL TRANSCRIPT
         ===================================================== */

      case 'final_transcript':

        // Ignore Lyra's own voice.
        if (lyraSpeakingRef.current) {
          break;
        }

        if (event.text) {
          setPartialTranscript('');
          setAppState('PROCESSING');

          const userMsg = {
            id: Date.now().toString(),
            sender: 'user',
            text: event.text,
            timestamp: new Date().toLocaleTimeString([], {
              hour: '2-digit',
              minute: '2-digit'
            })
          };

          setTranscript((prev) => [
            ...prev,
            userMsg
          ]);
        }

        break;

      /* =====================================================
         LYRA RESPONSE
         ===================================================== */

      case 'lyra_response':
      case 'agent_response':

        setAppState('RESPONDING');

        // ===================================================
        // HARD STOP MICROPHONE
        // ===================================================
        // DO NOT check `isListening`.
        // Always stop the audio streamer.
        // ===================================================

        try {
          audioStreamerRef.current.stop();
        } catch (error) {
          console.warn(
            'Could not stop microphone before Lyra response:',
            error
          );
        }

        setIsListening(false);
        setPartialTranscript('');

        // ===================================================
        // LYRA RESPONSE
        // ===================================================

        if (event.response) {

          // Start TTS.
          // speakLyra() also activates the hard lock.
          speakLyra(event.response);

          // Add Lyra response to conversation.
          setTranscript((prev) => [
            ...prev,
            {
              id: (Date.now() + 1).toString(),
              sender: 'agent',
              text: event.response,
              toolsUsed: event.tools_used || [],
              status: event.status || 'success',
              timestamp: new Date().toLocaleTimeString([], {
                hour: '2-digit',
                minute: '2-digit'
              })
            }
          ]);
        }

        break;

      /* =====================================================
         SESSION ENDED
         ===================================================== */

      case 'session_ended':

        // Don't allow session-ended events to
        // interfere with TTS state.
        if (lyraSpeakingRef.current) {
          setIsListening(false);
          setPartialTranscript('');
          break;
        }

        setIsListening(false);
        setAppState('READY');
        setPartialTranscript('');

        break;

      /* =====================================================
         ERROR
         ===================================================== */

      case 'error':

        setErrorMessage(
          event.message || 'AssemblyAI streaming error'
        );

        setAppState('ERROR');
        setIsListening(false);
        setPartialTranscript('');

        break;

      /* =====================================================
         UNKNOWN EVENT
         ===================================================== */

      default:
        break;
    }
  };

  /* =========================================================
     STREAM ERROR
     ========================================================= */

  const handleStreamError = (err) => {
    console.error('Audio streaming error:', err);

    setErrorMessage(
      err.message ||
      'Failed to access microphone or WebSocket connection.'
    );

    setAppState('ERROR');
    setIsListening(false);
    setPartialTranscript('');
  };

  /* =========================================================
     MICROPHONE CONTROL
     ========================================================= */

  const toggleMic = async () => {

    // =======================================================
    // HARD BLOCK:
    // NEVER start microphone while Lyra is speaking.
    // =======================================================

    if (lyraSpeakingRef.current) {
      console.log(
        'Microphone blocked: Lyra is currently speaking.'
      );

      return;
    }

    // =======================================================
    // STOP CURRENT LISTENING SESSION
    // =======================================================

    if (isListening) {

      try {
        audioStreamerRef.current.stop();
      } catch (error) {
        console.warn(
          'Could not stop microphone:',
          error
        );
      }

      setIsListening(false);
      setAppState('READY');
      setPartialTranscript('');

      return;
    }

    // =======================================================
    // START NEW LISTENING SESSION
    // =======================================================

    setErrorMessage('');
    setAppState('CONNECTING');

    try {

      await audioStreamerRef.current.start(
        handleAssemblyAIEvent,
        handleStreamError
      );

    } catch (err) {

      handleStreamError(err);
    }
  };

  /* =========================================================
     UI
     ========================================================= */

  return (
    <div className="app-shell">

      <Header
        appState={appState}
        backendStatus={backendStatus}
      />

      <main className="main-console-grid">

        <ConversationPanel
          transcript={transcript}
          partialTranscript={partialTranscript}
          errorMessage={errorMessage}
          isListening={isListening}
          appState={appState}
          onToggleMic={toggleMic}
        />

      </main>

      <SystemStatus/>

    </div>
  );
}