"""
JARVIS Assistant - Módulo de Reconocimiento de Voz (Speech-to-Text)
Usa faster-whisper en local con captura dinámica desde micrófono sin ruido de ALSA/JACK.
"""

import os
import sys
import time
import numpy as np
from faster_whisper import WhisperModel

class _SuppressStderr:
    """Suprime mensajes de depuración de bajo nivel de ALSA y JACK a nivel de descriptor C."""
    def __enter__(self):
        try:
            self.devnull = os.open(os.devnull, os.O_WRONLY)
            self.old_stderr = os.dup(2)
            sys.stderr.flush()
            os.dup2(self.devnull, 2)
            os.close(self.devnull)
        except Exception:
            self.old_stderr = None

    def __exit__(self, exc_type, exc_val, exc_tb):
        if self.old_stderr is not None:
            try:
                os.dup2(self.old_stderr, 2)
                os.close(self.old_stderr)
            except Exception:
                pass

class SpeechTranscriber:
    def __init__(self, model_size: str = "base", language: str = "es"):
        self.model_size = model_size
        self.language = language
        self._model = None
        self.sample_rate = 48000
        self.target_rate = 16000
        
        # Inicializar PyAudio de forma silenciosa una sola vez
        with _SuppressStderr():
            import pyaudio
            self._pyaudio_module = pyaudio
            self._pa = pyaudio.PyAudio()

    @property
    def model(self):
        if self._model is None:
            self._model = WhisperModel(self.model_size, device="cpu", compute_type="int8")
        return self._model

    def record_until_silence(self, silence_duration: float = 1.4, default_threshold: int = 700) -> str:
        """Graba audio desde el micrófono predeterminado hasta detectar pausa de voz."""
        chunk = 2048
        
        with _SuppressStderr():
            try:
                stream = self._pa.open(
                    format=self._pyaudio_module.paInt16,
                    channels=1,
                    rate=self.sample_rate,
                    input=True,
                    frames_per_buffer=chunk
                )
            except Exception:
                self.sample_rate = 16000
                stream = self._pa.open(
                    format=self._pyaudio_module.paInt16,
                    channels=1,
                    rate=self.sample_rate,
                    input=True,
                    frames_per_buffer=chunk
                )

        frames = []
        silence_start = None
        recording_started = False
        start_time = time.time()
        
        # Calibración rápida de ruido ambiental en 0.2 segundos
        ambient_energies = []
        for _ in range(5):
            try:
                data = stream.read(chunk, exception_on_overflow=False)
                audio_arr = np.frombuffer(data, dtype=np.int16)
                ambient_energies.append(np.abs(audio_arr).mean())
            except Exception:
                pass
        
        noise_floor = np.mean(ambient_energies) if ambient_energies else default_threshold
        threshold = max(default_threshold, noise_floor * 1.4)

        print("\r[🎤 JARVIS]: Escuchando...             ", end="", flush=True)

        try:
            while True:
                data = stream.read(chunk, exception_on_overflow=False)
                audio_data = np.frombuffer(data, dtype=np.int16)
                energy = np.abs(audio_data).mean()

                if energy > threshold:
                    if not recording_started:
                        recording_started = True
                        print("\r[🔴 Grabando tu voz... (habla)]        ", end="", flush=True)
                    silence_start = None
                    frames.append(audio_data)
                elif recording_started:
                    frames.append(audio_data)
                    if silence_start is None:
                        silence_start = time.time()
                    elif time.time() - silence_start >= silence_duration:
                        # Silencio detectado tras hablar
                        break

                # Timeout si nadie habla en 8 segundos
                if not recording_started and (time.time() - start_time > 8):
                    break
        finally:
            stream.stop_stream()
            stream.close()

        if not frames:
            return ""

        print("\r[🧠 Procesando lo que dijiste...]       ", end="", flush=True)

        # Preparar array para Whisper
        full_audio = np.concatenate(frames).astype(np.float32) / 32768.0

        if self.sample_rate != self.target_rate:
            indices = np.round(np.arange(0, len(full_audio), self.sample_rate / self.target_rate)).astype(int)
            indices = indices[indices < len(full_audio)]
            whisper_audio = full_audio[indices]
        else:
            whisper_audio = full_audio

        try:
            segments, _ = self.model.transcribe(
                whisper_audio,
                language=self.language,
                beam_size=3,
                vad_filter=True
            )
            text = " ".join([seg.text for seg in segments]).strip()
            print() # Salto de línea limpio
            return text
        except Exception as e:
            print(f"\n[!] Error al transcribir voz: {e}")
            return ""

speech_transcriber = SpeechTranscriber()
