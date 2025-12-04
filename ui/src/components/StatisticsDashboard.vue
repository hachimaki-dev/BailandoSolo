<template>
  <div class="stats-dashboard-overlay" @click.self="$emit('close')">
    <div class="stats-dashboard">
      <div class="stats-header">
        <h2><span class="retro-text">PULPERIA</span> STATISTICS</h2>
        <button class="close-btn" @click="$emit('close')">×</button>
      </div>

      <div v-if="loading" class="loading">Loading Data...</div>
      <div v-else-if="error" class="error-message">{{ error }}</div>
      
      <div v-else class="stats-content">
        <!-- Top Section: Highlights -->
        <div class="highlights-grid">
          
          <!-- Most Played -->
          <div class="stat-card gold-card" v-if="stats.most_played">
            <div class="card-icon">🏆</div>
            <div class="card-label">MOST PLAYED</div>
            <div class="card-value">{{ stats.most_played.title }}</div>
            <div class="card-sub">{{ stats.most_played.play_count }} Plays</div>
          </div>

          <!-- Total Time -->
          <div class="stat-card neon-card">
            <div class="card-icon">⏱️</div>
            <div class="card-label">TOTAL LISTENING</div>
            <div class="card-value digital-clock">{{ formatTime(stats.total_time_global) }}</div>
          </div>

          <!-- Total Plays -->
          <div class="stat-card retro-card">
            <div class="card-icon">💿</div>
            <div class="card-label">TOTAL SPINS</div>
            <div class="card-value">{{ stats.total_plays }}</div>
          </div>
        </div>

        <!-- Middle Section: Lists -->
        <div class="lists-grid">
            <div class="list-column">
                <h3>Least Played</h3>
                <div class="mini-list">
                    <div v-if="stats.least_played" class="list-item">
                        <span class="item-name">{{ stats.least_played.title }}</span>
                        <span class="item-count">{{ stats.least_played.play_count }}</span>
                    </div>
                    <div v-else class="empty-state">No data yet</div>
                </div>
            </div>

            <div class="list-column">
                <h3>The Vault (Never Played)</h3>
                <div class="mini-list scrollable">
                    <div v-for="song in stats.never_played" :key="song" class="list-item fade">
                        <span class="item-name">{{ song }}</span>
                    </div>
                    <div v-if="stats.never_played.length === 0" class="empty-state">You've heard it all!</div>
                </div>
            </div>
        </div>

      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { StatsService } from '../services/StatsService'

const loading = ref(true)
const stats = ref({})
const error = ref(null)

onMounted(async () => {
    loading.value = true
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
})

const formatTime = (seconds) => {
    if (!seconds) return "00:00:00"
    const h = Math.floor(seconds / 3600)
    const m = Math.floor((seconds % 3600) / 60)
    const s = Math.floor(seconds % 60)
    return `${h.toString().padStart(2, '0')}:${m.toString().padStart(2, '0')}:${s.toString().padStart(2, '0')}`
}
</script>

<style scoped>
.stats-dashboard-overlay {
    position: fixed;
    top: 0;
    left: 0;
    width: 100vw;
    height: 100vh;
    background: rgba(0, 0, 0, 0.85);
    backdrop-filter: blur(5px);
    z-index: 2000;
    display: flex;
    justify-content: center;
    align-items: center;
    animation: fadeIn 0.3s ease;
}

.stats-dashboard {
    width: 90%;
    max-width: 800px;
    height: 80vh;
    background: linear-gradient(135deg, #1a1a1a 0%, #2d2d2d 100%);
    border: 2px solid #444;
    border-radius: 20px;
    box-shadow: 0 0 30px rgba(0, 255, 255, 0.1);
    display: flex;
    flex-direction: column;
    overflow: hidden;
    color: #fff;
    font-family: 'Inter', sans-serif;
}

.stats-header {
    padding: 20px;
    border-bottom: 1px solid #444;
    display: flex;
    justify-content: space-between;
    align-items: center;
    background: rgba(0,0,0,0.2);
}

.retro-text {
    background: linear-gradient(to right, #ff00cc, #3333ff);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    font-weight: 900;
    letter-spacing: 2px;
}

.close-btn {
    background: none;
    border: none;
    color: #fff;
    font-size: 2rem;
    cursor: pointer;
    opacity: 0.7;
    transition: opacity 0.2s;
}

.close-btn:hover {
    opacity: 1;
}

.loading, .error-message {
    padding: 40px;
    text-align: center;
    font-size: 1.2rem;
}

.error-message {
    color: #ff6b6b;
}

.stats-content {
    padding: 30px;
    overflow-y: auto;
    flex: 1;
}

.highlights-grid {
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
    gap: 20px;
    margin-bottom: 40px;
}

.stat-card {
    background: rgba(255,255,255,0.05);
    padding: 20px;
    border-radius: 15px;
    text-align: center;
    transition: transform 0.2s;
    border: 1px solid rgba(255,255,255,0.1);
}

.stat-card:hover {
    transform: translateY(-5px);
}

.gold-card {
    background: linear-gradient(135deg, rgba(255, 215, 0, 0.1) 0%, rgba(255, 215, 0, 0.05) 100%);
    border-color: rgba(255, 215, 0, 0.3);
}

.neon-card {
    background: linear-gradient(135deg, rgba(0, 255, 255, 0.1) 0%, rgba(0, 255, 255, 0.05) 100%);
    border-color: rgba(0, 255, 255, 0.3);
}

.retro-card {
    background: linear-gradient(135deg, rgba(255, 0, 204, 0.1) 0%, rgba(255, 0, 204, 0.05) 100%);
    border-color: rgba(255, 0, 204, 0.3);
}

.card-icon {
    font-size: 2.5rem;
    margin-bottom: 10px;
}

.card-label {
    font-size: 0.8rem;
    text-transform: uppercase;
    letter-spacing: 1px;
    opacity: 0.7;
    margin-bottom: 5px;
}

.card-value {
    font-size: 1.2rem;
    font-weight: bold;
    word-break: break-word;
}

.digital-clock {
    font-family: 'Courier New', monospace;
    letter-spacing: 2px;
    font-weight: bold;
}

.lists-grid {
    display: grid;
    grid-template-columns: 1fr 1fr;
    gap: 30px;
}

.list-column h3 {
    margin-bottom: 15px;
    font-size: 1.1rem;
    opacity: 0.8;
    border-bottom: 2px solid #444;
    padding-bottom: 5px;
    display: inline-block;
}

.mini-list {
    background: rgba(0,0,0,0.2);
    border-radius: 10px;
    padding: 10px;
}

.scrollable {
    max-height: 200px;
    overflow-y: auto;
}

.list-item {
    padding: 8px;
    border-bottom: 1px solid rgba(255,255,255,0.05);
    display: flex;
    justify-content: space-between;
    font-size: 0.9rem;
}

.list-item:last-child {
    border-bottom: none;
}

.fade {
    opacity: 0.6;
}

@keyframes fadeIn {
    from { opacity: 0; }
    to { opacity: 1; }
}
</style>
