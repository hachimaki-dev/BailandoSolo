<template>
  <div v-if="isOpen" class="retro-modal-overlay" @click="$emit('close')">
    <div class="retro-modal-box qr-modal-box" @click.stop>
      <div class="retro-modal-header">
        <div class="header-title-left">
          <span class="led-dot" :class="activeTab === 'tunnel' && tunnelActive ? 'led-cyan' : 'led-green'"></span>
          <h3>📱 ACCESO MÓVIL & DESCARGAS</h3>
        </div>
        <button class="btn-retro-icon btn-close-modal" @click="$emit('close')" title="Cerrar (Esc)">✕</button>
      </div>

      <!-- Mode Selector Tabs -->
      <div class="tunnel-mode-tabs">
        <button 
          class="tab-btn" 
          :class="{ active: activeTab === 'local' }" 
          @click="selectTab('local')"
        >
          🏠 RED LOCAL / WIFI
        </button>
        <button 
          class="tab-btn" 
          :class="{ active: activeTab === 'tunnel' }" 
          @click="selectTab('tunnel')"
        >
          ⚡ MODO UNIVERSIDAD (TÚNEL)
        </button>
      </div>
      
      <!-- TAB 1: LOCAL NETWORK -->
      <div v-if="activeTab === 'local'">
        <p class="qr-instructions">
          Para redes domésticas o si conectas tu PC a la <strong>Zona Wi-Fi (Hotspot)</strong> de tu móvil:
        </p>
        
        <div v-if="loading" class="qr-loading-box">
          <div class="spinner-pixel"></div>
          <p>Cargando información de red...</p>
        </div>
        
        <div v-else-if="error" class="qr-error-box">
          <p>⚠️ {{ error }}</p>
          <button @click="loadInfo" class="btn-retro-secondary btn-sm">Reintentar</button>
        </div>
        
        <div v-show="!loading && !error" class="qr-main-section">
          <div class="qr-code-wrapper">
            <div ref="localQrContainer" class="qr-code"></div>
          </div>
          
          <div class="url-manual-box">
            <label class="url-label">Ingresa desde el navegador de tu móvil:</label>
            <div class="url-input-strip">
              <input 
                type="text" 
                :value="localMobileUrl" 
                readonly 
                class="retro-input"
              />
              <button @click="copyText(localMobileUrl)" class="btn-retro-primary btn-sm">
                {{ copiedLocal ? '✓ Copiado' : '📋 Copiar' }}
              </button>
            </div>
          </div>
          
          <div class="network-info-pill">
            <span>ℹ️ IP Local: <strong>{{ networkIp }}</strong> (Puerto {{ port }})</span>
          </div>

          <div class="network-warning-pill">
            ⚠️ <strong>¿En la Universidad?</strong> Si la red tiene <em>AP Isolation</em> (como Eduroam), los dispositivos no pueden verse entre sí. Activa la pestaña <strong>"MODO UNIVERSIDAD"</strong> arriba o comparte internet desde tu celular a la PC.
          </div>
        </div>
      </div>

      <!-- TAB 2: UNIVERSITY / CLOUDFLARE TUNNEL -->
      <div v-if="activeTab === 'tunnel'">
        <p class="qr-instructions">
          Genera un <strong>túnel seguro HTTPS (puerto 443)</strong> para saltar el firewall y el bloqueo de <em>AP Isolation</em> de la universidad:
        </p>

        <!-- Tunnel Not Active -->
        <div v-if="!tunnelActive && !tunnelStarting" class="tunnel-inactive-box">
          <div class="shield-icon">🛡️</div>
          <h4>Túnel Remoto Apagado</h4>
          <p class="tunnel-desc">
            Crea un enlace público cifrado con Cloudflare para que tu celular pueda reproducir y descargar música desde cualquier red (WiFi universidad o datos móviles 4G/5G).
          </p>
          <button @click="startTunnelAction" class="btn-retro-action btn-tunnel-start">
            ⚡ ACTIVAR TÚNEL UNIVERSITARIO
          </button>
        </div>

        <!-- Tunnel Starting / Loading -->
        <div v-else-if="tunnelStarting" class="qr-loading-box">
          <div class="spinner-pixel"></div>
          <p>Creando túnel seguro Cloudflare HTTPS...</p>
          <small style="color: #888; font-size: 10px;">Estableciendo conexión por puerto 443...</small>
        </div>

        <!-- Tunnel Active -->
        <div v-else class="qr-main-section">
          <div class="tunnel-badge-active">
            <span class="pulse-dot">●</span> TÚNEL SEGURO ACTIVO (PORT 443 HTTPS)
          </div>

          <div class="qr-code-wrapper">
            <div ref="tunnelQrContainer" class="qr-code"></div>
          </div>

          <div class="url-manual-box">
            <label class="url-label">Enlace HTTPS del Túnel (Universal):</label>
            <div class="url-input-strip">
              <input 
                type="text" 
                :value="tunnelMobileUrl" 
                readonly 
                class="retro-input"
                style="color: #00f0ff;"
              />
              <button @click="copyText(tunnelMobileUrl)" class="btn-retro-primary btn-sm">
                {{ copiedTunnel ? '✓ Copiado' : '📋 Copiar' }}
              </button>
            </div>
          </div>

          <div style="display: flex; gap: 8px; justify-content: center; margin-top: 8px;">
            <button @click="stopTunnelAction" class="btn-retro-secondary btn-sm" style="color: #ff80bf; border-color: #ff007f;">
              ⏹️ Detener Túnel
            </button>
          </div>

          <div class="offline-tip-pill" style="margin-top: 10px;">
            💡 <strong>100% Funcional en la Universidad:</strong> Puedes escanear este QR desde tu teléfono conectado a la red de la universidad o incluso con tus datos móviles. ¡Descarga las canciones que quieras a tu teléfono y quedarán guardadas offline para siempre!
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, watch, nextTick, onMounted } from 'vue'
import QRCode from 'qrcode'
import { apiUrl } from '../config'

const props = defineProps({
  isOpen: Boolean
})

const emit = defineEmits(['close'])

const activeTab = ref('tunnel') // Default to university tunnel for restricted networks
const loading = ref(false)
const error = ref(null)

// Local Network State
const localMobileUrl = ref('')
const networkIp = ref('127.0.0.1')
const port = ref(5001)
const copiedLocal = ref(false)
const localQrContainer = ref(null)

// Tunnel State
const tunnelActive = ref(false)
const tunnelStarting = ref(false)
const tunnelUrl = ref('')
const tunnelMobileUrl = ref('')
const copiedTunnel = ref(false)
const tunnelQrContainer = ref(null)

const selectTab = async (tab) => {
  activeTab.value = tab
  await nextTick()
  if (tab === 'local') {
    await renderLocalQR()
  } else if (tab === 'tunnel' && tunnelActive.value) {
    await renderTunnelQR()
  }
}

const loadInfo = async () => {
  loading.value = true
  error.value = null
  
  try {
    const response = await fetch(apiUrl('/api/mobile/info'))
    if (!response.ok) throw new Error('No se pudo obtener información de red')
    
    const data = await response.json()
    networkIp.value = data.ip || '127.0.0.1'
    port.value = data.port || 5001
    localMobileUrl.value = data.url || `http://${networkIp.value}:${port.value}/mobile`

    if (data.tunnel && data.tunnel.running) {
      tunnelActive.value = true
      tunnelUrl.value = data.tunnel.url || ''
      tunnelMobileUrl.value = data.tunnel.mobile_url || `${tunnelUrl.value}/mobile`
    } else {
      tunnelActive.value = false
    }
    
    loading.value = false
    await nextTick()
    
    if (activeTab.value === 'tunnel' && tunnelActive.value) {
      await renderTunnelQR()
    } else {
      await renderLocalQR()
    }
  } catch (err) {
    console.error('Error loading mobile info:', err)
    error.value = 'No se pudo conectar con el servidor local'
    loading.value = false
  }
}

const renderLocalQR = async () => {
  if (!localMobileUrl.value || !localQrContainer.value) return
  await generateQRCode(localMobileUrl.value, localQrContainer.value)
}

const renderTunnelQR = async () => {
  if (!tunnelMobileUrl.value || !tunnelQrContainer.value) return
  await generateQRCode(tunnelMobileUrl.value, tunnelQrContainer.value)
}

const generateQRCode = async (url, container) => {
  try {
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
    console.error('Error drawing QR code:', err)
  }
}

const startTunnelAction = async () => {
  tunnelStarting.value = true
  try {
    const res = await fetch(apiUrl('/api/tunnel/start'), { method: 'POST' })
    const data = await res.json()
    if (data.status === 'started' || data.status === 'already_running') {
      tunnelActive.value = true
      tunnelUrl.value = data.url
      tunnelMobileUrl.value = data.mobile_url || `${data.url}/mobile`
      tunnelStarting.value = false
      await nextTick()
      await renderTunnelQR()
    } else {
      alert('No se pudo iniciar el túnel: ' + (data.error || 'Error desconocido'))
      tunnelStarting.value = false
    }
  } catch (e) {
    alert('Error al contactar con el servicio de túnel: ' + e.message)
    tunnelStarting.value = false
  }
}

const stopTunnelAction = async () => {
  try {
    await fetch(apiUrl('/api/tunnel/stop'), { method: 'POST' })
    tunnelActive.value = false
    tunnelUrl.value = ''
    tunnelMobileUrl.value = ''
  } catch (e) {
    console.error('Error stopping tunnel:', e)
  }
}

const copyText = async (text) => {
  try {
    await navigator.clipboard.writeText(text)
    if (activeTab.value === 'tunnel') {
      copiedTunnel.value = true
      setTimeout(() => { copiedTunnel.value = false }, 2000)
    } else {
      copiedLocal.value = true
      setTimeout(() => { copiedLocal.value = false }, 2000)
    }
  } catch (err) {
    console.error('Error copying text:', err)
  }
}

watch(() => props.isOpen, (newVal) => {
  if (newVal) {
    loadInfo()
  }
})

onMounted(() => {
  if (props.isOpen) {
    loadInfo()
  }
})
</script>

<style scoped>
.qr-modal-box {
  max-width: 500px;
  width: 95%;
  text-align: center;
}

.header-title-left {
  display: flex;
  align-items: center;
  gap: 8px;
}

.led-cyan {
  background: #00f0ff;
  box-shadow: 0 0 6px #00f0ff;
}

.btn-close-modal {
  width: 36px;
  height: 36px;
  font-size: 16px;
  display: flex;
  align-items: center;
  justify-content: center;
}

.tunnel-mode-tabs {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 6px;
  background: #11111a;
  padding: 4px;
  border: 2px solid #000;
  margin-bottom: 12px;
}

.tab-btn {
  font-family: var(--font-pixel);
  font-size: 7.5px;
  padding: 8px 4px;
  border: 2px solid #000;
  background: #252538;
  color: #a0a0b8;
  cursor: pointer;
  box-shadow: inset 1px 1px 0 #444455;
}

.tab-btn.active {
  background: var(--color-retro-blue, #5a5aff);
  color: #ffffff;
  border-color: #00f0ff;
  box-shadow: inset 2px 2px 0 #8888ff, 2px 2px 0 #000;
}

.qr-instructions {
  font-family: var(--font-mono);
  font-size: 11px;
  color: #333333;
  margin-bottom: 12px;
  line-height: 1.4;
}

.qr-loading-box, .qr-error-box {
  padding: 24px;
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
  margin-bottom: 12px;
}

.url-manual-box {
  text-align: left;
  margin-bottom: 10px;
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
  font-family: var(--font-pixel);
  cursor: pointer;
}

.network-info-pill {
  background: #d4d4d4;
  border: 1px solid #000000;
  padding: 6px;
  font-family: var(--font-mono);
  font-size: 10px;
  color: #333333;
}

.network-warning-pill {
  margin-top: 10px;
  font-size: 10px;
  color: #e65100;
  background: #fff3e0;
  border: 1px dashed #ff9800;
  padding: 8px;
  line-height: 1.4;
  text-align: left;
}

.tunnel-inactive-box {
  background: #181828;
  border: 2px solid #000;
  padding: 20px 16px;
  margin-bottom: 12px;
  box-shadow: inset 1px 1px 0 #333348, 2px 2px 0 #000;
}

.shield-icon {
  font-size: 32px;
  margin-bottom: 6px;
}

.tunnel-inactive-box h4 {
  font-family: var(--font-pixel);
  font-size: 10px;
  color: #ffb703;
  margin-bottom: 8px;
}

.tunnel-desc {
  font-size: 11px;
  color: #a0a0b8;
  line-height: 1.5;
  margin-bottom: 14px;
}

.btn-tunnel-start {
  background: linear-gradient(180deg, #00f0ff 0%, #0077b6 100%);
  color: #000;
  font-weight: bold;
  font-family: var(--font-pixel);
  font-size: 8px;
  padding: 12px 18px;
  border: 2px solid #000;
  box-shadow: inset 1px 1px 0 rgba(255,255,255,0.6), 3px 3px 0 #000;
  cursor: pointer;
  transition: transform 0.1s;
}

.btn-tunnel-start:active {
  transform: translate(2px, 2px);
}

.tunnel-badge-active {
  background: #003322;
  color: #39ff14;
  font-family: var(--font-pixel);
  font-size: 7.5px;
  padding: 6px 10px;
  border: 2px solid #39ff14;
  margin-bottom: 12px;
  display: inline-flex;
  align-items: center;
  gap: 6px;
  box-shadow: 0 0 8px rgba(57, 255, 20, 0.3);
}

.pulse-dot {
  animation: blink 1.2s infinite;
}

@keyframes blink {
  0%, 100% { opacity: 1; }
  50% { opacity: 0.2; }
}

.offline-tip-pill {
  font-size: 10px;
  color: #a0a0b8;
  background: #161622;
  border: 1px dashed #444466;
  padding: 8px;
  border-radius: 4px;
  line-height: 1.4;
  text-align: left;
}
</style>
