"""
JARVIS Assistant - Módulo de Síntesis de Voz (Text-to-Speech)
Usa edge-tts con voces neuronales en español (sin costo de API) y reproducción fluida.
"""

import asyncio
import os
import subprocess
import edge_tts

class VoiceSynthesizer:
    def __init__(self, voice: str = "es-MX-DaliaNeural", rate: str = "+0%"):
        self.voice = voice
        self.rate = rate

    async def _generate_audio_async(self, text: str, output_path: str):
        communicate = edge_tts.Communicate(text, self.voice, rate=self.rate)
        await communicate.save(output_path)

    def speak(self, text: str):
        """Sintetiza y reproduce el texto en los altavoces o audífonos del usuario."""
        if not text or not text.strip():
            return

        tmp_mp3 = "/tmp/jarvis_speech.mp3"
        try:
            # Generar audio con edge-tts
            asyncio.run(self._generate_audio_async(text, tmp_mp3))
            
            # Reproducir con mpv o ffplay o paplay
            players = [
                ["mpv", "--no-video", "--really-quiet", tmp_mp3],
                ["ffplay", "-nodisp", "-autoexit", "-loglevel", "quiet", tmp_mp3],
            ]
            
            played = False
            for p in players:
                try:
                    res = subprocess.run(p, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, timeout=40)
                    if res.returncode == 0:
                        played = True
                        break
                except FileNotFoundError:
                    continue
                except Exception:
                    pass

            if not played:
                print(f"[!] No se encontró reproductor de audio compatible para {tmp_mp3}")
        except Exception as e:
            print(f"[!] Error en síntesis de voz: {e}")

voice_synthesizer = VoiceSynthesizer()
