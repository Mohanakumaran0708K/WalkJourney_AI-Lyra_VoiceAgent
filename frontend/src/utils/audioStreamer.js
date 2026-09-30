/**
 * Utility for capturing browser microphone audio, resampling to PCM16 16kHz mono,
 * and streaming binary audio chunks over WebSocket to AssemblyAI STT v3.
 */

export class AudioStreamer {
  constructor(wsUrl = 'ws://localhost:8000/api/v1/ws/voice') {
    this.wsUrl = wsUrl;
    this.ws = null;
    this.audioContext = null;
    this.mediaStream = null;
    this.processor = null;
    this.source = null;
    this.isStreaming = false;
  }

  async start(onEvent, onError) {
    if (this.isStreaming) return;

    try {
      // 1. Establish WebSocket connection to backend
      this.ws = new WebSocket(this.wsUrl);
      this.ws.binaryType = 'arraybuffer';

      await new Promise((resolve, reject) => {
        const timeout = setTimeout(() => reject(new Error("WebSocket connection timeout")), 5000);

        this.ws.onopen = () => {
          clearTimeout(timeout);
          resolve();
        };

        this.ws.onerror = (err) => {
          clearTimeout(timeout);
          reject(new Error("Failed to connect to Voice WebSocket on backend."));
        };
      });

      // Handle incoming STT events from backend
      this.ws.onmessage = (event) => {
        try {
          const data = JSON.parse(event.data);
          if (onEvent) onEvent(data);
        } catch (err) {
          console.warn("Failed to parse incoming WebSocket message:", err);
        }
      };

      this.ws.onclose = () => {
        this.stop();
      };

      // 2. Request microphone permission
      this.mediaStream = await navigator.mediaDevices.getUserMedia({
        audio: {
          channelCount: 1,
          echoCancellation: true,
          noiseSuppression: true
        }
      });

      // 3. Setup Web Audio API Context (target 16000 Hz)
      const AudioCtx = window.AudioContext || window.webkitAudioContext;
      this.audioContext = new AudioCtx({ sampleRate: 16000 });

      // Fallback sample rate ratio if browser forces hardware sample rate (e.g. 44100/48000 Hz)
      const inputSampleRate = this.audioContext.sampleRate;
      const targetSampleRate = 16000;

      this.source = this.audioContext.createMediaStreamSource(this.mediaStream);
      // ScriptProcessor bufferSize = 4096 (approx 85ms-250ms chunks)
      this.processor = this.audioContext.createScriptProcessor(4096, 1, 1);

      this.processor.onaudioprocess = (e) => {
        if (!this.ws || this.ws.readyState !== WebSocket.OPEN) return;

        const inputData = e.inputBuffer.getChannelData(0);
        let pcmData;

        if (inputSampleRate === targetSampleRate) {
          pcmData = this.floatTo16BitPCM(inputData);
        } else {
          // Resample to 16kHz if browser sample rate differs
          const resampled = this.resampleBuffer(inputData, inputSampleRate, targetSampleRate);
          pcmData = this.floatTo16BitPCM(resampled);
        }

        this.ws.send(pcmData);
      };

      this.source.connect(this.processor);
      this.processor.connect(this.audioContext.destination);
      this.isStreaming = true;

    } catch (err) {
      this.stop();
      if (onError) onError(err);
      throw err;
    }
  }

  floatTo16BitPCM(float32Array) {
    const buffer = new ArrayBuffer(float32Array.length * 2);
    const view = new DataView(buffer);
    let offset = 0;
    for (let i = 0; i < float32Array.length; i++, offset += 2) {
      const s = Math.max(-1, Math.min(1, float32Array[i]));
      view.setInt16(offset, s < 0 ? s * 0x8000 : s * 0x7FFF, true); // Little-endian
    }
    return buffer;
  }

  resampleBuffer(buffer, fromSampleRate, toSampleRate) {
    if (fromSampleRate === toSampleRate) return buffer;
    const ratio = fromSampleRate / toSampleRate;
    const newLength = Math.round(buffer.length / ratio);
    const result = new Float32Array(newLength);
    let offsetResult = 0;
    let offsetBuffer = 0;

    while (offsetResult < result.length) {
      const nextOffsetBuffer = Math.round((offsetResult + 1) * ratio);
      let accum = 0;
      let count = 0;
      for (let i = offsetBuffer; i < nextOffsetBuffer && i < buffer.length; i++) {
        accum += buffer[i];
        count++;
      }
      result[offsetResult] = count > 0 ? accum / count : 0;
      offsetResult++;
      offsetBuffer = nextOffsetBuffer;
    }
    return result;
  }

  stop() {
    if (!this.isStreaming && !this.ws) return;

    this.isStreaming = false;

    // Send termination message over WebSocket before closing
    if (this.ws && this.ws.readyState === WebSocket.OPEN) {
      try {
        this.ws.send("terminate");
        this.ws.close();
      } catch (err) {
        console.warn("Error terminating WebSocket:", err);
      }
    }
    this.ws = null;

    // Stop MediaStream tracks
    if (this.mediaStream) {
      this.mediaStream.getTracks().forEach((track) => track.stop());
      this.mediaStream = null;
    }

    // Disconnect Web Audio processor & close AudioContext
    if (this.processor) {
      try { this.processor.disconnect(); } catch (e) {}
      this.processor = null;
    }

    if (this.source) {
      try { this.source.disconnect(); } catch (e) {}
      this.source = null;
    }

    if (this.audioContext) {
      try { this.audioContext.close(); } catch (e) {}
      this.audioContext = null;
    }
  }
}
