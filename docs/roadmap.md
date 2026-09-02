# Roadmap — Bailando Solo

Backlog de features y deuda técnica. Consolidado desde la documentación existente y el análisis del código.

> **Para agentes IA:** Consulta este archivo antes de proponer features nuevas — muchas ya están planificadas.

---

## 🔴 Deuda Técnica (Prioridad Alta)

- [ ] **Tests automatizados** — 0% de cobertura actual
  - [ ] pytest para backend (`server/routes/`)
  - [ ] vitest para frontend (`ui/src/components/`, `ui/src/services/`)
  - [ ] Tests E2E básicos
- [ ] **Linting y formateo**
  - [ ] Configurar ESLint + Prettier para frontend
  - [ ] Configurar Ruff o Flake8 para backend
  - [ ] Pre-commit hooks
- [ ] **Eliminar `index.html` legacy** — 28KB standalone prototype en la raíz que ya no se usa
- [ ] **Descomponer `App.vue`** — 666 líneas, candidato a extraer lógica de audio a composables
- [ ] **Limpiar ramas remotas abandonadas** — `beta`, `bailandosolo/alpha`, `developer/2`, `fixing/cositas`, `feature/arquitectura_ia`
- [ ] **Corregir `origin/HEAD`** — apunta a `beta`, debería apuntar a `main`

---

## 🟡 Features Planificadas (Prioridad Media)

### Perfiles
- [ ] Exportar/Importar perfiles
- [ ] Estadísticas por perfil (actualmente compartidas)
- [ ] Temas personalizados por perfil
- [ ] Compartir perfiles entre dispositivos

### Biblioteca y Reproducción
- [ ] Mejoras en gestión de playlists (reordenar, duplicar)
- [ ] Edición de metadata en batch
- [ ] Soporte para más fuentes de audio (no solo YouTube)
- [ ] Modo offline mejorado

### Interfaz Móvil
- [ ] Sincronización de estado con la app desktop
- [ ] Controles de reproducción remota desde móvil
- [ ] PWA completa con cache de canciones

---

## 🔵 Features Experimentales (Prioridad Baja)

### Karaoke
- [ ] Modo pitch detection (mostrar notas musicales)
- [ ] Karaoke multijugador (sincronización entre dispositivos)
- [ ] Grabación de voz del usuario
- [ ] Puntuación de precisión vocal
- [ ] Exportar video del karaoke
- [ ] Efectos de voz en tiempo real (reverb, echo)
- [ ] Biblioteca de letras integrada con APIs externas (Genius, Musixmatch)
- [ ] Traducción automática de letras

### Audio Avanzado
- [ ] WebGPU audio processing (shader-based FFT) — ver `WebGPUAudioProcessor.js`
- [ ] Separación de voces del instrumental (TensorFlow.js)
- [ ] Análisis de sentimiento para colores dinámicos
- [ ] Detección de estructura de canciones (verso, coro, puente)

### Plataforma
- [ ] Integración con Last.fm (scrobbling)
- [ ] Integración con Discord Rich Presence
- [ ] Auto-actualización (electron-updater)
- [ ] Temas creados por la comunidad (marketplace)

---

## ✅ Completado

Ver [`docs/changelog.md`](changelog.md) para el historial completo de lo que ya se implementó.
