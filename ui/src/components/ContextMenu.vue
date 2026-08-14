<template>
  <div 
    v-if="show" 
    class="retro-context-menu" 
    :style="{ top: clampedY + 'px', left: clampedX + 'px' }"
    @click.stop
  >
    <div class="menu-header">
      <span class="menu-song-title">{{ song?.title || 'Canción' }}</span>
    </div>

    <div class="menu-items">
      <button class="menu-item primary-action" @click="handleAction('play-now')">
        <span class="menu-icon">▶</span>
        <span>Reproducir ahora</span>
      </button>

      <button class="menu-item" @click="handleAction('play-next')">
        <span class="menu-icon">⏭</span>
        <span>Reproducir siguiente</span>
      </button>

      <button class="menu-item" @click="handleAction('add-queue')">
        <span class="menu-icon">＋</span>
        <span>Agregar a la cola</span>
      </button>

      <div class="menu-separator"></div>

      <!-- Playlist Submenu / Trigger -->
      <button class="menu-item" @click="handleAction('add-playlist')">
        <span class="menu-icon">📑</span>
        <span>Agregar a Playlist...</span>
      </button>

      <button v-if="song?.folder" class="menu-item" @click="handleAction('open-folder')">
        <span class="menu-icon">📁</span>
        <span>Abrir carpeta ({{ song.folder }})</span>
      </button>

      <div class="menu-separator"></div>

      <button class="menu-item" @click="handleAction('edit-metadata')">
        <span class="menu-icon">✎</span>
        <span>Editar metadatos...</span>
      </button>

      <button class="menu-item" @click="handleAction('copy-info')">
        <span class="menu-icon">📋</span>
        <span>Copiar información</span>
      </button>

      <div class="menu-separator"></div>

      <button class="menu-item danger-action" @click="handleAction('delete')">
        <span class="menu-icon">🗑</span>
        <span>Eliminar archivo</span>
      </button>
    </div>
  </div>
</template>

<script setup>
import { computed, onMounted, onUnmounted } from 'vue'

const props = defineProps({
  show: Boolean,
  x: { type: Number, default: 0 },
  y: { type: Number, default: 0 },
  song: { type: Object, default: null }
})

const emit = defineEmits(['close', 'action'])

// Prevent menu from overflowing outside viewport
const clampedX = computed(() => {
  const menuWidth = 240
  if (props.x + menuWidth > window.innerWidth - 10) {
    return Math.max(10, window.innerWidth - menuWidth - 10)
  }
  return props.x
})

const clampedY = computed(() => {
  const menuHeight = 320
  if (props.y + menuHeight > window.innerHeight - 10) {
    return Math.max(10, window.innerHeight - menuHeight - 10)
  }
  return props.y
})

const handleAction = (action) => {
  emit('action', { action, song: props.song })
  emit('close')
}

const handleClickOutside = (e) => {
  if (props.show) {
    emit('close')
  }
}

onMounted(() => {
  window.addEventListener('click', handleClickOutside)
  window.addEventListener('contextmenu', handleClickOutside)
})

onUnmounted(() => {
  window.removeEventListener('click', handleClickOutside)
  window.removeEventListener('contextmenu', handleClickOutside)
})
</script>

<style scoped>
.retro-context-menu {
  position: fixed;
  background: #e4e4e4;
  border: 3px solid #000000;
  box-shadow: inset 1px 1px 0px #ffffff, inset -1px -1px 0px #666666, 6px 6px 0px #000000;
  z-index: 10000;
  min-width: 220px;
  max-width: 280px;
  padding: 4px;
  animation: popIn 0.1s cubic-bezier(0.1, 0.9, 0.2, 1);
  user-select: none;
}

@keyframes popIn {
  from {
    opacity: 0;
    transform: scale(0.95);
  }
  to {
    opacity: 1;
    transform: scale(1);
  }
}

.menu-header {
  padding: 6px 8px;
  background: #333333;
  color: #00f0ff;
  font-family: var(--font-pixel);
  font-size: 8px;
  border-bottom: 2px solid #000000;
  margin-bottom: 4px;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.menu-song-title {
  display: block;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.menu-items {
  display: flex;
  flex-direction: column;
  gap: 2px;
}

.menu-item {
  width: 100%;
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 6px 10px;
  background: transparent;
  border: 1px solid transparent;
  color: #1a1a1a;
  font-family: var(--font-mono);
  font-size: 11px;
  font-weight: 600;
  text-align: left;
  cursor: pointer;
  border-radius: 2px;
  transition: all 0.05s ease;
}

.menu-item:hover {
  background: #0088cc;
  color: #ffffff;
  border-color: #005588;
  box-shadow: inset 1px 1px 0px rgba(255, 255, 255, 0.5);
}

.menu-item.primary-action {
  font-weight: 700;
  color: #005588;
}

.menu-item.primary-action:hover {
  color: #ffffff;
}

.menu-item.danger-action {
  color: #c92a2a;
}

.menu-item.danger-action:hover {
  background: #c92a2a;
  color: #ffffff;
  border-color: #800000;
}

.menu-icon {
  font-size: 12px;
  width: 14px;
  text-align: center;
  flex-shrink: 0;
}

.menu-separator {
  height: 1px;
  background: #999999;
  border-bottom: 1px solid #ffffff;
  margin: 3px 2px;
}
</style>
