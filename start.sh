#!/bin/bash

# Colores
GREEN='\033[0;32m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

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

# 4. Iniciar servidor
echo -e "${GREEN}🎵 Servidor listo!${NC}"
echo -e "${GREEN}👉 Abre index.html en tu navegador para empezar.${NC}"
python3 server.py
