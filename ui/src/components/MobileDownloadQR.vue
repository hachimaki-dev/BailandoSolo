<template>
  <div class="mobile-qr-container">
    <button class="qr-trigger-btn" @click="toggleModal" title="Descargar en móvil">
      📱
    </button>

    <div v-if="isOpen" class="modal-overlay" @click="toggleModal">
      <div class="modal-content" @click.stop>
        <button class="close-btn" @click="toggleModal">✕</button>
        
        <h2>Descargar en Móvil</h2>
        <p class="instructions">Escanea el código QR con tu dispositivo móvil para acceder a la biblioteca</p>
        
        <div v-if="loading" class="loading">
          <div class="spinner"></div>
          <p>Generando código QR...</p>
        </div>
        
        <div v-else-if="error" class="error">
          <p>{{ error }}</p>
          <button @click="loadQR" class="retry-btn">Reintentar</button>
        </div>
        
        <div v-else class="qr-section">
          <div id="qrcode" class="qr-code"></div>
          
          <div class="url-section">
            <p class="url-label">O ingresa manualmente:</p>
            <div class="url-display">
              <input 
                type="text" 
                :value="mobileUrl" 
                readonly 
                ref="urlInput"
                class="url-input"
              />
              <button @click="copyUrl" class="copy-btn">
                {{ copied ? '✓ Copiado' : '📋 Copiar' }}
              </button>
            </div>
          </div>
          
          <div class="info-box">
            <p>ℹ️ Asegúrate de que tu móvil esté conectado a la misma red WiFi</p>
            <p class="network-info">Red: {{ networkIp }}</p>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted, watch, nextTick } from 'vue'

const isOpen = ref(false)
const loading = ref(false)
const error = ref(null)
const mobileUrl = ref('')
const networkIp = ref('')
const copied = ref(false)
const urlInput = ref(null)

let QRCode = null

const toggleModal = () => {
  isOpen.value = !isOpen.value
  if (isOpen.value && !mobileUrl.value) {
    loadQR()
  }
}

const loadQR = async () => {
  loading.value = true
  error.value = null
  
  try {
    // Dynamically import QRCode library
    if (!QRCode) {
      const module = await import('qrcode')
      QRCode = module.default
    }
    
    // Get network info from backend
    const response = await fetch('/api/mobile/info')
    if (!response.ok) throw new Error('No se pudo obtener la información de red')
    
    const data = await response.json()
    mobileUrl.value = data.url
    networkIp.value = data.ip
    
    // Stop loading to render the container
    loading.value = false
    
    // Wait for DOM update
    await nextTick()
    
    // Generate QR code
    await generateQRCode(data.url)
    
  } catch (err) {
    console.error(err)
    error.value = err.message || 'Error al generar código QR'
    loading.value = false
  }
}

const generateQRCode = async (url) => {
  const container = document.getElementById('qrcode')
  if (!container) return
  
  // Clear previous QR
  container.innerHTML = ''
  
  // Generate QR code as canvas
  const canvas = document.createElement('canvas')
  await QRCode.toCanvas(canvas, url, {
    width: 280,
    margin: 2,
    color: {
      dark: '#000000',
      light: '#ffffff'
    }
  })
  
  container.appendChild(canvas)
}

const copyUrl = async () => {
  try {
    await navigator.clipboard.writeText(mobileUrl.value)
    copied.value = true
    setTimeout(() => {
      copied.value = false
    }, 2000)
  } catch (err) {
    // Fallback for older browsers
    urlInput.value?.select()
    document.execCommand('copy')
    copied.value = true
    setTimeout(() => {
      copied.value = false
    }, 2000)
  }
}

// Reload QR when modal opens
watch(isOpen, (newVal) => {
  if (newVal && mobileUrl.value) {
    // Regenerate QR in case it was removed from DOM
    setTimeout(() => {
      if (document.getElementById('qrcode')) {
        generateQRCode(mobileUrl.value)
      }
    }, 100)
  }
})
</script>

<style scoped>
.mobile-qr-container {
  position: relative;
}

.qr-trigger-btn {
  background: #b4b4b4;
  border: 3px solid #000;
  color: #000;
  font-size: 1.5rem;
  width: 50px;
  height: 50px;
  cursor: pointer;
  transition: transform 0.1s;
  display: flex;
  align-items: center;
  justify-content: center;
  box-shadow: inset -2px -2px 0 #7c7c7c, inset 2px 2px 0 #fff;
}

.qr-trigger-btn:hover {
  background: #c4c4c4;
  transform: translateY(-2px);
}

.qr-trigger-btn:active {
  box-shadow: inset 2px 2px 0 #000;
  transform: translate(2px, 2px);
}

.modal-overlay {
  position: fixed;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  background: rgba(0, 0, 0, 0.8);
  backdrop-filter: blur(2px);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 10000;
  animation: fadeIn 0.3s ease;
}

@keyframes fadeIn {
  from { opacity: 0; }
  to { opacity: 1; }
}

.modal-content {
  background: #e4e4e4;
  border: 4px solid #000;
  padding: 30px;
  max-width: 500px;
  width: 90%;
  box-shadow: inset -2px -2px 0 #7c7c7c, inset 2px 2px 0 #fff, 10px 10px 0 #000;
  position: relative;
  animation: slideUp 0.3s ease;
  image-rendering: pixelated;
  font-family: 'Press Start 2P', cursive;
}

@keyframes slideUp {
  from { 
    opacity: 0;
    transform: translateY(30px);
  }
  to { 
    opacity: 1;
    transform: translateY(0);
  }
}

.close-btn {
  position: absolute;
  top: 15px;
  right: 15px;
  background: #ff5a5a;
  border: 3px solid #000;
  color: #fff;
  font-size: 1rem;
  width: 35px;
  height: 35px;
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
  box-shadow: inset -2px -2px 0 #aa0000, inset 2px 2px 0 #ffaaaa;
}

.close-btn:hover {
  background: #ff6a6a;
}

.close-btn:active {
  box-shadow: inset 2px 2px 0 #000;
  transform: translate(2px, 2px);
}

h2 {
  color: #000;
  margin-bottom: 15px;
  font-size: 1.2rem;
  text-align: center;
  text-shadow: 2px 2px 0 #ccc;
  line-height: 1.5;
}

.instructions {
  color: #555;
  text-align: center;
  margin-bottom: 30px;
  font-size: 0.7rem;
  font-family: 'Courier New', monospace;
  font-weight: bold;
}

.loading, .error {
  text-align: center;
  padding: 40px;
  color: #000;
}

.spinner {
  border: 4px solid #ccc;
  border-top: 4px solid #5a5aff;
  width: 50px;
  height: 50px;
  animation: spin 1s steps(8) infinite;
  margin: 0 auto 20px;
}

@keyframes spin {
  0% { transform: rotate(0deg); }
  100% { transform: rotate(360deg); }
}

.qr-section {
  text-align: center;
}

.qr-code {
  background: #fff;
  padding: 15px;
  border: 4px solid #000;
  display: inline-block;
  margin-bottom: 25px;
  box-shadow: 6px 6px 0 #000;
}

.url-section {
  margin-bottom: 25px;
}

.url-label {
  color: #000;
  margin-bottom: 10px;
  font-size: 0.7rem;
}

.url-display {
  display: flex;
  gap: 10px;
  align-items: center;
}

.url-input {
  flex: 1;
  padding: 12px 15px;
  border: 3px solid #000;
  background: #fff;
  color: #000;
  font-size: 0.7rem;
  font-family: 'Courier New', monospace;
  box-shadow: inset 2px 2px 0 #ccc;
}

.url-input:focus {
  outline: none;
  background: #ffffcc;
}

.copy-btn {
  background: #5a5aff;
  border: 3px solid #000;
  color: #fff;
  padding: 12px 15px;
  cursor: pointer;
  font-family: 'Press Start 2P', cursive;
  font-size: 0.6rem;
  box-shadow: inset -2px -2px 0 #0000aa, inset 2px 2px 0 #aaaaff;
  white-space: nowrap;
}

.copy-btn:hover {
  background: #6a6aff;
}

.copy-btn:active {
  box-shadow: inset 2px 2px 0 #000;
  transform: translate(2px, 2px);
}

.retry-btn {
  background: #5a5aff;
  border: 3px solid #000;
  color: #fff;
  padding: 12px 20px;
  cursor: pointer;
  font-family: 'Press Start 2P', cursive;
  font-size: 0.7rem;
  box-shadow: inset -2px -2px 0 #0000aa, inset 2px 2px 0 #aaaaff;
  margin-top: 15px;
}

.retry-btn:active {
  box-shadow: inset 2px 2px 0 #000;
  transform: translate(2px, 2px);
}

.info-box {
  background: #ffff00;
  padding: 15px;
  border: 4px solid #000;
  box-shadow: 4px 4px 0 #000;
}

.info-box p {
  color: #000;
  margin: 5px 0;
  font-size: 0.6rem;
  font-family: 'Courier New', monospace;
  font-weight: bold;
}

.network-info {
  font-family: 'Courier New', monospace;
  font-weight: 800;
  text-decoration: underline;
}

@media (max-width: 600px) {
  .modal-content {
    padding: 20px;
  }
  
  h2 {
    font-size: 1rem;
  }
  
  .qr-code {
    padding: 10px;
  }
  
  .url-display {
    flex-direction: column;
  }
  
  .copy-btn {
    width: 100%;
  }
}
</style>
