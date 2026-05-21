<template>
  <header>
    <div class="logo">
      <div class="logo-icon">♪</div>
      <h1>Bailando Solo</h1>
    </div>
    <nav>
      <button :class="{ active: currentView === 'downloader' }" @click="$emit('navigate', 'downloader')">Descargar</button>
      <button :class="{ active: currentView === 'library' || currentView === 'folder' }" @click="$emit('navigate', 'library')">Biblioteca</button>
    </nav>
  </header>
</template>

<script setup>
defineProps(['currentView'])
defineEmits(['navigate'])
</script>
