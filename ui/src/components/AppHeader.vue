<template>
  <header class="app-console-header">
    <div class="header-main-rack">
      <!-- Left: Logo & Branding -->
      <div class="header-branding" @click="$emit('navigate', 'downloader')">
        <div class="logo-badge">
          <span class="disc-icon">💿</span>
          <div class="brand-text">
            <h1 class="brand-title">BAILANDO SOLO</h1>
          </div>
        </div>
      </div>

      <!-- Center: Navigation Tabs (Responsive & Slob-Free) -->
      <nav class="console-nav-dock">
        <button 
          class="nav-tab-btn" 
          :class="{ active: currentView === 'downloader' }"
          @click="$emit('navigate', 'downloader')"
        >
          <span class="nav-ico">⚡</span>
          <span class="tab-label">Descargas</span>
        </button>

        <button 
          class="nav-tab-btn" 
          :class="{ active: currentView === 'library' || currentView === 'folder' }"
          @click="$emit('navigate', 'library')"
        >
          <span class="nav-ico">📼</span>
          <span class="tab-label">Biblioteca</span>
        </button>

        <button 
          class="nav-tab-btn" 
          :class="{ active: currentView === 'playlists' }"
          @click="$emit('navigate', 'playlists')"
        >
          <span class="nav-ico">📑</span>
          <span class="tab-label">Playlists</span>
        </button>

        <button 
          class="nav-tab-btn" 
          :class="{ active: currentView === 'plaza' }"
          @click="$emit('navigate', 'plaza')"
        >
          <span class="nav-ico">🌐</span>
          <span class="tab-label">La Plaza</span>
        </button>

        <button 
          class="nav-tab-btn" 
          @click="$emit('open-stats')"
        >
          <span class="nav-ico">📊</span>
          <span class="tab-label">Estadísticas</span>
        </button>
      </nav>

      <!-- Right: System Rack -->
      <div class="header-system-rack">
        <!-- Quick Search -->
        <button 
          class="btn-system-tool" 
          @click="$emit('open-search')" 
          title="Buscar (Ctrl+K)"
        >
          🔍 <span class="hotkey-hint">Ctrl+K</span>
        </button>

        <!-- Mobile QR -->
        <button 
          class="btn-system-tool" 
          @click="$emit('open-qr')" 
          title="Descargar en Móvil"
        >
          📱 Móvil
        </button>

        <!-- Profile Switcher -->
        <button 
          class="btn-system-tool" 
          @click="$emit('open-profiles')" 
          title="Perfiles"
        >
          👤 Perfil
        </button>
      </div>
    </div>
  </header>
</template>

<script setup>
defineProps({
  currentView: { type: String, default: 'downloader' }
})

defineEmits(['navigate', 'open-search', 'open-stats', 'open-profiles', 'open-qr'])
</script>

<style scoped>
.app-console-header {
  background: #2b2b2b;
  border: 3px solid #000000;
  box-shadow: inset 1px 1px 0px #666666, inset -1px -1px 0px #111111, 4px 4px 0px #000000;
  margin-bottom: 14px;
  padding: 8px 12px;
}

.header-main-rack {
  display: flex;
  justify-content: space-between;
  align-items: center;
  gap: 10px;
  flex-wrap: wrap;
}

.header-branding {
  cursor: pointer;
  user-select: none;
  flex-shrink: 0;
  -webkit-app-region: no-drag;
}

.logo-badge {
  display: flex;
  align-items: center;
  gap: 8px;
  background: #1a1a1a;
  border: 2px solid #000000;
  padding: 6px 10px;
  box-shadow: inset 1px 1px 0px #444444;
}

.disc-icon {
  font-size: 20px;
}

.brand-title {
  font-family: var(--font-pixel);
  font-size: 11px;
  color: #00f0ff;
  margin: 0;
  letter-spacing: 0.5px;
  text-shadow: 1px 1px 0px #000000;
}

/* Nav Dock */
.console-nav-dock {
  display: flex;
  gap: 6px;
  flex-wrap: wrap;
  align-items: center;
  -webkit-app-region: no-drag;
}

.nav-tab-btn {
  display: flex;
  align-items: center;
  gap: 5px;
  font-family: var(--font-pixel);
  font-size: 8px;
  background: #444444;
  color: #ffffff;
  border: 2px solid #000000;
  padding: 8px 12px;
  cursor: pointer;
  box-shadow: inset 1px 1px 0px #888888, inset -1px -1px 0px #222222, 2px 2px 0px #000000;
  transition: all 0.1s ease;
  white-space: nowrap;
  -webkit-app-region: no-drag;
}

.nav-tab-btn:hover {
  background: #555555;
  transform: translateY(-2px);
}

.nav-tab-btn.active {
  background: #00A8E1;
  color: #ffffff;
  box-shadow: inset 2px 2px 0px #66d9ff, inset -2px -2px 0px #005577, 2px 2px 0px #000000;
  transform: translateY(1px);
}

.nav-ico {
  font-size: 11px;
}

/* System Rack */
.header-system-rack {
  display: flex;
  align-items: center;
  gap: 6px;
  flex-wrap: wrap;
  -webkit-app-region: no-drag;
}

.btn-system-tool {
  display: flex;
  align-items: center;
  gap: 5px;
  background: #d4d4d4;
  border: 2px solid #000000;
  font-family: var(--font-pixel);
  font-size: 7.5px;
  color: #111111;
  padding: 6px 9px;
  cursor: pointer;
  box-shadow: inset 1px 1px 0px #ffffff, inset -1px -1px 0px #777777, 2px 2px 0px #000000;
  height: 34px;
  white-space: nowrap;
  -webkit-app-region: no-drag;
}

.btn-system-tool:hover {
  background: #ffffff;
}

.btn-system-tool:active {
  transform: translate(1px, 1px);
  box-shadow: inset 1px 1px 0px #000000;
}

.hotkey-hint {
  font-family: var(--font-mono);
  font-size: 9px;
  background: #111111;
  color: #00f0ff;
  padding: 1px 4px;
  border-radius: 2px;
}

@media (max-width: 900px) {
  .app-console-header {
    padding: 6px 8px;
  }
  .header-main-rack {
    justify-content: center;
    gap: 8px;
  }
  .console-nav-dock {
    justify-content: center;
    width: 100%;
  }
  .header-system-rack {
    justify-content: center;
  }
}
</style>
