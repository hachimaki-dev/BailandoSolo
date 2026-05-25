# Bailando Solo

**Tu música. Tus reglas. Tu disco duro.**

Bailando Solo es un descargador de playlists de alta fidelidad hecho para gente que todavía cree que *poseer* su música tiene más sentido que pagar 14 suscripciones para escuchar el mismo álbum comprimido a bitrate de sopa instantánea.

Busca, descarga y organiza música desde YouTube con una app de escritorio rápida, multiusuario y sin humo corporativo.
Porque sí, el streaming es cómodo… hasta que desaparece una canción, cambian la versión del álbum o te meten anuncios cada 12 segundos.

---

## ¿Qué hace?

* Descarga playlists completas.
* Convierte y organiza automáticamente.
* Soporta perfiles multiusuario.
* Guarda estadísticas y configuraciones localmente.
* Funciona en Linux, Windows y macOS.
* Usa `yt-dlp`, porque claramente los héroes usan capa.

Todo corre en tu máquina.
Nada de “sube tus datos a nuestra nube revolucionaria impulsada por IA blockchain web3 cuántica”.

---

# 📥 Instalación (Humanos Normales)

¿Solo quieres bajar música y seguir con tu vida?

1. Ve a **Releases** en GitHub.
2. Descarga el instalador:

   * `.exe` → Windows
   * `.AppImage` o `.deb` → Linux
3. Instala.
4. Disfruta de escuchar música sin rezarle a un algoritmo.

---

# 🛠️ Desarrollo

¿Quieres mirar las tripas del monstruo? Excelente.

Bailando Solo está construido con:

* Frontend: Electron + Vue 3 + Vite
* Backend: Python + Flask + `yt-dlp`

Porque mezclar tecnologías como un científico loco también es arte.

---

## Requisitos

* Node.js 18+
* Python 3.10+
* `pip`
* `ffmpeg` (opcional… pero en realidad no quieres vivir sin él)

---

# 🚀 Arranque Rápido

Abrir terminal. Ejecutar. Fingir que sabes DevOps.

```bash
chmod +x start.sh
./start.sh
```

El script:

* crea el entorno virtual,
* instala dependencias,
* levanta Flask,
* levanta Vite,
* abre Electron,
* y probablemente hace más trabajo que varios CTOs.

---

# 📦 Empaquetar Instaladores

¿Modificaste el proyecto y ahora quieres distribuir tu propia versión mutante? Perfecto. Así empieza el software libre.

## 1. Compilar Backend

```bash
chmod +x build_backend.sh
./build_backend.sh
```

Esto genera el binario Python en `dist/`.

---

## 2. Empaquetar Electron

```bash
pnpm run dist
```

Esto:

* compila Vue,
* une el backend,
* empaqueta Electron,
* y genera instaladores en `release/`.

---

## Nota para Windows™

Sí, para generar `.exe`, necesitas compilar desde Windows.
Porque el sufrimiento construye carácter.

---

# 🏴 Filosofía del Proyecto

Bailando Solo existe porque internet olvidó algo importante:

> Si comprar música no significa poseerla,
> entonces “alquilar acceso” no significa libertad.

La idea no es piratear artistas independientes ni hacer daño a músicos.
La idea es recuperar control sobre tu biblioteca musical, tus archivos y tu experiencia.

Descarga legalmente el contenido al que tengas derecho de acceso.
*Guiño guiño.*

---

# 🍴 Haz Fork. Rómpelo. Mejóralo.

Este proyecto no quiere ser una catedral.
Quiere ser un garaje lleno de cables, commits sospechosos y gente construyendo cosas interesantes.

Haz forks.
Cámbiale la UI.
Agrégale soporte para metadata absurda.
Conecta Last.fm.
Haz una versión cyberpunk.
Reescribe el backend en Rust porque claramente todos terminan haciendo eso.
O convierte el reproductor en un visualizador psicodélico alimentado por FFTs.

Si mejoras algo:

* abre un PR,
* comparte ideas,
* o simplemente roba código con estilo.

El software libre vive de gente curiosa y peligrosamente motivada.

---

# 📂 Privacidad

Todo se guarda localmente:

* Linux/macOS:
  `~/.bailandosolo`

* Windows:
  `C:\Users\TuUsuario\.bailandosolo`

Sin cuentas.
Sin trackers.
Sin analytics invasivos.
Sin “mejoramos tu experiencia” mientras venden tus hábitos musicales a un fondo de inversión.

---

# 📦 Créditos y Licencias

Bailando Solo se construye sobre los hombros de gigantes del software libre y de código abierto. Agradecemos y respetamos la propiedad intelectual de las siguientes herramientas:

*   **[yt-dlp](https://github.com/yt-dlp/yt-dlp)** (Licencia Unlicense) - Motor de línea de comandos para descargas de audio y video.
*   **[Electron](https://github.com/electron/electron)** (Licencia MIT) - Framework de escritorio multiplataforma.
*   **[Vue.js 3](https://github.com/vuejs/core)** (Licencia MIT) - Interfaz reactiva interactiva.
*   **[Vite](https://github.com/vitejs/vite)** (Licencia MIT) - Servidor de desarrollo y compilador de frontend.
*   **[Flask](https://github.com/pallets/flask)** (Licencia BSD-3-Clause) - Microservidor web local de Python.
*   **[qrcode](https://github.com/soldair/node-qrcode)** (Licencia MIT) - Generación de códigos QR para acceso móvil.

Apoya el desarrollo de software libre: si te gusta la app, considera dejarnos una estrellita ⭐ en el repositorio o una reseña en las Issues.

---

# ⚠️ Disclaimer Legal Súper Serio™

Bailando Solo es simplemente una herramienta.

Como un martillo.
O `ffmpeg`.
O una katana emocional para recuperar soberanía digital.

Úsalo responsablemente y respeta las leyes de tu país.

Nosotros jamás te diríamos que descargues compulsivamente discografías enteras a las 3 AM mientras miras la terminal como hacker de película.

Jamás.