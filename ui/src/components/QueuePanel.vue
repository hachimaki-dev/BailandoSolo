<template>
  <div class="queue-panel" :class="{ open: isOpen }">
    <div class="queue-header">
        <h3>Cola de Reproducción</h3>
        <button class="control-icon-btn" @click="$emit('close')">✕</button>
    </div>
    <div class="queue-list">
        <div v-if="queue.length === 0" style="padding: 20px; text-align: center; color: #999;">Cola vacía</div>
        <div v-else v-for="(song, index) in queue" :key="index" class="queue-item" @click="$emit('play-item', index)">
            <div style="flex: 1; overflow: hidden; white-space: nowrap; text-overflow: ellipsis;">
                <div style="font-weight: bold; font-size: 14px;">{{ song.title }}</div>
                <div style="font-size: 12px; color: #666;">{{ song.filename }}</div>
            </div>
            <button class="remove-btn" style="background: none; border: none; color: #999; cursor: pointer;" @click.stop="$emit('remove-item', index)">✕</button>
        </div>
    </div>
  </div>
</template>

<script setup>
defineProps(['queue', 'isOpen'])
defineEmits(['close', 'remove-item', 'play-item'])
</script>
