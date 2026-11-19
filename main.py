"""
JARVIS Assistant - Punto de Entrada Principal
Ejecuta el asistente en modo Voz Continua, Modo Terminal Interactivo o Consulta Rápida.
"""

import sys
import argparse
from rich.console import Console
from rich.panel import Panel
from rich.table import Table

from config import config
from jarvis.agent import JarvisAgent
from jarvis.audio import speech_transcriber
from jarvis.tools import tools

console = Console()

def print_banner():
    banner = """
    ╔═══════════════════════════════════════════════════════════╗
    ║                     J.A.R.V.I.S.                          ║
    ║      Asistente Autónomo Multimodal & Tool Calling         ║
    ╚═══════════════════════════════════════════════════════════╝
    """
    console.print(f"[bold cyan]{banner}[/bold cyan]")

    table = Table(title="Configuración de Sistema", border_style="dim")
    table.add_column("Componente", style="bold green")
    table.add_column("Detalle", style="cyan")

    table.add_row("Proveedor LLM", f"{config.provider.upper()} ({config.model})")
    table.add_row("Entrada de Voz (STT)", f"Faster-Whisper ({config.stt_model_size}) [{config.stt_language}]")
    table.add_row("Salida de Voz (TTS)", f"Edge-TTS ({config.tts_voice})")
    table.add_row("Cámara Web", f"{config.camera_device} ({config.camera_width}x{config.camera_height})")
    table.add_row("Herramientas Activas", f"{len(tools.get_schemas())} registradas")

    console.print(table)
    console.print()

def run_voice_loop(agent: JarvisAgent):
    console.print("[bold yellow]Iniciando Modo de Voz Continua.[/bold yellow]")
    console.print("[dim]Habla a través de tu micrófono. Di 'salir' o presiona Ctrl+C para terminar.[/dim]\n")

    while True:
        try:
            # Escucha hasta que se detecte una pausa de silencio
            text = speech_transcriber.record_until_silence()
            if not text or not text.strip():
                continue

            if text.lower().strip() in ("salir", "terminar", "apagar", "adiós", "adios"):
                console.print("[bold red]Apagando JARVIS... Hasta pronto.[/bold red]")
                break

            # Determinar si la consulta requiere visión
            requires_camera = any(w in text.lower() for w in ("mira", "ves", "viendo", "cámara", "camara", "foto", "entorno", "escritorio", "mesa", "cable"))
            
            agent.ask(text, include_camera=requires_camera)

        except KeyboardInterrupt:
            console.print("\n[bold red]Interrupción por usuario. Hasta luego.[/bold red]")
            break
        except Exception as e:
            console.print(f"[bold red][!] Error en ciclo de voz: {e}[/bold red]")

def run_text_loop(agent: JarvisAgent):
    console.print("[bold yellow]Iniciando Modo Consola Interactiva.[/bold yellow]")
    console.print("[dim]Comandos especiales: /cam (adjunta foto de webcam), /screen (captura pantalla), exit (salir)[/dim]\n")

    while True:
        try:
            prompt = console.input("[bold green]Tú > [/bold green]").strip()
            if not prompt:
                continue
            if prompt.lower() in ("exit", "quit", "salir"):
                break

            include_cam = False
            include_scr = False

            if prompt.startswith("/cam"):
                include_cam = True
                prompt = prompt[4:].strip() or "¿Qué estás viendo a través de la cámara?"
            elif prompt.startswith("/screen"):
                include_scr = True
                prompt = prompt[7:].strip() or "Analiza lo que se ve en mi pantalla."

            agent.ask(prompt, include_camera=include_cam, include_screen=include_scr)

        except (KeyboardInterrupt, EOFError):
            console.print("\n[bold red]Saliendo...[/bold red]")
            break

def main():
    parser = argparse.ArgumentParser(description="JARVIS Autonomous Assistant")
    parser.add_argument("--voice", action="store_true", help="Iniciar en modo de escucha continua por voz")
    parser.add_argument("--once", type=str, help="Ejecutar una consulta directa y terminar")
    parser.add_argument("--cam", action="store_true", help="Adjuntar captura de cámara en consulta única")
    args = parser.parse_args()

    print_banner()
    agent = JarvisAgent(config)

    if args.once:
        agent.ask(args.once, include_camera=args.cam)
    elif args.voice:
        run_voice_loop(agent)
    else:
        run_text_loop(agent)

if __name__ == "__main__":
    main()
