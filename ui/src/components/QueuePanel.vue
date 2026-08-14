<template>
  <div>
    <!-- Backdrop Overlay -->
    <div v-if="isOpen" class="queue-backdrop" @click="$emit('close')"></div>

    <!-- Sliding Drawer Panel -->
    <div class="queue-panel" :class="{ open: isOpen }">
      <div class="queue-header">
        <div class="header-title-group">
          <h3>📑 COLA DE REPRODUCCIÓN</h3>
          <span class="queue-stats-badge">{{ queue.length }} PISTAS</span>
        </div>
        <button class="btn-retro-icon btn-close-queue" @click="$emit('close')" title="Cerrar cola (Esc)">
          ✕
        </button>
      </div>

      <!-- Queue Action Bar -->
      <div v-if="queue.length > 0" class="queue-action-bar">
        <button class="btn-retro-secondary btn-sm" @click="$emit('save-as-playlist')">
          💾 Guardar Playlist
        </button>
        <button class="btn-retro-danger btn-sm" @click="$emit('clear-queue')">
          🗑 Vaciar
        </button>
      </div>

      <!-- Queue List -->
      <div class="queue-list">
        <div v-if="queue.length === 0" class="empty-queue-panel">
          <div class="empty-ico">🎵</div>
          <p>Tu cola de reproducción está vacía.</p>
          <small>Agrega canciones haciendo click derecho o usando el botón ＋</small>
        </div>

        <div 
          v-else 
          v-for="(song, index) in queue" 
          :key="song.path || index" 
          class="queue-item"
          @click="$emit('play-item', index)"
        >
          <div class="queue-num">{{ index + 1 }}</div>
          
          <div class="queue-item-info">
            <div class="queue-item-title">{{ song.title }}</div>
            <div class="queue-item-meta">{{ song.uploader || song.folder || 'Desconocido' }}</div>
          </div>

          <div class="queue-item-controls" @click.stop>
            <button 
              v-if="index > 0" 
              class="move-btn" 
              @click="$emit('move-item', { from: index, to: index - 1 })" 
              title="Mover arriba"
            >
              ▲
            </button>
            <button 
              v-if="index < queue.length - 1" 
              class="move-btn" 
              @click="$emit('move-item', { from: index, to: index + 1 })" 
              title="Mover abajo"
            >
              ▼
            </button>
            <button class="remove-btn" @click="$emit('remove-item', index)" title="Quitar de la cola">
              ✕
            </button>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
defineProps({
  queue: { type: Array, default: () => [] },
  isOpen: Boolean
})

defineEmits(['close', 'remove-item', 'play-item', 'move-item', 'clear-queue', 'save-as-playlist'])
</script>

<style scoped>
.queue-backdrop {
  position: fixed;
  top: 0;
  left: 0;
  width: 100vw;
  height: 100vh;
  background: rgba(0, 0, 0, 0.5);
  backdrop-filter: blur(2px);
  z-index: 1999;
}

.queue-panel {
  position: fixed;
  top: 0;
  right: -360px;
  width: 340px;
  height: 100vh;
  background: #d4d4d4;
  border-left: 4px solid #000000;
  box-shadow: -6px 0 20px rgba(0, 0, 0, 0.4);
  z-index: 2000;
  transition: right 0.25s cubic-bezier(0.2, 0.9, 0.3, 1);
  padding: 16px;
  display: flex;
  flex-direction: column;
}

.queue-panel.open {
  right: 0;
}

.queue-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 12px;
  padding-bottom: 10px;
  border-bottom: 3px solid #000000;
}

.header-title-group h3 {
  font-family: var(--font-pixel);
  font-size: 10px;
  margin: 0;
  color: #000000;
}

.queue-stats-badge {
  font-family: var(--font-mono);
  font-size: 10px;
  color: #0077b6;
  font-weight: bold;
}

.btn-close-queue {
  width: 36px;
  height: 36px;
  font-size: 16px;
  font-weight: bold;
  display: flex;
  align-items: center;
  justify-content: center;
}

.queue-action-bar {
  display: flex;
  justify-content: space-between;
  gap: 8px;
  margin-bottom: 10px;
  padding-bottom: 8px;
  border-bottom: 1px solid #cccccc;
}

.btn-sm {
  padding: 6px 10px;
  font-size: 9px;
}

.empty-queue-panel {
  padding: 40px 10px;
  text-align: center;
  font-family: var(--font-mono);
  color: #666666;
}

.empty-ico {
  font-size: 32px;
  margin-bottom: 8px;
}

.empty-queue-panel p {
  font-size: 12px;
  font-weight: bold;
  margin-bottom: 4px;
}

.empty-queue-panel small {
  font-size: 10px;
}

.queue-list {
  flex: 1;
  overflow-y: auto;
}

.queue-item {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 8px 10px;
  background: #ffffff;
  border: 2px solid #000000;
  margin-bottom: 6px;
  cursor: pointer;
  box-shadow: 2px 2px 0px #000000;
  transition: all 0.1s ease;
}

.queue-item:hover {
  background: #e0f2fe;
  transform: translateX(-2px);
}

.queue-num {
  font-family: var(--font-pixel);
  font-size: 9px;
  color: #0088cc;
  width: 18px;
  text-align: center;
}

.queue-item-info {
  flex: 1;
  min-width: 0;
}

.queue-item-title {
  font-family: var(--font-mono);
  font-size: 12px;
  font-weight: 700;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

.queue-item-meta {
  font-family: var(--font-mono);
  font-size: 10px;
  color: #666666;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

.queue-item-controls {
  display: flex;
  align-items: center;
  gap: 4px;
}

.move-btn, .remove-btn {
  background: #e4e4e4;
  border: 1.5px solid #000000;
  font-size: 11px;
  cursor: pointer;
  width: 28px;
  height: 28px;
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 0;
}

.move-btn:hover {
  background: #ffffff;
}

.remove-btn:hover {
  background: #ff6b6b;
  color: #ffffff;
}
</style>
