<template>
  <transition name="karaoke-overlay">
    <div v-if="isActive" class="karaoke-overlay">
      <!-- Visualizador de espectro de fondo -->
      <canvas ref="spectrumCanvas" class="spectrum-bg"></canvas>
      
      <!-- Contenedor de letras -->
      <div class="lyrics-container">
        <transition-group name="lyrics-slide" tag="div" class="lyrics-wrapper">
          <!-- Línea anterior (más pequeña, desvanecida) -->
          <div v-if="previousLine" key="prev" class="lyric-line lyric-previous">
            <span v-for="(word, idx) in previousLine.words" :key="`prev-${idx}`" class="lyric-word">
              {{ word }}
            </span>
          </div>
          
          <!-- Línea actual (gigante, animada) -->
          <div v-if="currentLine" key="current" class="lyric-line lyric-current">
            <span 
              v-for="(word, idx) in currentLine.words" 
              :key="`current-${idx}`"
              class="lyric-word"
              :class="{ 'word-active': idx === activeWordIndex }"
              :style="getWordStyle(idx)"
            >
              {{ word }}
            </span>
          </div>
          
          <!-- Línea siguiente (pequeña, preview) -->
          <div v-if="nextLine" key="next" class="lyric-line lyric-next">
            <span v-for="(word, idx) in nextLine.words" :key="`next-${idx}`" class="lyric-word">
              {{ word }}
            </span>
          </div>
        </transition-group>
      </div>

      <!-- Indicador de beat/pulso -->
      <div class="beat-indicator" :class="{ pulse: beatPulse }"></div>

      <!-- Barra de progreso circular -->
      <svg class="progress-ring" width="200" height="200">
        <circle
          class="progress-ring-circle"
          :stroke-dasharray="circumference"
          :stroke-dashoffset="progressOffset"
          cx="100"
          cy="100"
          r="90"
        />
      </svg>
    </div>
  </transition>
</template>

<script setup>
import { ref, computed, watch, onMounted, onUnmounted } from 'vue'
import { lyricsService, sampleLyrics } from '../services/LyricsTranscriptionService.js'

const props = defineProps({
  isPlaying: Boolean,
  currentSong: Object,
  currentTime: Number,
  duration: Number,
  analyser: Object // Changed from audioElement to analyser
})

const emit = defineEmits(['toggle-karaoke'])

const isActive = ref(true)
const spectrumCanvas = ref(null)
const beatPulse = ref(false)

// Lyrics state
const currentLine = ref(null)
const previousLine = ref(null)
const nextLine = ref(null)
const activeWordIndex = ref(0)

let animationId = null
let beatCheckInterval = null

// Progress ring calculation
const circumference = 2 * Math.PI * 90
const progressOffset = computed(() => {
  if (!props.duration) return circumference
  const progress = props.currentTime / props.duration
  return circumference - (progress * circumference)
})

// Parse line into words
const parseLine = (text) => {
  return {
    text,
    words: text.split(' ')
  }
}

// Update lyrics based on current time
watch(() => props.currentTime, (time) => {
  if (!time) return
  
  const lyricData = lyricsService.getCurrentLyric(time)
  
  if (lyricData && lyricData.current) {
    currentLine.value = parseLine(lyricData.current.text)
    previousLine.value = lyricData.previous ? parseLine(lyricData.previous.text) : null
    nextLine.value = lyricData.next ? parseLine(lyricData.next.text) : null
    
    // Calculate word progression based on line progress
    activeWordIndex.value = Math.floor(lyricData.progress * currentLine.value.words.length)
  }
})

// Dynamic word styling based on beat
const getWordStyle = (idx) => {
  const isActive = idx === activeWordIndex.value
  const delay = idx * 0.1
  
  return {
    animationDelay: `${delay}s`,
    transform: isActive ? 'scale(1.2)' : 'scale(1)',
    color: isActive ? 'var(--karaoke-active)' : 'var(--karaoke-text)'
  }
}

// Beat detection loop
const checkBeat = () => {
  const beat = lyricsService.detectBeat()
  
  if (beat.isBeat) {
    beatPulse.value = true
    setTimeout(() => beatPulse.value = false, 150)
  }
}

// Spectrum visualization
const drawSpectrum = () => {
  if (!spectrumCanvas.value) return
  
  const canvas = spectrumCanvas.value
  const ctx = canvas.getContext('2d')
  const width = canvas.width = window.innerWidth
  const height = canvas.height = window.innerHeight
  
  const dataArray = lyricsService.getSpectrumData()
  
  if (dataArray.length === 0) {
    animationId = requestAnimationFrame(drawSpectrum)
    return
  }
  
  ctx.clearRect(0, 0, width, height)
  
  const barWidth = width / dataArray.length * 2.5
  let x = 0
  
  for (let i = 0; i < dataArray.length; i++) {
    const barHeight = (dataArray[i] / 255) * height * 0.5
    
    // Color dinámico basado en frecuencia
    const hue = (i / dataArray.length) * 360
    const opacity = 0.3 + (dataArray[i] / 255) * 0.7
    
    ctx.fillStyle = `hsla(${hue}, 80%, 60%, ${opacity})`
    ctx.fillRect(x, height - barHeight, barWidth, barHeight)
    
    x += barWidth + 2
  }
  
  animationId = requestAnimationFrame(drawSpectrum)
}

// Initialize audio analysis
const initAudioAnalysis = async () => {
  if (!props.analyser) return
  
  const initialized = await lyricsService.initialize(props.analyser)
  
  if (initialized) {
    // Cargar letras de ejemplo (en producción, vendrían de una API o archivo)
    lyricsService.loadLyrics(sampleLyrics, 'json')
    
    // Iniciar visualización de espectro
    drawSpectrum()
    
    // Iniciar detección de beats
    beatCheckInterval = setInterval(checkBeat, 50)
  }
}

// Cleanup
const cleanup = () => {
  if (animationId) {
    cancelAnimationFrame(animationId)
    animationId = null
  }
  if (beatCheckInterval) {
    clearInterval(beatCheckInterval)
    beatCheckInterval = null
  }
}

onMounted(() => {
  if (props.analyser) {
    initAudioAnalysis()
  }
})

onUnmounted(() => {
  cleanup()
})

watch(() => props.analyser, (newAnalyser) => {
  if (newAnalyser) {
    cleanup()
    initAudioAnalysis()
  }
})

// Cleanup cuando el tema cambia
watch(() => isActive.value, (active) => {
  if (!active) {
    cleanup()
  }
})
</script>

<style scoped>
.karaoke-overlay {
  position: fixed;
  top: 0;
  left: 0;
  width: 100vw;
  height: 100vh;
  z-index: 9999;
  background: linear-gradient(135deg, 
    rgba(0, 0, 0, 0.85) 0%, 
    rgba(20, 0, 40, 0.9) 50%, 
    rgba(0, 0, 0, 0.85) 100%
  );
  backdrop-filter: blur(20px);
  display: flex;
  align-items: center;
  justify-content: center;
  overflow: hidden;
}

.spectrum-bg {
  position: absolute;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  opacity: 0.4;
  filter: blur(2px);
}

.lyrics-container {
  position: relative;
  z-index: 2;
  width: 90%;
  max-width: 1400px;
  text-align: center;
  perspective: 1000px;
}

.lyrics-wrapper {
  display: flex;
  flex-direction: column;
  gap: 40px;
  align-items: center;
}

.lyric-line {
  display: flex;
  flex-wrap: wrap;
  justify-content: center;
  gap: 20px;
  transition: all 0.6s cubic-bezier(0.68, -0.55, 0.265, 1.55);
}

.lyric-previous {
  opacity: 0.3;
  transform: translateY(-20px) scale(0.7);
  filter: blur(3px);
}

.lyric-current {
  font-size: clamp(3rem, 8vw, 10rem);
  font-weight: 900;
  text-transform: uppercase;
  letter-spacing: 0.05em;
  line-height: 1.2;
}

.lyric-next {
  opacity: 0.5;
  transform: translateY(20px) scale(0.8);
  filter: blur(2px);
  font-size: 2rem;
}

.lyric-word {
  display: inline-block;
  transition: all 0.3s cubic-bezier(0.175, 0.885, 0.32, 1.275);
  color: var(--karaoke-text, #ffffff);
  text-shadow: 
    0 0 20px rgba(255, 255, 255, 0.5),
    0 0 40px var(--karaoke-glow, rgba(138, 43, 226, 0.6)),
    0 4px 8px rgba(0, 0, 0, 0.5);
  animation: word-enter 0.5s ease-out forwards;
}

.lyric-word.word-active {
  color: var(--karaoke-active, #ff00ff);
  transform: scale(1.3) translateY(-10px);
  text-shadow: 
    0 0 30px var(--karaoke-active, #ff00ff),
    0 0 60px var(--karaoke-active, #ff00ff),
    0 0 90px var(--karaoke-active-glow, rgba(255, 0, 255, 0.8)),
    0 8px 16px rgba(0, 0, 0, 0.7);
  animation: word-pulse 0.4s ease-in-out infinite alternate;
}

@keyframes word-enter {
  from {
    opacity: 0;
    transform: translateY(30px) rotateX(-90deg);
  }
  to {
    opacity: 1;
    transform: translateY(0) rotateX(0);
  }
}

@keyframes word-pulse {
  from {
    filter: brightness(1);
  }
  to {
    filter: brightness(1.4);
  }
}

.beat-indicator {
  position: absolute;
  bottom: 100px;
  left: 50%;
  transform: translateX(-50%);
  width: 40px;
  height: 40px;
  border-radius: 50%;
  background: var(--karaoke-beat, rgba(255, 255, 255, 0.3));
  transition: all 0.1s ease-out;
}

.beat-indicator.pulse {
  transform: translateX(-50%) scale(2);
  background: var(--karaoke-beat-active, rgba(255, 0, 255, 0.8));
  box-shadow: 0 0 40px var(--karaoke-beat-active, rgba(255, 0, 255, 1));
}

.progress-ring {
  position: absolute;
  bottom: 50px;
  right: 50px;
  transform: rotate(-90deg);
}

.progress-ring-circle {
  fill: none;
  stroke: var(--karaoke-progress, #ff00ff);
  stroke-width: 8;
  stroke-linecap: round;
  filter: drop-shadow(0 0 10px var(--karaoke-progress, #ff00ff));
  transition: stroke-dashoffset 0.3s ease;
}

/* Transitions */
.lyrics-slide-enter-active,
.lyrics-slide-leave-active {
  transition: all 0.8s cubic-bezier(0.68, -0.55, 0.265, 1.55);
}

.lyrics-slide-enter-from {
  opacity: 0;
  transform: translateY(100px) scale(0.5) rotateX(90deg);
}

.lyrics-slide-leave-to {
  opacity: 0;
  transform: translateY(-100px) scale(0.5) rotateX(-90deg);
}

.karaoke-overlay-enter-active,
.karaoke-overlay-leave-active {
  transition: all 0.6s ease;
}

.karaoke-overlay-enter-from,
.karaoke-overlay-leave-to {
  opacity: 0;
  transform: scale(1.2);
}

/* Responsive */
@media (max-width: 768px) {
  .lyric-current {
    font-size: clamp(2rem, 12vw, 6rem);
  }
  
  .lyric-next {
    font-size: 1.5rem;
  }
  
  .lyrics-wrapper {
    gap: 20px;
  }
}
</style>
