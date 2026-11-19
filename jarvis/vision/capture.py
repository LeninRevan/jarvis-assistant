"""
JARVIS Assistant - Módulo de Visión por Computadora
Captura fotogramas de alta resolución desde la webcam o captura de pantalla.
"""

import os
import base64
import subprocess
from typing import Optional

class VisionManager:
    def __init__(self, device: str = "/dev/video0", width: int = 1920, height: int = 1080):
        self.device = device
        self.width = width
        self.height = height

    def capture_webcam(self, skip_frames: int = 3) -> Optional[bytes]:
        """Captura un fotograma nítido de la cámara web usando ffmpeg."""
        tmp_output = "/tmp/jarvis_webcam_frame.jpg"
        
        # Intentar captura estabilizada
        cmd = [
            "ffmpeg", "-y",
            "-f", "v4l2",
            "-input_format", "mjpeg",
            "-video_size", f"{self.width}x{self.height}",
            "-i", self.device,
            "-vf", f"select=gte(n\\,{skip_frames})",
            "-frames:v", "1",
            "-q:v", "2",
            tmp_output
        ]
        
        try:
            subprocess.run(cmd, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, timeout=5)
            if os.path.exists(tmp_output) and os.path.getsize(tmp_output) > 0:
                with open(tmp_output, "rb") as f:
                    return f.read()
        except Exception:
            pass

        # Fallback sin filtro select
        cmd_fallback = [
            "ffmpeg", "-y",
            "-f", "v4l2",
            "-input_format", "mjpeg",
            "-video_size", f"{self.width}x{self.height}",
            "-i", self.device,
            "-frames:v", "1",
            "-q:v", "3",
            tmp_output
        ]
        try:
            subprocess.run(cmd_fallback, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, timeout=5)
            if os.path.exists(tmp_output) and os.path.getsize(tmp_output) > 0:
                with open(tmp_output, "rb") as f:
                    return f.read()
        except Exception as e:
            print(f"[!] Error capturando cámara: {e}")

        return None

    def capture_screen(self) -> Optional[bytes]:
        """Toma una captura de la pantalla actual (display X11)."""
        tmp_output = "/tmp/jarvis_screen_frame.jpg"
        display = os.getenv("DISPLAY", ":0")
        cmd = [
            "ffmpeg", "-y",
            "-f", "x11grab",
            "-i", display,
            "-frames:v", "1",
            "-q:v", "2",
            tmp_output
        ]
        try:
            subprocess.run(cmd, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, timeout=5)
            if os.path.exists(tmp_output) and os.path.getsize(tmp_output) > 0:
                with open(tmp_output, "rb") as f:
                    return f.read()
        except Exception as e:
            print(f"[!] Error capturando pantalla: {e}")
        return None

    @staticmethod
    def to_base64_url(image_bytes: bytes, mime_type: str = "image/jpeg") -> str:
        """Convierte los bytes de una imagen en Data URL en base64 para APIs de visión."""
        b64 = base64.b64encode(image_bytes).decode("utf-8")
        return f"data:{mime_type};base64,{b64}"

vision_manager = VisionManager()
