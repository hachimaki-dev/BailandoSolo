<template>
  <div v-if="isOpen" class="retro-modal-overlay" @click="$emit('close')">
    <div class="retro-modal-box qr-modal-box" @click.stop>
      <div class="retro-modal-header">
        <div class="header-title-left">
          <span class="led-dot led-green"></span>
          <h3>📱 DESCARGA EN MÓVIL (RED LOCAL)</h3>
        </div>
        <button class="btn-retro-icon btn-close-modal" @click="$emit('close')" title="Cerrar (Esc)">✕</button>
      </div>
      
      <p class="qr-instructions">Escanea el código QR con tu móvil (conectado al mismo WiFi) para acceder al reproductor móvil:</p>
      
      <div v-if="loading" class="qr-loading-box">
        <div class="spinner-pixel"></div>
        <p>Generando código QR...</p>
      </div>
      
      <div v-else-if="error" class="qr-error-box">
        <p>⚠️ {{ error }}</p>
        <button @click="loadQR" class="btn-retro-secondary btn-sm">Reintentar</button>
      </div>
      
      <div v-else class="qr-main-section">
        <div class="qr-code-wrapper">
          <div id="qrcode" class="qr-code"></div>
        </div>
        
        <div class="url-manual-box">
          <label class="url-label">O ingresa manualmente desde tu navegador móvil:</label>
          <div class="url-input-strip">
            <input 
              type="text" 
              :value="mobileUrl" 
              readonly 
              ref="urlInput"
              class="retro-input"
            />
            <button @click="copyUrl" class="btn-retro-primary btn-sm">
              {{ copied ? '✓ Copiado' : '📋 Copiar' }}
            </button>
          </div>
        </div>
        
        <div class="network-info-pill">
          <span>ℹ️ WiFi local IP: <strong>{{ networkIp }}</strong></span>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, watch, nextTick } from 'vue'

const props = defineProps({
  isOpen: Boolean
})

const emit = defineEmits(['close'])

const loading = ref(false)
const error = ref(null)
const mobileUrl = ref('')
const networkIp = ref('')
const copied = ref(false)
const urlInput = ref(null)

let QRCode = null

const loadQR = async () => {
  loading.value = true
  error.value = null
  
  try {
    if (!QRCode) {
      const module = await import('qrcode')
      QRCode = module.default
    }
    
    const response = await fetch('/api/mobile/info')
    if (!response.ok) throw new Error('No se pudo obtener la información de red')
    
    const data = await response.json()
    mobileUrl.value = data.url
    networkIp.value = data.ip
    
    loading.value = false
    await nextTick()
    await generateQRCode(data.url)
  } catch (err) {
    console.error('Error loading QR:', err)
    error.value = 'No se pudo conectar con el servidor local'
    loading.value = false
  }
}

const generateQRCode = async (url) => {
  try {
    const container = document.getElementById('qrcode')
    if (!container) return
    container.innerHTML = ''
    
    const canvas = document.createElement('canvas')
    await QRCode.toCanvas(canvas, url, {
      width: 200,
      margin: 2,
      color: {
        dark: '#000000',
        light: '#ffffff'
      }
    })
    container.appendChild(canvas)
  } catch (err) {
    console.error('Error generating QR canvas:', err)
    error.value = 'Error al dibujar código QR'
  }
}

const copyUrl = async () => {
  try {
    await navigator.clipboard.writeText(mobileUrl.value)
    copied.value = true
    setTimeout(() => {
      copied.value = false
    }, 2000)
  } catch (err) {
    console.error('Error copying URL:', err)
  }
}

watch(() => props.isOpen, (newVal) => {
  if (newVal) {
    loadQR()
  }
})
</script>

<style scoped>
.qr-modal-box {
  max-width: 480px;
  width: 95%;
  text-align: center;
}

.header-title-left {
  display: flex;
  align-items: center;
  gap: 8px;
}

.btn-close-modal {
  width: 36px;
  height: 36px;
  font-size: 16px;
  display: flex;
  align-items: center;
  justify-content: center;
}

.qr-instructions {
  font-family: var(--font-mono);
  font-size: 11px;
  color: #333333;
  margin-bottom: 14px;
}

.qr-loading-box, .qr-error-box {
  padding: 30px;
  font-family: var(--font-mono);
}

.spinner-pixel {
  width: 24px;
  height: 24px;
  border: 3px solid #666;
  border-top-color: #0088cc;
  border-radius: 50%;
  animation: spin 0.8s linear infinite;
  margin: 0 auto 10px auto;
}

@keyframes spin {
  to { transform: rotate(360deg); }
}

.qr-code-wrapper {
  display: inline-block;
  background: #ffffff;
  padding: 10px;
  border: 3px solid #000000;
  box-shadow: 2px 2px 0px #000000;
  margin-bottom: 14px;
}

.url-manual-box {
  text-align: left;
  margin-bottom: 12px;
}

.url-label {
  display: block;
  font-family: var(--font-pixel);
  font-size: 7px;
  color: #222222;
  margin-bottom: 4px;
}

.url-input-strip {
  display: flex;
  gap: 6px;
}

.url-input-strip input {
  flex: 1;
  padding: 8px;
  font-family: var(--font-mono);
  font-size: 12px;
}

.btn-sm {
  padding: 6px 12px;
  font-size: 9px;
}

.network-info-pill {
  background: #d4d4d4;
  border: 1px solid #000000;
  padding: 6px;
  font-family: var(--font-mono);
  font-size: 10px;
  color: #333333;
}
</style>
