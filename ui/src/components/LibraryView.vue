<template>
  <div class="panel">
    <h2 style="margin-bottom: 16px;">Mis Carpetas</h2>
    <div class="folder-grid">
      <div v-for="folder in folders" :key="folder.name" class="cassette-folder" @click="$emit('open-folder', folder.name)">
        <div class="cassette-body" :style="folder.thumbnail ? { backgroundImage: `url(${getThumbnail(folder.thumbnail)})` } : {}">
            <div class="cassette-overlay"></div>
            <div class="cassette-label">
                <div v-if="!folder.thumbnail" class="cassette-art-placeholder">
                    <span>{{ folder.name.substring(0, 2).toUpperCase() }}</span>
                </div>
                <div class="cassette-title-strip">
                    <span class="cassette-title">{{ folder.name }}</span>
                </div>
            </div>
            <div class="cassette-bottom">
                <div class="cassette-holes">
                    <div class="hole left"></div>
                    <div class="hole right"></div>
                </div>
                <div class="cassette-trapezoid"></div>
            </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { onMounted, ref } from 'vue'

const folders = ref([])
const emit = defineEmits(['open-folder'])

const getThumbnail = (path) => {
    if (!path) return null
    if (path.startsWith('http')) return path
    return `http://localhost:5001${path}`
}

const loadLibrary = async () => {
    try {
        const response = await fetch('http://localhost:5001/api/library');
        folders.value = await response.json();
    } catch (error) {
        console.error(error);
    }
}

onMounted(() => {
    loadLibrary()
})
</script>

<style scoped>
.folder-grid {
    display: grid;
    grid-template-columns: repeat(auto-fill, minmax(140px, 1fr));
    gap: 20px;
    padding: 10px;
}

.cassette-folder {
    cursor: pointer;
    transition: transform 0.2s;
    width: 100%;
    aspect-ratio: 1.6; /* Cassette ratio */
    position: relative;
}

.cassette-folder:hover {
    transform: translateY(-5px) scale(1.02);
}

.cassette-body {
    width: 100%;
    height: 100%;
    background-color: #333;
    background-size: cover;
    background-position: center;
    border-radius: 8px;
    padding: 6px;
    display: flex;
    flex-direction: column;
    box-shadow: 
        inset 0 0 10px rgba(0,0,0,0.8),
        2px 4px 6px rgba(0,0,0,0.3);
    border: 1px solid #555;
    position: relative;
    overflow: hidden;
}

.cassette-overlay {
    position: absolute;
    top: 0;
    left: 0;
    width: 100%;
    height: 100%;
    background: rgba(0, 0, 0, 0.2); /* Slight darken */
    box-shadow: inset 0 0 20px rgba(0,0,0,0.8);
    pointer-events: none;
    z-index: 1;
}

/* Screws */
.cassette-body::before, .cassette-body::after {
    content: '';
    position: absolute;
    width: 6px;
    height: 6px;
    background: #111;
    border-radius: 50%;
    top: 6px;
    box-shadow: inset 1px 1px 1px rgba(255,255,255,0.2);
    z-index: 2;
}
.cassette-body::before { left: 6px; }
.cassette-body::after { right: 6px; }

.cassette-label {
    flex: 1;
    /* background: transparent; Removed paper background */
    border-radius: 4px;
    overflow: hidden;
    position: relative;
    display: flex;
    flex-direction: column;
    align-items: center;
    justify-content: center;
    padding: 2px;
    z-index: 2;
}

.cassette-art-placeholder {
    width: 100%;
    height: 100%;
    background: linear-gradient(135deg, #f6d365 0%, #fda085 100%);
    display: flex;
    align-items: center;
    justify-content: center;
    font-weight: bold;
    font-size: 24px;
    color: rgba(255,255,255,0.8);
    border-radius: 4px;
}

.cassette-title-strip {
    position: absolute;
    top: 10px;
    left: 0;
    width: 100%;
    background: rgba(255, 255, 255, 0.9);
    padding: 4px 8px;
    box-shadow: 0 2px 4px rgba(0,0,0,0.2);
    transform: rotate(-2deg);
    border: 1px solid #ccc;
    z-index: 2;
}

.cassette-title {
    display: block;
    font-family: 'Courier New', monospace;
    font-weight: bold;
    font-size: 11px;
    color: #000;
    white-space: nowrap;
    overflow: hidden;
    text-overflow: ellipsis;
    text-align: center;
    text-transform: uppercase;
    letter-spacing: -0.5px;
}

.cassette-bottom {
    height: 25%;
    position: relative;
    margin-top: 4px;
    z-index: 2;
}

.cassette-holes {
    position: absolute;
    top: 50%;
    left: 50%;
    transform: translate(-50%, -50%);
    width: 60%;
    display: flex;
    justify-content: space-between;
    z-index: 3;
}

.hole {
    width: 20px;
    height: 20px;
    background: #fff;
    border-radius: 50%;
    border: 4px solid #fff;
    box-shadow: inset 0 0 0 2px #000;
    position: relative;
}

.hole::after {
    content: '';
    position: absolute;
    top: 50%;
    left: 50%;
    transform: translate(-50%, -50%);
    width: 6px;
    height: 6px;
    background: transparent;
    border-left: 2px solid #000;
    border-right: 2px solid #000;
}

.cassette-trapezoid {
    position: absolute;
    bottom: 0;
    left: 50%;
    transform: translateX(-50%);
    width: 60%;
    height: 100%;
    background: #2a2a2a;
    clip-path: polygon(10% 0, 90% 0, 100% 100%, 0% 100%);
    z-index: 1;
    border-top: 1px solid #444;
}


</style>
