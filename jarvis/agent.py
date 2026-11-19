"""
JARVIS Assistant - Orquestador Central del Asistente (Agent Loop)
Integra Percepción Visual, Razón (LLM), Ejecución de Acciones (Tool Calling) y Síntesis de Voz.
"""

from typing import List, Dict, Any, Optional
from rich.console import Console
from rich.panel import Panel

from config import JarvisConfig
from .backends import get_llm_client, BaseLLMClient
from .tools import tools
from .vision import vision_manager
from .audio import voice_synthesizer, speech_transcriber

console = Console()

class JarvisAgent:
    def __init__(self, config: JarvisConfig):
        self.config = config
        self.client: BaseLLMClient = get_llm_client(
            provider=config.provider,
            api_key=config.api_key,
            base_url=config.base_url,
            model=config.model,
            temperature=config.temperature
        )
        self.history: List[Dict[str, Any]] = [
            {"role": "system", "content": config.system_prompt}
        ]

    def ask(self, user_input: str, include_camera: bool = False, include_screen: bool = False) -> str:
        """Ciclo completo de Percepción -> Razonamiento -> Tool Calling -> Respuesta -> Voz."""
        console.print(f"[bold cyan]👤 Usuario:[/bold cyan] {user_input}")

        # 1. Percepción visual si fue solicitada
        image_bytes: Optional[bytes] = None
        if include_camera:
            console.print("[dim]📸 Capturando imagen desde cámara web...[/dim]")
            image_bytes = vision_manager.capture_webcam()
            if image_bytes:
                console.print("[green]✔ Imagen de cámara capturada (1080p).[/green]")
        elif include_screen:
            console.print("[dim]🖥 Tomando captura de pantalla...[/dim]")
            image_bytes = vision_manager.capture_screen()
            if image_bytes:
                console.print("[green]✔ Captura de pantalla obtenida.[/green]")

        # 2. Registrar turno de usuario en el historial
        self.history.append({"role": "user", "content": user_input})

        # 3. Ciclo de razonamiento y ejecución de herramientas (Tool Calling Loop)
        max_tool_iterations = 5
        iteration = 0
        final_answer = ""

        tool_schemas = tools.get_schemas() if self.config.enable_tools else None

        while iteration < max_tool_iterations:
            iteration += 1
            
            with console.status("[bold yellow]🧠 Jarvis razonando...", spinner="dots"):
                response = self.client.generate(
                    messages=self.history,
                    tools=tool_schemas,
                    image_bytes=image_bytes if iteration == 1 else None  # solo enviar imagen en el primer paso
                )

            # Si el modelo ejecutó herramientas
            if response.tool_calls:
                # Guardar respuesta del asistente que invoca herramientas
                self.history.append({
                    "role": "assistant",
                    "content": response.content or "",
                    "tool_calls": [
                        {
                            "id": tc.id,
                            "type": "function",
                            "function": {"name": tc.name, "arguments": str(tc.arguments)}
                        } for tc in response.tool_calls
                    ]
                })

                for tc in response.tool_calls:
                    console.print(Panel(
                        f"[bold yellow]Herramienta:[/bold yellow] [green]{tc.name}[/green]\n[bold]Argumentos:[/bold] {tc.arguments}",
                        title="⚙ Invocación de Herramienta",
                        border_style="yellow"
                    ))

                    # Ejecutar herramienta
                    result = tools.execute(tc.name, tc.arguments)
                    console.print(f"[dim]Resultado ({tc.name}): {str(result)[:200]}...[/dim]")

                    # Devolver resultado al modelo
                    self.history.append({
                        "role": "tool",
                        "tool_call_id": tc.id,
                        "name": tc.name,
                        "content": str(result)
                    })
                
                # Continuar el loop para que el modelo interprete el resultado de la herramienta
                continue

            # Respuesta final obtenida
            if response.content:
                final_answer = response.content
                self.history.append({"role": "assistant", "content": final_answer})
                break

        # 4. Mostrar respuesta en terminal
        console.print(Panel(
            final_answer,
            title="🤖 JARVIS",
            border_style="cyan"
        ))

        # 5. Respuesta por voz si TTS está habilitado
        if self.config.tts_enabled and final_answer:
            with console.status("[dim]🔊 Reproduciendo respuesta por voz...", spinner="aesthetic"):
                voice_synthesizer.speak(final_answer)

        return final_answer
