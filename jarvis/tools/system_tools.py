"""
Herramientas del sistema para JARVIS: Shell, estadísticas de hardware y utilidades.
"""

import subprocess
import shutil
import datetime
import os
from .registry import tool

@tool
def get_current_time() -> str:
    """Devuelve la fecha y hora actual en formato local."""
    now = datetime.datetime.now()
    return f"Fecha y hora actual: {now.strftime('%A %d de %B de %Y, %H:%M:%S')}"

@tool
def get_system_stats() -> str:
    """Obtiene el estado de los recursos de la máquina: uso de CPU, memoria RAM y espacio en disco."""
    stats = []
    
    # Memoria RAM
    if os.path.exists("/proc/meminfo"):
        mem = {}
        with open("/proc/meminfo") as f:
            for line in f:
                parts = line.split(":")
                if len(parts) == 2:
                    mem[parts[0].strip()] = int(parts[1].split()[0])
        total_ram = mem.get("MemTotal", 0) / 1024
        free_ram = mem.get("MemAvailable", mem.get("MemFree", 0)) / 1024
        used_ram = total_ram - free_ram
        stats.append(f"RAM: {used_ram:.1f} MB en uso / {total_ram:.1f} MB total ({used_ram/total_ram*100:.1f}%)")

    # Disco
    usage = shutil.disk_usage("/")
    stats.append(f"Disco (/): {usage.used // (2**30)} GB usados de {usage.total // (2**30)} GB ({usage.used/usage.total*100:.1f}%)")

    return "\n".join(stats)

@tool
def run_shell_command(command: str) -> str:
    """Ejecuta un comando en la terminal bash de Linux y devuelve la salida estándar y de error."""
    try:
        proc = subprocess.run(
            command,
            shell=True,
            capture_output=True,
            text=True,
            timeout=30
        )
        output = proc.stdout.strip()
        if proc.stderr:
            output += f"\n[stderr]: {proc.stderr.strip()}"
        return output if output else f"Comando ejecutado con código de salida: {proc.returncode}"
    except subprocess.TimeoutExpired:
        return "Error: El comando superó el tiempo límite de ejecución (30s)."
    except Exception as e:
        return f"Error ejecutando comando: {str(e)}"
