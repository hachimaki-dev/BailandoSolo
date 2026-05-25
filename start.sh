#!/bin/bash

# Colores
GREEN='\033[0;32m'
BLUE='\033[0;34m'
RED='\033[0;31m'
NC='\033[0m' # No Color

echo -e "${BLUE}🚀 Configurando entorno de desarrollo de Bailando Solo...${NC}"

# 1. Configurar Backend (Python)
echo -e "${BLUE}📦 Verificando entorno de Python...${NC}"
if [ ! -d "venv" ]; then
    python3 -m venv venv
    echo -e "${GREEN}✓ Entorno virtual creado.${NC}"
fi

source venv/bin/activate
pip install -r requirements.txt > /dev/null
echo -e "${GREEN}✓ Dependencias de Python instaladas.${NC}"

# 2. Configurar Frontend (Node/Electron)
echo -e "${BLUE}📦 Verificando dependencias de Node.js...${NC}"
if [ ! -d "node_modules" ]; then
    pnpm install
fi

if [ ! -d "ui/node_modules" ]; then
    pnpm --dir ui install
fi
echo -e "${GREEN}✓ Dependencias de Node instaladas.${NC}"

# 3. Iniciar entorno de desarrollo
echo -e "${GREEN}🎵 Iniciando la aplicación (Electron + Flask)...${NC}"
pnpm run dev
