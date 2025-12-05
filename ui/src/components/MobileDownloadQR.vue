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
import { ref, onMounted, watch } from 'vue'

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
    
    // Generate QR code
    await generateQRCode(data.url)
    
  } catch (err) {
    error.value = err.message || 'Error al generar código QR'
  } finally {
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
  background: rgba(255, 255, 255, 0.15);
  backdrop-filter: blur(10px);
  border: 2px solid rgba(255, 255, 255, 0.3);
  color: #fff;
  font-size: 1.5rem;
  width: 50px;
  height: 50px;
  border-radius: 15px;
  cursor: pointer;
  transition: all 0.3s ease;
  display: flex;
  align-items: center;
  justify-content: center;
}

.qr-trigger-btn:hover {
  background: rgba(255, 255, 255, 0.25);
  transform: scale(1.05);
  box-shadow: 0 8px 20px rgba(0, 0, 0, 0.2);
}

.modal-overlay {
  position: fixed;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  background: rgba(0, 0, 0, 0.7);
  backdrop-filter: blur(5px);
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
  background: linear-gradient(135deg, rgba(102, 126, 234, 0.95) 0%, rgba(118, 75, 162, 0.95) 100%);
  backdrop-filter: blur(20px);
  border-radius: 25px;
  padding: 40px;
  max-width: 500px;
  width: 90%;
  box-shadow: 0 20px 60px rgba(0, 0, 0, 0.5);
  position: relative;
  animation: slideUp 0.3s ease;
  border: 2px solid rgba(255, 255, 255, 0.2);
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
  background: rgba(255, 255, 255, 0.2);
  border: none;
  color: #fff;
  font-size: 1.5rem;
  width: 35px;
  height: 35px;
  border-radius: 50%;
  cursor: pointer;
  transition: all 0.3s;
  display: flex;
  align-items: center;
  justify-content: center;
}

.close-btn:hover {
  background: rgba(255, 255, 255, 0.3);
  transform: rotate(90deg);
}

h2 {
  color: #fff;
  margin-bottom: 10px;
  font-size: 1.8rem;
  text-align: center;
}

.instructions {
  color: rgba(255, 255, 255, 0.9);
  text-align: center;
  margin-bottom: 30px;
  font-size: 0.95rem;
}

.loading, .error {
  text-align: center;
  padding: 40px;
  color: #fff;
}

.spinner {
  border: 4px solid rgba(255, 255, 255, 0.3);
  border-top: 4px solid #fff;
  border-radius: 50%;
  width: 50px;
  height: 50px;
  animation: spin 1s linear infinite;
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
  padding: 20px;
  border-radius: 20px;
  display: inline-block;
  margin-bottom: 25px;
  box-shadow: 0 10px 30px rgba(0, 0, 0, 0.3);
}

.url-section {
  margin-bottom: 25px;
}

.url-label {
  color: rgba(255, 255, 255, 0.9);
  margin-bottom: 10px;
  font-size: 0.9rem;
}

.url-display {
  display: flex;
  gap: 10px;
  align-items: center;
}

.url-input {
  flex: 1;
  padding: 12px 15px;
  border-radius: 12px;
  border: 2px solid rgba(255, 255, 255, 0.3);
  background: rgba(255, 255, 255, 0.15);
  color: #fff;
  font-size: 0.85rem;
  font-family: monospace;
}

.url-input:focus {
  outline: none;
  border-color: rgba(255, 255, 255, 0.5);
  background: rgba(255, 255, 255, 0.2);
}

.copy-btn {
  background: rgba(255, 255, 255, 0.25);
  border: 2px solid rgba(255, 255, 255, 0.3);
  color: #fff;
  padding: 12px 20px;
  border-radius: 12px;
  cursor: pointer;
  font-weight: 600;
  transition: all 0.3s;
  white-space: nowrap;
}

.copy-btn:hover {
  background: rgba(255, 255, 255, 0.35);
  transform: translateY(-2px);
}

.retry-btn {
  background: rgba(255, 255, 255, 0.25);
  border: 2px solid rgba(255, 255, 255, 0.3);
  color: #fff;
  padding: 12px 30px;
  border-radius: 12px;
  cursor: pointer;
  font-weight: 600;
  transition: all 0.3s;
  margin-top: 15px;
}

.retry-btn:hover {
  background: rgba(255, 255, 255, 0.35);
  transform: translateY(-2px);
}

.info-box {
  background: rgba(255, 255, 255, 0.15);
  border-radius: 15px;
  padding: 15px;
  border: 1px solid rgba(255, 255, 255, 0.2);
}

.info-box p {
  color: rgba(255, 255, 255, 0.95);
  margin: 5px 0;
  font-size: 0.85rem;
}

.network-info {
  font-family: monospace;
  font-weight: 600;
}

@media (max-width: 600px) {
  .modal-content {
    padding: 25px;
  }
  
  h2 {
    font-size: 1.5rem;
  }
  
  .qr-code {
    padding: 15px;
  }
  
  .url-display {
    flex-direction: column;
  }
  
  .copy-btn {
    width: 100%;
  }
}
</style>
