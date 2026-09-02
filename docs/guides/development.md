# Guía de Desarrollo — Bailando Solo

## Requisitos

| Herramienta | Versión mínima | Propósito |
|---|---|---|
| Node.js | 18+ | Electron, Vite, frontend tooling |
| Python | 3.10+ | Backend Flask |
| pip | — | Dependencias Python |
| npm | 8+ | Package manager (NO pnpm) |
| ffmpeg | latest | Conversión de audio (recomendado) |

---

## Setup Inicial

### 1. Clonar e instalar

```bash
git clone https://github.com/hachimaki-dev/BailandoSolo.git
cd BailandoSolo

# Backend
python3 -m venv venv
source venv/bin/activate        # Linux/macOS
# .\venv\Scripts\Activate.ps1   # Windows PowerShell
pip install -r requirements.txt

# Frontend
npm install
npm --prefix ui install
```

### 2. Iniciar en modo desarrollo

**Opción A: Script todo-en-uno**
```bash
chmod +x start.sh
./start.sh
```

**Opción B: Manual (recomendado para desarrollo)**
```bash
# Terminal 1 — Backend Python
source venv/bin/activate
python3 server.py
# → Flask corriendo en http://localhost:5001

# Terminal 2 — Frontend + Electron
npm run dev
# → Vite en http://localhost:5173 (proxied to Flask)
# → Electron abre automáticamente
```

### 3. Solo frontend (sin Electron)

```bash
cd ui
npm run dev
# Abrir http://localhost:5173 en el navegador
```

---

## Arquitectura de Desarrollo

```
Browser/Electron
    ↓ http://localhost:5173
Vite Dev Server (HMR)
    ↓ proxy /api/* → localhost:5001
Flask Backend
    ↓ filesystem
downloads/ (música)
profiles.json, stats.json
```

El proxy está configurado en [`ui/vite.config.js`](../ui/vite.config.js):
```javascript
proxy: {
  '/api': { target: 'http://localhost:5001' },
  '/stream': { target: 'http://localhost:5001' },
  '/mobile': { target: 'http://localhost:5001' }
}
```

---

## Flujo de Trabajo Git

### Crear una feature nueva

```bash
git checkout develop
git pull origin develop
git checkout -b feature/mi-feature

# ... trabajar ...

git add .
git commit -m "feat(scope): descripción"
git push origin feature/mi-feature

# Abrir PR a develop en GitHub
```

### Hacer un release

```bash
# 1. Merge develop → main
git checkout main
git merge develop

# 2. Actualizar versión
# Editar package.json: "version": "X.Y.Z"
# Actualizar docs/changelog.md

# 3. Tag y push
git tag vX.Y.Z
git push origin main --tags

# 4. CI genera los instaladores automáticamente
```

---

## Empaquetar para distribución

### Backend (binario Python)

```bash
chmod +x build_backend.sh
./build_backend.sh
# Genera: dist/bailandosolo-server
```

### Electron (instaladores)

```bash
# Requiere que el backend ya esté compilado en dist/
npm run dist          # Plataforma actual
npm run dist:mac      # macOS (dmg + zip)
npm run dist:win      # Windows (nsis + portable)
npm run dist:linux    # Linux (AppImage + deb)
```

Los instaladores se generan en `release/`.

---

## Estructura de URLs de la API

Base: `http://localhost:5001`

| Grupo | Patrón | Archivo |
|---|---|---|
| Perfiles | `/api/profiles/*` | `server/routes/profiles.py` |
| Descargas | `/api/analyze`, `/api/download`, `/api/status` | `server/routes/downloads.py` |
| Biblioteca | `/api/library/*`, `/api/stream/*` | `server/routes/library.py` |
| Playlists | `/api/playlists/*` | `server/routes/playlists.py` |
| Estadísticas | `/api/stats/*` | `server/routes/stats.py` |
| Móvil | `/api/mobile/*`, `/mobile`, `/test-mobile` | `server/routes/mobile.py` |

Referencia completa de endpoints en [`docs/architecture.md`](architecture.md#api-reference).

---

## Datos locales

Todo se almacena en la máquina del usuario:

| Dato | Ubicación |
|---|---|
| Música descargada | `downloads/<perfil>/<carpeta>/` |
| Configuración de perfiles | `profiles.json` (raíz del proyecto en dev, `~/.bailandosolo` en producción) |
| Estadísticas | `stats.json` |
| Playlists | Gestionadas vía API, almacenadas en filesystem |

---

## Troubleshooting

### El audio no reproduce
1. ¿Flask está corriendo? → `lsof -i :5001`
2. ¿Hay canciones en `downloads/`? → `ls downloads/*/`
3. ¿CORS está habilitado? → Verificar `flask_cors` en `server/__init__.py`

### Vite no conecta con Flask
1. ¿Flask corre en puerto 5001? → Verificar `server/config.py`
2. ¿El proxy de Vite está bien? → Verificar `ui/vite.config.js`

### Electron no abre
1. ¿Vite está corriendo? → `npm run dev` espera a que Vite esté listo en puerto 5173
2. ¿Las DevTools muestran errores? → Revisar la consola de Electron

### El acceso móvil no funciona
Ver guía completa en [`docs/features/mobile-access.md`](features/mobile-access.md).
