#!/usr/bin/env bash
# ==============================================================================
# JARVIS Assistant - Script Lanzador Universal
# ==============================================================================

DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" >/dev/null 2>&1 && pwd )"
cd "$DIR"

# 1. Verificar si existe el archivo .env
if [ ! -f ".env" ]; then
    echo -e "\e[33m[!] No se encontró archivo .env. Creando uno a partir de .env.example...\e[0m"
    cp .env.example .env
    echo -e "\e[32m✔ Archivo .env creado. Puedes editarlo para configurar tu API Key o backend local.\e[0m\n"
fi

# 2. Verificar entorno virtual de Python
if [ ! -d "venv" ]; then
    echo -e "\e[34m[*] Creando entorno virtual de Python (venv)...\e[0m"
    python3 -m venv venv
    echo -e "\e[34m[*] Instalando dependencias necesarias...\e[0m"
    ./venv/bin/pip install --upgrade pip
    ./venv/bin/pip install -r requirements.txt
    echo -e "\e[32m✔ Entorno virtual listo.\e[0m\n"
fi

# 3. Ejecutar JARVIS pasando cualquier argumento adicional (ej. --voice, --once)
exec ./venv/bin/python main.py "$@"
