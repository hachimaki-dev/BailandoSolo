<template>
  <div class="stats-panel" :class="{ open: isOpen }">
    <div class="stats-header">
      <h2>📊 ESTADÍSTICAS</h2>
      <button class="close-btn" @click="$emit('close')">×</button>
    </div>

    <div v-if="loading" class="loading">Cargando...</div>
    <div v-else-if="error" class="error-message">{{ error }}</div>
    
    <div v-else class="stats-content">
      
      <!-- Global Stats Cards -->
      <div class="global-stats">
        <div class="stat-badge">
          <div class="badge-icon">💿</div>
          <div class="badge-label">TOTAL SPINS</div>
          <div class="badge-value">{{ stats.total_plays || 0 }}</div>
        </div>
        <div class="stat-badge">
          <div class="badge-icon">⏱️</div>
          <div class="badge-label">TIEMPO TOTAL</div>
          <div class="badge-value">{{ formatTime(stats.total_time_global) }}</div>
        </div>
      </div>

      <!-- Library Exploration -->
      <div class="stats-section" v-if="stats.library_explored_percent !== undefined">
        <h3>📚 EXPLORACIÓN DE BIBLIOTECA</h3>
        <div class="exploration-bar">
          <div class="exploration-fill" :style="{ width: stats.library_explored_percent + '%' }"></div>
          <div class="exploration-text">
            {{ stats.unique_songs_played }} / {{ stats.total_songs }} canciones
            <span class="exploration-percent">({{ stats.library_explored_percent }}%)</span>
          </div>
        </div>
      </div>

      <!-- Achievements -->
      <div class="stats-section" v-if="stats.achievements && stats.achievements.length > 0">
        <h3>🏆 LOGROS DESBLOQUEADOS</h3>
        <div class="achievements-grid">
          <div v-for="achievement in stats.achievements" :key="achievement.id" class="achievement-badge">
            <div class="achievement-icon">{{ achievement.icon }}</div>
            <div class="achievement-title">{{ achievement.title }}</div>
            <div class="achievement-desc">{{ achievement.desc }}</div>
          </div>
        </div>
      </div>

      <!-- Top Folders -->
      <div class="stats-section" v-if="stats.top_folders && stats.top_folders.length > 0">
        <h3>📁 TOP CARPETAS</h3>
        <div class="folder-list">
          <div v-for="(folder, idx) in stats.top_folders" :key="folder.name" class="folder-item">
            <div class="folder-rank">{{ idx + 1 }}</div>
            <div class="folder-info">
              <div class="folder-name">{{ folder.name }}</div>
              <div class="folder-meta">
                {{ folder.play_count }} plays · {{ formatTime(folder.total_time) }}
              </div>
            </div>
            <div class="folder-badge">{{ folder.song_count }} 🎵</div>
          </div>
        </div>
      </div>

      <!-- Most Played -->
      <div class="stats-section" v-if="stats.most_played">
        <h3>🏆 MÁS REPRODUCIDA</h3>
        <div class="cartridge-container">
          <div class="stats-cartridge gold">
            <div class="cartridge-art">
              <img :src="getSongThumbnail(stats.most_played)" :alt="stats.most_played.title">
              <div class="cartridge-badge">
                <span>{{ stats.most_played.play_count }}</span>
                <small>plays</small>
              </div>
            </div>
            <div class="cartridge-title">{{ stats.most_played.title }}</div>
            <div class="cartridge-meta">
              <span>⏱️ {{ formatTime(stats.most_played.total_time) }}</span>
            </div>
          </div>
        </div>
      </div>

      <!-- Most Time -->
      <div class="stats-section" v-if="stats.most_time && stats.most_time.id !== stats.most_played?.id">
        <h3>🎧 MÁS ESCUCHADA</h3>
        <div class="cartridge-container">
          <div class="stats-cartridge platinum">
            <div class="cartridge-art">
              <img :src="getSongThumbnail(stats.most_time)" :alt="stats.most_time.title">
              <div class="cartridge-badge">
                <span>{{ formatTime(stats.most_time.total_time) }}</span>
              </div>
            </div>
            <div class="cartridge-title">{{ stats.most_time.title }}</div>
            <div class="cartridge-meta">
              <span>🔁 {{ stats.most_time.play_count }} plays</span>
            </div>
          </div>
        </div>
      </div>

      <!-- First & Last Played -->
      <div class="stats-section" v-if="stats.first_played || stats.last_played">
        <h3>⏰ CRONOLOGÍA</h3>
        <div class="timeline-grid">
          <div v-if="stats.first_played" class="timeline-item">
            <div class="timeline-label">Primera vez</div>
            <div class="timeline-song">{{ stats.first_played.title }}</div>
            <div class="timeline-date">{{ formatDate(stats.first_played.last_played) }}</div>
          </div>
          <div v-if="stats.last_played" class="timeline-item">
            <div class="timeline-label">Última vez</div>
            <div class="timeline-song">{{ stats.last_played.title }}</div>
            <div class="timeline-date">{{ formatDate(stats.last_played.last_played) }}</div>
          </div>
        </div>
      </div>

      <!-- Least Played -->
      <div class="stats-section" v-if="stats.least_played">
        <h3>💤 MENOS REPRODUCIDA</h3>
        <div class="cartridge-container">
          <div class="stats-cartridge dusty">
            <div class="cartridge-art">
              <img :src="getSongThumbnail(stats.least_played)" :alt="stats.least_played.title">
              <div class="cartridge-badge dusty-badge">
                <span>{{ stats.least_played.play_count }}</span>
                <small>plays</small>
              </div>
            </div>
            <div class="cartridge-title">{{ stats.least_played.title }}</div>
          </div>
        </div>
      </div>

      <!-- Never Played -->
      <div class="stats-section" v-if="stats.never_played && stats.never_played.length > 0">
        <h3>🔒 LA BÓVEDA ({{ stats.never_played.length }})</h3>
        <div class="vault-list">
          <div v-for="(song, idx) in stats.never_played.slice(0, 10)" :key="idx" class="vault-item">
            <div class="vault-icon">📦</div>
            <div class="vault-name">{{ song }}</div>
          </div>
          <div v-if="stats.never_played.length > 10" class="vault-more">
            +{{ stats.never_played.length - 10 }} más...
          </div>
        </div>
      </div>

      <div v-if="!stats.most_played && !stats.least_played" class="empty-state">
        <div class="empty-icon">🎵</div>
        <p>Aún no hay estadísticas</p>
        <small>Reproduce algunas canciones para ver tus stats</small>
      </div>

    </div>
  </div>
</template>

<script setup>
import { ref, onMounted, watch } from 'vue'
import { StatsService } from '../services/StatsService'

const props = defineProps({
  isOpen: {
    type: Boolean,
    default: false
  }
})

const loading = ref(true)
const stats = ref({})
const error = ref(null)

// Watch for panel opening to reload stats
watch(() => props.isOpen, (newVal) => {
  if (newVal) {
    loadStats()
  }
})

const loadStats = async () => {
  loading.value = true
  error.value = null
  try {
    const result = await StatsService.getStats()
    console.log('Stats loaded:', result)
    if (result) {
      stats.value = result
    } else {
      error.value = 'No se pudieron cargar las estadísticas'
    }
  } catch (e) {
    console.error('Error loading stats:', e)
    error.value = e.message
  } finally {
    loading.value = false
  }
}

onMounted(() => {
  if (props.isOpen) {
    loadStats()
  }
})

const getSongThumbnail = (song) => {
  // Try to extract folder and filename from the song ID
  // The ID is typically the filename
  const songId = song.id || song.title
  
  // Generate a deterministic cover based on title
  const hash = songId.split('').reduce((acc, char) => acc + char.charCodeAt(0), 0)
  const coverNum = (hash % 9) + 1
  return new URL(`../assets/styles/no_cover/${coverNum}.png`, import.meta.url).href
}

const formatTime = (seconds) => {
  if (!seconds) return "0:00"
  const h = Math.floor(seconds / 3600)
  const m = Math.floor((seconds % 3600) / 60)
  const s = Math.floor(seconds % 60)
  
  if (h > 0) {
    return `${h}:${m.toString().padStart(2, '0')}:${s.toString().padStart(2, '0')}`
  }
  return `${m}:${s.toString().padStart(2, '0')}`
}

const formatDate = (timestamp) => {
  if (!timestamp) return "Desconocido"
  const date = new Date(timestamp * 1000)
  const now = new Date()
  const diffMs = now - date
  const diffDays = Math.floor(diffMs / (1000 * 60 * 60 * 24))
  
  if (diffDays === 0) return "Hoy"
  if (diffDays === 1) return "Ayer"
  if (diffDays < 7) return `Hace ${diffDays} días`
  if (diffDays < 30) return `Hace ${Math.floor(diffDays / 7)} semanas`
  
  return date.toLocaleDateString('es-ES', { day: 'numeric', month: 'short', year: 'numeric' })
}
</script>

<style scoped>
.stats-panel {
  position: fixed;
  top: 0;
  right: -420px;
  width: 400px;
  height: 100vh;
  background: var(--bg-panel);
  box-shadow: -5px 0 20px var(--shadow-color);
  z-index: 2000;
  transition: right 0.3s cubic-bezier(0.4, 0, 0.2, 1);
  display: flex;
  flex-direction: column;
  border-left: var(--border-width) var(--border-style) var(--border-color);
  overflow: hidden;
}

.stats-panel.open {
  right: 0;
}

.stats-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 20px;
  border-bottom: var(--border-width) var(--border-style) var(--border-color);
  flex-shrink: 0;
}

.stats-header h2 {
  font-size: var(--text-base);
  margin: 0;
  text-transform: uppercase;
  letter-spacing: 1px;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

.close-btn {
  background: none;
  border: none;
  color: var(--text-main);
  font-size: 2rem;
  cursor: pointer;
  opacity: 0.7;
  transition: opacity 0.2s;
  padding: 0;
  line-height: 1;
  flex-shrink: 0;
  margin-left: 10px;
}

.close-btn:hover {
  opacity: 1;
}

.loading, .error-message {
  padding: 40px 20px;
  text-align: center;
  font-size: var(--text-base);
}

.error-message {
  color: var(--danger);
}

.stats-content {
  flex: 1;
  overflow-y: auto;
  overflow-x: hidden;
  padding: 20px;
}

.global-stats {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 10px;
  margin-bottom: 20px;
}

.stat-badge {
  background: var(--bg-alt);
  padding: 12px 8px;
  border-radius: var(--radius-md);
  text-align: center;
  border: var(--border-width) var(--border-style) var(--border-color);
  box-shadow: var(--shadow-sm);
  min-width: 0;
}

.badge-icon {
  font-size: 1.5rem;
  margin-bottom: 5px;
}

.badge-label {
  font-size: 9px;
  text-transform: uppercase;
  letter-spacing: 0.5px;
  opacity: 0.7;
  margin-bottom: 5px;
  font-weight: bold;
  line-height: 1.2;
}

.badge-value {
  font-size: var(--text-base);
  font-weight: bold;
  font-family: var(--font-mono);
  word-break: break-all;
}

.stats-section {
  margin-bottom: 20px;
}

.stats-section h3 {
  font-size: 11px;
  margin-bottom: 10px;
  text-transform: uppercase;
  letter-spacing: 1px;
  opacity: 0.8;
  font-weight: bold;
}

.cartridge-container {
  display: flex;
  justify-content: center;
}

.stats-cartridge {
  width: 130px;
  background: var(--bg-alt);
  border: var(--border-width) var(--border-style) var(--border-color);
  border-radius: var(--radius-md);
  overflow: hidden;
  box-shadow: var(--shadow-md);
  transition: transform 0.2s;
  position: relative;
}

.stats-cartridge:hover {
  transform: translateY(-3px);
}

.stats-cartridge.gold {
  border-color: #FFD700;
  box-shadow: 0 0 15px rgba(255, 215, 0, 0.3), var(--shadow-md);
}

.stats-cartridge.platinum {
  border-color: #00CED1;
  box-shadow: 0 0 15px rgba(0, 206, 209, 0.3), var(--shadow-md);
}

.stats-cartridge.dusty {
  opacity: 0.7;
  filter: grayscale(0.3);
}

.cartridge-art {
  width: 100%;
  height: 110px;
  background: #333;
  position: relative;
  overflow: hidden;
}

.cartridge-art img {
  width: 100%;
  height: 100%;
  object-fit: cover;
}

.cartridge-badge {
  position: absolute;
  top: 6px;
  right: 6px;
  background: rgba(0, 0, 0, 0.85);
  color: #FFD700;
  padding: 3px 6px;
  border-radius: 4px;
  font-weight: bold;
  font-size: 10px;
  display: flex;
  flex-direction: column;
  align-items: center;
  line-height: 1.2;
  border: 1px solid #FFD700;
}

.cartridge-badge small {
  font-size: 8px;
  opacity: 0.8;
}

.dusty-badge {
  background: rgba(100, 100, 100, 0.85);
  color: #999;
  border-color: #666;
}

.cartridge-title {
  padding: 8px 6px;
  font-size: 10px;
  font-weight: bold;
  text-align: center;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
  line-height: 1.3;
}

.cartridge-meta {
  padding: 0 6px 8px;
  font-size: 9px;
  text-align: center;
  opacity: 0.7;
}

.vault-list {
  background: var(--bg-alt);
  border: var(--border-width) var(--border-style) var(--border-color);
  border-radius: var(--radius-md);
  padding: 8px;
  max-height: 200px;
  overflow-y: auto;
}

.vault-item {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 6px;
  border-bottom: 1px solid var(--border-color);
  font-size: var(--text-sm);
  min-width: 0;
}

.vault-item:last-child {
  border-bottom: none;
}

.vault-icon {
  font-size: 1rem;
  opacity: 0.5;
  flex-shrink: 0;
}

.vault-name {
  flex: 1;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
  font-size: 10px;
  min-width: 0;
}

.vault-more {
  padding: 8px;
  text-align: center;
  font-size: 10px;
  opacity: 0.6;
  font-style: italic;
}

.empty-state {
  padding: 60px 20px;
  text-align: center;
  opacity: 0.6;
}

.empty-icon {
  font-size: 3rem;
  margin-bottom: 15px;
  opacity: 0.3;
}

.empty-state p {
  font-size: var(--text-base);
  margin-bottom: 5px;
}

.empty-state small {
  font-size: var(--text-sm);
  opacity: 0.7;
}

/* Exploration Bar */
.exploration-bar {
  position: relative;
  background: var(--bg-alt);
  border: var(--border-width) var(--border-style) var(--border-color);
  border-radius: var(--radius-md);
  height: 35px;
  overflow: hidden;
}

.exploration-fill {
  position: absolute;
  top: 0;
  left: 0;
  height: 100%;
  background: linear-gradient(90deg, #4CAF50, #8BC34A);
  transition: width 0.5s ease;
  box-shadow: inset 0 0 10px rgba(255, 255, 255, 0.2);
}

.exploration-text {
  position: relative;
  z-index: 1;
  display: flex;
  align-items: center;
  justify-content: center;
  height: 100%;
  font-size: 10px;
  font-weight: bold;
  text-shadow: 0 1px 2px rgba(0, 0, 0, 0.5);
  padding: 0 8px;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

.exploration-percent {
  margin-left: 5px;
  opacity: 0.8;
}

/* Achievements */
.achievements-grid {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: 8px;
}

.achievement-badge {
  background: var(--bg-alt);
  border: var(--border-width) var(--border-style) var(--border-color);
  border-radius: var(--radius-md);
  padding: 10px 6px;
  text-align: center;
  transition: transform 0.2s;
  box-shadow: var(--shadow-sm);
  min-width: 0;
}

.achievement-badge:hover {
  transform: translateY(-3px);
  box-shadow: var(--shadow-md);
}

.achievement-icon {
  font-size: 1.5rem;
  margin-bottom: 4px;
  animation: float 3s ease-in-out infinite;
}

@keyframes float {
  0%, 100% { transform: translateY(0); }
  50% { transform: translateY(-5px); }
}

.achievement-title {
  font-size: 9px;
  font-weight: bold;
  margin-bottom: 2px;
  line-height: 1.2;
  word-break: break-word;
}

.achievement-desc {
  font-size: 8px;
  opacity: 0.7;
}

/* Folder List */
.folder-list {
  background: var(--bg-alt);
  border: var(--border-width) var(--border-style) var(--border-color);
  border-radius: var(--radius-md);
  padding: 8px;
}

.folder-item {
  display: flex;
  align-items: center;
  gap: 10px;
  padding: 8px;
  border-bottom: 1px solid var(--border-color);
  transition: background 0.2s;
  min-width: 0;
}

.folder-item:last-child {
  border-bottom: none;
}

.folder-item:hover {
  background: rgba(255, 255, 255, 0.05);
}

.folder-rank {
  width: 24px;
  height: 24px;
  background: var(--primary);
  color: var(--text-inverse);
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  font-weight: bold;
  font-size: 11px;
  flex-shrink: 0;
}

.folder-info {
  flex: 1;
  min-width: 0;
}

.folder-name {
  font-size: 11px;
  font-weight: bold;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

.folder-meta {
  font-size: 9px;
  opacity: 0.7;
  margin-top: 2px;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

.folder-badge {
  background: rgba(255, 255, 255, 0.1);
  padding: 3px 6px;
  border-radius: 10px;
  font-size: 9px;
  font-weight: bold;
  white-space: nowrap;
  flex-shrink: 0;
}

/* Timeline */
.timeline-grid {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 8px;
}

.timeline-item {
  background: var(--bg-alt);
  border: var(--border-width) var(--border-style) var(--border-color);
  border-radius: var(--radius-md);
  padding: 10px 8px;
  text-align: center;
  min-width: 0;
}

.timeline-label {
  font-size: 9px;
  text-transform: uppercase;
  letter-spacing: 0.5px;
  opacity: 0.6;
  margin-bottom: 6px;
  font-weight: bold;
}

.timeline-song {
  font-size: 10px;
  font-weight: bold;
  margin-bottom: 4px;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

.timeline-date {
  font-size: 9px;
  opacity: 0.7;
  font-family: var(--font-mono);
}

/* Exploration Bar */
.exploration-bar {
  position: relative;
  background: var(--bg-alt);
  border: var(--border-width) var(--border-style) var(--border-color);
  border-radius: var(--radius-md);
  height: 40px;
  overflow: hidden;
}

.exploration-fill {
  position: absolute;
  top: 0;
  left: 0;
  height: 100%;
  background: linear-gradient(90deg, #4CAF50, #8BC34A);
  transition: width 0.5s ease;
  box-shadow: inset 0 0 10px rgba(255, 255, 255, 0.2);
}

.exploration-text {
  position: relative;
  z-index: 1;
  display: flex;
  align-items: center;
  justify-content: center;
  height: 100%;
  font-size: var(--text-sm);
  font-weight: bold;
  text-shadow: 0 1px 2px rgba(0, 0, 0, 0.5);
}

.exploration-percent {
  margin-left: 8px;
  opacity: 0.8;
}

/* Achievements */
.achievements-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(100px, 1fr));
  gap: 10px;
}

.achievement-badge {
  background: var(--bg-alt);
  border: var(--border-width) var(--border-style) var(--border-color);
  border-radius: var(--radius-md);
  padding: 12px 8px;
  text-align: center;
  transition: transform 0.2s;
  box-shadow: var(--shadow-sm);
}

.achievement-badge:hover {
  transform: translateY(-3px);
  box-shadow: var(--shadow-md);
}

.achievement-icon {
  font-size: 2rem;
  margin-bottom: 5px;
  animation: float 3s ease-in-out infinite;
}

@keyframes float {
  0%, 100% { transform: translateY(0); }
  50% { transform: translateY(-5px); }
}

.achievement-title {
  font-size: var(--text-xs);
  font-weight: bold;
  margin-bottom: 3px;
  line-height: 1.2;
}

.achievement-desc {
  font-size: 10px;
  opacity: 0.7;
}

/* Folder List */
.folder-list {
  background: var(--bg-alt);
  border: var(--border-width) var(--border-style) var(--border-color);
  border-radius: var(--radius-md);
  padding: 10px;
}

.folder-item {
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 10px;
  border-bottom: 1px solid var(--border-color);
  transition: background 0.2s;
}

.folder-item:last-child {
  border-bottom: none;
}

.folder-item:hover {
  background: rgba(255, 255, 255, 0.05);
}

.folder-rank {
  width: 28px;
  height: 28px;
  background: var(--primary);
  color: var(--text-inverse);
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  font-weight: bold;
  font-size: var(--text-sm);
  flex-shrink: 0;
}

.folder-info {
  flex: 1;
  min-width: 0;
}

.folder-name {
  font-size: var(--text-sm);
  font-weight: bold;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

.folder-meta {
  font-size: 10px;
  opacity: 0.7;
  margin-top: 2px;
}

.folder-badge {
  background: rgba(255, 255, 255, 0.1);
  padding: 4px 8px;
  border-radius: 12px;
  font-size: var(--text-xs);
  font-weight: bold;
  white-space: nowrap;
}

/* Timeline */
.timeline-grid {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 10px;
}

.timeline-item {
  background: var(--bg-alt);
  border: var(--border-width) var(--border-style) var(--border-color);
  border-radius: var(--radius-md);
  padding: 12px;
  text-align: center;
}

.timeline-label {
  font-size: var(--text-xs);
  text-transform: uppercase;
  letter-spacing: 1px;
  opacity: 0.6;
  margin-bottom: 8px;
  font-weight: bold;
}

.timeline-song {
  font-size: var(--text-sm);
  font-weight: bold;
  margin-bottom: 5px;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

.timeline-date {
  font-size: 10px;
  opacity: 0.7;
  font-family: var(--font-mono);
}

/* SNES Theme Overrides */
body[data-theme="snes"] .stats-panel {
  background: #e4e4e4;
  box-shadow: inset 3px 0 0 #fff, inset -3px 0 0 #7c7c7c, -6px 0 0 #000;
}

body[data-theme="snes"] .stat-badge {
  box-shadow: inset -2px -2px 0 #7c7c7c, inset 2px 2px 0 #fff, 3px 3px 0 #000;
}

body[data-theme="snes"] .stats-cartridge {
  box-shadow: inset -2px -2px 0 #7c7c7c, inset 2px 2px 0 #fff, 4px 4px 0 #000;
}

body[data-theme="snes"] .stats-cartridge.gold {
  box-shadow: inset -2px -2px 0 #c4a000, inset 2px 2px 0 #ffea5a, 4px 4px 0 #000, 0 0 10px rgba(255, 215, 0, 0.5);
}

body[data-theme="snes"] .stats-cartridge.platinum {
  box-shadow: inset -2px -2px 0 #0088aa, inset 2px 2px 0 #5aefff, 4px 4px 0 #000, 0 0 10px rgba(0, 206, 209, 0.5);
}

body[data-theme="snes"] .vault-list {
  box-shadow: inset 2px 2px 0 #7c7c7c;
}

body[data-theme="snes"] .exploration-bar {
  box-shadow: inset 2px 2px 0 #7c7c7c, 3px 3px 0 #000;
}

body[data-theme="snes"] .exploration-fill {
  background: linear-gradient(90deg, #5a5aff, #8a8aff);
}

body[data-theme="snes"] .achievement-badge {
  box-shadow: inset -2px -2px 0 #7c7c7c, inset 2px 2px 0 #fff, 3px 3px 0 #000;
}

body[data-theme="snes"] .folder-list {
  box-shadow: inset 2px 2px 0 #7c7c7c, 3px 3px 0 #000;
}

body[data-theme="snes"] .folder-rank {
  background: #5a5aff;
  box-shadow: inset -1px -1px 0 #2a2aaf, inset 1px 1px 0 #8a8aff, 2px 2px 0 #000;
}

body[data-theme="snes"] .timeline-item {
  box-shadow: inset -2px -2px 0 #7c7c7c, inset 2px 2px 0 #fff, 3px 3px 0 #000;
}
</style>
