#!/bin/bash

# Colores
GREEN='\033[0;32m'
BLUE='\033[0;34m'
RED='\033[0;31m'
NC='\033[0m' # No Color

PORT=${BAILANDO_PORT:-5001}

echo -e "${BLUE}🚀 Iniciando Bailando Solo...${NC}"

# 1. Crear entorno virtual si no existe
if [ ! -d "venv" ]; then
    echo -e "${BLUE}📦 Creando entorno virtual seguro (venv)...${NC}"
    python3 -m venv venv
fi

# 2. Activar entorno virtual
source venv/bin/activate

# 3. Instalar dependencias
echo -e "${BLUE}⬇️  Verificando dependencias...${NC}"
pip install -r requirements.txt

# 4. Check for port conflicts
if lsof -Pi :$PORT -sTCP:LISTEN -t >/dev/null 2>&1; then
    echo -e "${RED}⚠️  Puerto $PORT está ocupado. Liberando...${NC}"
    lsof -ti:$PORT | xargs kill -9 2>/dev/null
    sleep 1
fi

# 5. Iniciar servidor
echo -e "${GREEN}🎵 Servidor listo!${NC}"
echo -e "${GREEN}👉 Abre http://localhost:$PORT en tu navegador para empezar.${NC}"
python3 server.py
