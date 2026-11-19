"""
JARVIS Assistant - Módulo de Reconocimiento de Voz (Speech-to-Text)
Usa faster-whisper en local con captura dinámica desde micrófono (ALSA/Pulse/PipeWire).
"""

import time
import pyaudio
import numpy as np
from faster_whisper import WhisperModel

class SpeechTranscriber:
    def __init__(self, model_size: str = "base", language: str = "es"):
        self.model_size = model_size
        self.language = language
        self._model = None
        self.sample_rate = 48000  # Nativo para la mayoría de codecs Realtek/USB
        self.target_rate = 16000  # Requerido por Whisper

    @property
    def model(self):
        if self._model is None:
            # Carga perezosa del modelo en CPU con cuantización int8 para máxima velocidad
            self._model = WhisperModel(self.model_size, device="cpu", compute_type="int8")
        return self._model

    def record_until_silence(self, silence_duration: float = 1.6, energy_threshold: int = 1500) -> str:
        """Graba audio desde el micrófono predeterminado hasta que detecta una pausa de silencio prolongada."""
        p = pyaudio.PyAudio()
        chunk = 2048
        
        try:
            stream = p.open(
                format=pyaudio.paInt16,
                channels=1,
                rate=self.sample_rate,
                input=True,
                frames_per_buffer=chunk
            )
        except Exception:
            # Reintentar a 16000 Hz si la tarjeta no acepta 48000 Hz
            self.sample_rate = 16000
            stream = p.open(
                format=pyaudio.paInt16,
                channels=1,
                rate=self.sample_rate,
                input=True,
                frames_per_buffer=chunk
            )

        frames = []
        silence_start = None
        recording_started = False
        start_time = time.time()

        print("\n[🎤 JARVIS]: Escuchando...")

        try:
            while True:
                data = stream.read(chunk, exception_on_overflow=False)
                audio_data = np.frombuffer(data, dtype=np.int16)
                energy = np.abs(audio_data).mean()

                # Detectar inicio de voz
                if energy > energy_threshold:
                    if not recording_started:
                        recording_started = True
                    silence_start = None
                    frames.append(audio_data)
                elif recording_started:
                    frames.append(audio_data)
                    if silence_start is None:
                        silence_start = time.time()
                    elif time.time() - silence_start >= silence_duration:
                        # Pausa de silencio detectada tras hablar
                        break

                # Tiempo de espera máximo sin hablar (timeout de 10 segundos)
                if not recording_started and (time.time() - start_time > 10):
                    break
        finally:
            stream.stop_stream()
            stream.close()
            p.terminate()

        if not frames:
            return ""

        # Concatenar audio
        full_audio = np.concatenate(frames).astype(np.float32) / 32768.0

        # Resamplear si es necesario
        if self.sample_rate != self.target_rate:
            indices = np.round(np.arange(0, len(full_audio), self.sample_rate / self.target_rate)).astype(int)
            indices = indices[indices < len(full_audio)]
            whisper_audio = full_audio[indices]
        else:
            whisper_audio = full_audio

        # Transcripción con Faster Whisper
        try:
            segments, _ = self.model.transcribe(
                whisper_audio,
                language=self.language,
                beam_size=3,
                vad_filter=True
            )
            text = " ".join([seg.text for seg in segments]).strip()
            return text
        except Exception as e:
            print(f"[!] Error al transcribir voz: {e}")
            return ""

speech_transcriber = SpeechTranscriber()
