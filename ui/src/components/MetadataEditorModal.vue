<template>
  <div v-if="isOpen" class="retro-modal-overlay" @click="close">
    <div class="retro-modal-box metadata-modal" @click.stop>
      <div class="retro-modal-header">
        <h3>✎ EDITAR METADATOS</h3>
        <button class="btn-retro-icon" @click="close">✕</button>
      </div>

      <form @submit.prevent="saveMetadata">
        <div class="input-group">
          <label>Título de la Canción</label>
          <input 
            v-model="form.title" 
            type="text" 
            class="retro-input" 
            required 
            placeholder="Título de la canción" 
          />
        </div>

        <div class="input-group">
          <label>Artista / Intérprete</label>
          <input 
            v-model="form.artist" 
            type="text" 
            class="retro-input" 
            placeholder="Nombre del artista" 
          />
        </div>

        <div class="input-group">
          <label>Carpeta / Álbum</label>
          <input 
            v-model="form.new_folder" 
            type="text" 
            class="retro-input" 
            placeholder="Carpeta de destino" 
          />
        </div>

        <div class="file-details-preview">
          <div class="preview-row">
            <span class="preview-label">Archivo original:</span>
            <span class="preview-val">{{ song?.filename }}</span>
          </div>
          <div class="preview-row">
            <span class="preview-label">Ubicación actual:</span>
            <span class="preview-val">{{ song?.folder || 'Principal' }}</span>
          </div>
        </div>

        <div v-if="error" class="error-banner">
          ⚠️ {{ error }}
        </div>

        <div class="modal-footer-actions">
          <button type="button" class="btn-retro-secondary" @click="close" :disabled="saving">
            Cancelar
          </button>
          <button type="submit" class="btn-retro-primary" :disabled="saving">
            {{ saving ? 'Guardando...' : 'Guardar Cambios' }} ✓
          </button>
        </div>
      </form>
    </div>
  </div>
</template>

<script setup>
import { ref, watch } from 'vue'
import { LibraryService } from '../services/LibraryService'

const props = defineProps({
  isOpen: Boolean,
  song: Object
})

const emit = defineEmits(['close', 'saved'])

const form = ref({
  title: '',
  artist: '',
  new_folder: ''
})

const saving = ref(false)
const error = ref('')

watch(() => props.song, (s) => {
  if (s) {
    form.value.title = s.title || ''
    form.value.artist = s.uploader && s.uploader !== 'Desconocido' ? s.uploader : ''
    form.value.new_folder = s.folder || ''
    error.value = ''
  }
}, { immediate: true })

const saveMetadata = async () => {
  if (!props.song) return
  saving.value = true
  error.value = ''

  try {
    const updated = await LibraryService.editMetadata({
      folder: props.song.folder,
      old_filename: props.song.filename,
      title: form.value.title,
      artist: form.value.artist,
      new_folder: form.value.new_folder
    })

    emit('saved', updated)
    close()
  } catch (err) {
    error.value = err.message || 'Error al guardar metadatos'
  } finally {
    saving.value = false
  }
}

const close = () => {
  emit('close')
}
</script>

<style scoped>
.metadata-modal {
  max-width: 480px;
}

.retro-input {
  width: 100%;
  padding: 8px 12px;
  background: #ffffff;
  border: 2px solid #000000;
  font-family: var(--font-mono);
  font-size: 13px;
  box-shadow: inset 1px 1px 0px #666666;
  outline: none;
}

.retro-input:focus {
  border-color: #0088cc;
  box-shadow: inset 2px 2px 0px #005588, 0 0 0 2px rgba(0, 136, 204, 0.3);
}

.file-details-preview {
  background: #d4d4d4;
  border: 1px solid #999999;
  padding: 10px;
  margin: 12px 0;
  font-family: var(--font-mono);
  font-size: 11px;
}

.preview-row {
  display: flex;
  justify-content: space-between;
  margin-bottom: 4px;
}

.preview-label {
  color: #555555;
  font-weight: 600;
}

.preview-val {
  color: #1a1a1a;
  word-break: break-all;
  text-align: right;
}

.error-banner {
  background: #fee2e2;
  color: #b91c1c;
  border: 1px solid #dc2626;
  padding: 8px;
  font-family: var(--font-mono);
  font-size: 11px;
  margin-bottom: 12px;
}

.modal-footer-actions {
  display: flex;
  justify-content: flex-end;
  gap: 10px;
  margin-top: 18px;
  padding-top: 12px;
  border-top: 1px solid #cccccc;
}
</style>
