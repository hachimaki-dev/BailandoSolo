# Changelog — Bailando Solo

Todos los cambios notables del proyecto se documentan aquí.
Formato basado en [Keep a Changelog](https://keepachangelog.com/es-ES/1.1.0/).

---

## [1.1.0] — 2026-09-02

### Novedades y Resiliencia de Red
- **La Plaza P2P (Nostr)**:
  - Red comunitaria descentralizada sin servidor central para compartir y descubrir playlists de YouTube con metadatos completos.
  - Ribbon social en vivo *"EN SINTONÍA"* con presencia en tiempo real y visualizador de lo que escucha cada usuario.
  - Modo lista densa con acordeón de pistas desplegable y modo de fichas retro.
  - Cero listas ni usuarios hardcodeados: 100% impulsado por la comunidad.
- **Smart Fallback Search (Rescate Inteligente de Descargas)**:
  - Detección automática de enlaces caídos, videos eliminados o pistas geobloqueadas de YouTube Music (Topic).
  - Búsqueda en segundo plano de versiones alternativas disponibles en la región, descargando el audio de alta calidad con carátula y nombre original.
- **UX de Descargas en Tiempo Real**:
  - Eliminado el salto brusco de 0% a 100%. Progreso continuo y ascendente con sondeo reactivo a 350ms.
  - Barra de progreso general para descargas en lote (`PROGRESO GENERAL: X/Y`).
  - Indicadores de fase en vivo: *Iniciando*, *Buscando alternativa*, *Descargando audio (KB/s)*, *Extrayendo MP3*.
- **Resiliencia de Red en Redes Universitarias (Eduroam / Campus)**:
  - Bypass de cortafuegos con inspección SSL profunda (`nocheckcertificate`).
  - Bypass de caídas de enrutamiento IPv6 forzando IPv4 (`source_address: 0.0.0.0`).
  - Solucionador de desafíos JavaScript y firmas de YouTube integrado con Node.js (`ejs:github`).
  - Cabeceras emuladas de navegador y persistencia de cookies de sesión para saltar bloqueos 429 en IPs compartidas.

---

## [1.0.0] — 2026-09-02

### Lanzamiento Oficial
- **Arquitectura completa de producción**: Electron + Vue 3 + Flask + yt-dlp + PyInstaller.
- **Soporte Multi-plataforma**:
  - macOS Apple Silicon (M1 / M2 / M3 / M4) `.dmg` y `.zip`.
  - macOS Intel (x64) `.dmg` y `.zip`.
  - Windows (x64) instalador `.exe` (NSIS) y versión portable `.exe`.
  - Linux (x64) `.AppImage` y paquete Debian `.deb`.
- **Acceso Móvil PWA & Redes Restringidas**:
  - Interfaz web móvil responsive con soporte PWA y cache offline via Service Worker.
  - Generador de QR dinámico para conexión inmediata en red local (LAN).
  - Gestor de túneles cifrados (Cloudflare Tunnel / localtunnel) para saltar aislamiento AP y firewalls universitarios/públicos.
- **Descargas Resilientes de Música**:
  - Forzado IPv4, reintentos agresivos y fragmentación para evitar caídas en redes compartidas.
  - Detección de bloqueos de YouTube y soporte de sesión de navegador (`cookiesfrombrowser`).
- **Reproductor y Temas**:
  - Visualizador de audio reactivo, ecualizador por software, cola de reproducción y perfiles de usuario independientes.

---

### Agregado
- CI multi-plataforma: builds automáticos para macOS (ARM64 + Intel), Windows (installer + portable), Linux (AppImage + deb)
- GitHub Actions workflow (`release.yml`) con build matrix
- Iconos de packaging para todas las plataformas (`build/icons/`)

### Cambiado
- Configuración de `electron-builder` actualizada para soportar múltiples targets
- Proceso de release documentado

---

## [2.0.0] — 2025-12

### Agregado
- **Arquitectura completa**: Electron + Vue 3 + Flask + yt-dlp
- **Sistema de perfiles**: bibliotecas independientes por usuario (ver `docs/features/profiles.md`)
- **Reproductor de audio**: cola, shuffle, repeat, ecualizador, visualizador circular
- **6 temas visuales**: SNES, PS2, Wii U, Cassette, Nature, Karaoke
- **Modo Karaoke**: letras dinámicas con detección de beats en tiempo real
- **Interfaz móvil**: acceso por LAN con QR, HTML standalone, PWA (service worker)
- **Descargador**: análisis de playlists de YouTube, descarga con progreso
- **Biblioteca**: navegador de carpetas, búsqueda global, carátulas automáticas
- **Estadísticas**: tracking de reproducciones, logros, dashboard completo
- **Playlists**: creación, edición, gestión de playlists personalizadas
- **Menú contextual**: acciones por canción (agregar a playlist, editar metadata, etc.)
- **Editor de metadata**: edición de título, artista, etc.

### Corregido
- Carátulas no se mostraban correctamente (rutas sin prefijo del servidor)
- Carátulas random no se cargaban (módulo incorrecto: 7 → 9)
- Reproducción de audio: manejo correcto de `song.url`, `song.path`, `song.filename`
- Endpoint `/api/library/random`: rutas incorrectas para carpetas anidadas (ahora usa `os.path.relpath`)
- Problemas de CORS con streaming de audio
- Audio silencioso en build de producción (carga desde Flask en mismo origen)

---

## [Pre-release] — 2025-11

### Hitos
- `beta` — Primer prototipo funcional con UI standalone (`index.html`)
- `bailandosolo/alpha` — Exploración inicial de la arquitectura
- Reworking de la arquitectura a Flask Blueprints + Vue 3 + Vite
