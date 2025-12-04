<template>
  <canvas ref="canvas" class="bio-clock-canvas"></canvas>
</template>

<script setup>
import { ref, onMounted, onBeforeUnmount, watch } from 'vue'

const props = defineProps({
  isPlaying: Boolean,
  currentSongTime: Number, // In seconds
  songDuration: Number, // In seconds
})

const canvas = ref(null)
let ctx = null
let animationFrameId = null

// State
let timeOffset = 0
const textSpacing = 120 // Space between text
const fontSize = 24
const speed = 1 // Base speed

// Heartbeat
let pulse = 1

const getSystemTime = () => {
  const now = new Date()
  return now.toLocaleTimeString('en-US', { hour12: false })
}

const formatSongTime = (seconds) => {
  if (!seconds) return "00:00"
  const m = Math.floor(seconds / 60)
  const s = Math.floor(seconds % 60)
  return `${m.toString().padStart(2, '0')}:${s.toString().padStart(2, '0')}`
}

const getColor = (progress) => {
  // Progress 0 to 1
  // 0 - 0.25: Green (#00FF00) to YellowGreen (#ADFF2F)
  // 0.25 - 1.0: YellowGreen to Red (#FF0000)
  
  // Simple interpolation helper
  const lerp = (start, end, t) => start + (end - start) * t
  const hexToRgb = (hex) => {
    const bigint = parseInt(hex.slice(1), 16)
    return [(bigint >> 16) & 255, (bigint >> 8) & 255, bigint & 255]
  }
  const rgbToHex = (r, g, b) => `#${((1 << 24) + (r << 16) + (g << 8) + b).toString(16).slice(1)}`

  let startColor, endColor, t

  if (progress <= 0.25) {
    startColor = hexToRgb('#00FF00')
    endColor = hexToRgb('#ADFF2F')
    t = progress / 0.25
  } else {
    startColor = hexToRgb('#ADFF2F')
    endColor = hexToRgb('#FF0000')
    t = (progress - 0.25) / 0.75
  }

  const r = Math.round(lerp(startColor[0], endColor[0], t))
  const g = Math.round(lerp(startColor[1], endColor[1], t))
  const b = Math.round(lerp(startColor[2], endColor[2], t))

  return rgbToHex(r, g, b)
}

const draw = () => {
  if (!canvas.value || !ctx) return

  const width = canvas.value.width
  const height = canvas.value.height
  
  // Clear
  ctx.fillStyle = '#000000' // Background color
  ctx.fillRect(0, 0, width, height)

  // Determine content and style
  let text = getSystemTime()
  let color = '#00FF00' // Default Green
  let scale = 1
  let currentSpeed = speed

  if (props.isPlaying) {
    text = formatSongTime(props.currentSongTime)
    const progress = props.songDuration > 0 ? props.currentSongTime / props.songDuration : 0
    color = getColor(progress)
    
    // Heartbeat logic
    // Base BPM = 60, increases with progress
    const bpm = 60 + (progress * 120) // 60 to 180 BPM
    const beatTime = Date.now() / 1000 * (bpm / 60)
    // Pulse effect: sharp beat
    const beat = Math.sin(beatTime * Math.PI * 2)
    // Only pulse on the "beat" (positive sine wave, sharpened)
    scale = 1 + (Math.max(0, beat) * 0.2 * (0.5 + progress)) // Scale increases with progress
    
    currentSpeed = speed + (progress * 3) // Speed up
  }

  // Update offset
  timeOffset += currentSpeed
  
  ctx.save()
  
  // Diagonal Rotation
  // We need to draw a grid that covers the rotated area
  // Center the rotation
  ctx.translate(width / 2, height / 2)
  ctx.rotate(-Math.PI / 4) // 45 degrees
  ctx.translate(-width / 2, -height / 2)

  // Draw Grid
  ctx.font = `bold ${fontSize}px monospace`
  ctx.textAlign = 'center'
  ctx.textBaseline = 'middle'
  ctx.fillStyle = color

  // Calculate grid dimensions to cover the rotated screen
  // The diagonal of the screen is the max dimension needed
  const diagonal = Math.sqrt(width * width + height * height)
  const gridSize = diagonal * 1.5 // Extra buffer
  const cols = Math.ceil(gridSize / textSpacing)
  const rows = Math.ceil(gridSize / (fontSize * 2))

  const startX = (width - gridSize) / 2
  const startY = (height - gridSize) / 2

  for (let i = 0; i < cols; i++) {
    for (let j = 0; j < rows; j++) {
      const x = startX + i * textSpacing
      // Move Y with timeOffset
      const y = startY + j * (fontSize * 2) - (timeOffset % (fontSize * 2))
      
      ctx.save()
      ctx.translate(x, y)
      ctx.scale(scale, scale)
      ctx.fillText(text, 0, 0)
      ctx.restore()
    }
  }

  ctx.restore()

  animationFrameId = requestAnimationFrame(draw)
}

const resize = () => {
  if (canvas.value) {
    canvas.value.width = window.innerWidth
    canvas.value.height = window.innerHeight
  }
}

onMounted(() => {
  ctx = canvas.value.getContext('2d')
  resize()
  window.addEventListener('resize', resize)
  draw()
})

onBeforeUnmount(() => {
  window.removeEventListener('resize', resize)
  cancelAnimationFrame(animationFrameId)
})

</script>

<style scoped>
.bio-clock-canvas {
  position: fixed;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  z-index: 0; /* Behind content, above body */
  pointer-events: none;
}
</style>
