<template>
  <div v-if="isOpen" class="retro-modal-overlay" @click="$emit('close')">
    <div class="retro-modal-box profile-modal-box" @click.stop>
      <div class="retro-modal-header">
        <div class="header-title-left">
          <span class="led-dot led-blue"></span>
          <h3>👤 PERFILES DE USUARIO</h3>
        </div>
        <button class="btn-retro-icon btn-close-modal" @click="$emit('close')" title="Cerrar (Esc)">✕</button>
      </div>

      <div class="current-profile-callout">
        <span>Perfil Activo:</span>
        <strong class="active-name">{{ activeProfile }}</strong>
      </div>

      <!-- Profile List -->
      <div class="profile-cards-list">
        <div 
          v-for="profile in profiles" 
          :key="profile"
          class="profile-row-item"
          :class="{ active: profile === activeProfile }"
        >
          <!-- Editing Name -->
          <div v-if="editingProfile === profile" class="profile-edit-inline">
            <input 
              v-model="newProfileName" 
              @keyup.enter="confirmRename(profile)"
              @keyup.esc="cancelEdit"
              ref="editInput"
              class="retro-input"
              placeholder="Nuevo nombre"
            />
            <button @click="confirmRename(profile)" class="btn-retro-primary btn-sm">✓</button>
            <button @click="cancelEdit" class="btn-retro-secondary btn-sm">✕</button>
          </div>

          <!-- Normal Item -->
          <div v-else class="profile-content-inline">
            <button @click="switchProfile(profile)" class="profile-select-btn">
              <span class="status-bullet">{{ profile === activeProfile ? '●' : '○' }}</span>
              <span class="name-text">{{ profile }}</span>
              <span v-if="profile === activeProfile" class="badge-retro success pixel">ACTIVO</span>
            </button>

            <div class="profile-actions-btns">
              <button 
                v-if="profile !== 'Default'" 
                @click.stop="startRename(profile)" 
                class="btn-retro-icon btn-sm"
                title="Renombrar"
              >
                ✎
              </button>
              <button 
                v-if="profile !== 'Default' && profile !== activeProfile" 
                @click.stop="confirmDelete(profile)" 
                class="btn-retro-icon btn-sm danger-text"
                title="Eliminar perfil"
              >
                🗑
              </button>
            </div>
          </div>
        </div>
      </div>

      <!-- Create New Profile -->
      <div class="create-section">
        <div v-if="isCreating" class="create-form-inline">
          <input 
            v-model="newProfileName" 
            @keyup.enter="createProfile"
            @keyup.esc="cancelCreate"
            ref="createInput"
            class="retro-input"
            placeholder="Nombre del nuevo perfil..."
          />
          <button @click="createProfile" class="btn-retro-primary btn-sm">Crear ✓</button>
          <button @click="cancelCreate" class="btn-retro-secondary btn-sm">✕</button>
        </div>
        <button v-else @click="startCreate" class="btn-retro-secondary btn-full">
          ＋ Nuevo Perfil
        </button>
      </div>

      <div v-if="errorMessage" class="error-pill">
        ⚠️ {{ errorMessage }}
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted, nextTick } from 'vue'
import { ProfileService } from '../services/ProfileService'

defineProps({
  isOpen: Boolean
})

const emit = defineEmits(['close', 'profile-changed'])

const profiles = ref([])
const activeProfile = ref('Default')
const isCreating = ref(false)
const editingProfile = ref(null)
const newProfileName = ref('')
const errorMessage = ref('')
const createInput = ref(null)
const editInput = ref(null)

onMounted(async () => {
  await loadProfiles()
})

const loadProfiles = async () => {
  try {
    const data = await ProfileService.getProfiles()
    profiles.value = data.profiles || []
    activeProfile.value = data.active || 'Default'
  } catch (error) {
    console.error('Error loading profiles:', error)
    errorMessage.value = 'Error al cargar perfiles'
  }
}

const switchProfile = async (profile) => {
  if (profile === activeProfile.value) return
  
  try {
    await ProfileService.setActiveProfile(profile)
    activeProfile.value = profile
    errorMessage.value = ''
    emit('profile-changed', profile)
    
    setTimeout(() => {
      window.location.reload()
    }, 200)
  } catch (error) {
    console.error('Error switching profile:', error)
    errorMessage.value = 'Error al cambiar perfil'
  }
}

const startCreate = () => {
  isCreating.value = true
  newProfileName.value = ''
  errorMessage.value = ''
  nextTick(() => {
    createInput.value?.focus()
  })
}

const cancelCreate = () => {
  isCreating.value = false
  newProfileName.value = ''
  errorMessage.value = ''
}

const createProfile = async () => {
  const name = newProfileName.value.trim()
  if (!name) {
    errorMessage.value = 'El nombre no puede estar vacío'
    return
  }

  try {
    const result = await ProfileService.createProfile(name)
    if (result.error) {
      errorMessage.value = result.error
      return
    }
    
    await loadProfiles()
    cancelCreate()
    errorMessage.value = ''
  } catch (error) {
    console.error('Error creating profile:', error)
    errorMessage.value = 'Error al crear perfil'
  }
}

const startRename = (profile) => {
  editingProfile.value = profile
  newProfileName.value = profile
  errorMessage.value = ''
  nextTick(() => {
    editInput.value?.[0]?.focus()
  })
}

const cancelEdit = () => {
  editingProfile.value = null
  newProfileName.value = ''
  errorMessage.value = ''
}

const confirmRename = async (oldName) => {
  const newName = newProfileName.value.trim()
  if (!newName) {
    errorMessage.value = 'El nombre no puede estar vacío'
    return
  }

  if (newName === oldName) {
    cancelEdit()
    return
  }

  try {
    const result = await ProfileService.renameProfile(oldName, newName)
    if (result.error) {
      errorMessage.value = result.error
      return
    }
    
    await loadProfiles()
    cancelEdit()
    errorMessage.value = ''
  } catch (error) {
    console.error('Error renaming profile:', error)
    errorMessage.value = 'Error al renombrar perfil'
  }
}

const confirmDelete = async (profile) => {
  if (!confirm(`¿Estás seguro de eliminar el perfil "${profile}"? Esta acción no se puede deshacer.`)) {
    return
  }

  try {
    const result = await ProfileService.deleteProfile(profile)
    if (result.error) {
      errorMessage.value = result.error
      return
    }
    
    await loadProfiles()
    errorMessage.value = ''
  } catch (error) {
    console.error('Error deleting profile:', error)
    errorMessage.value = 'Error al eliminar perfil'
  }
}
</script>

<style scoped>
.profile-modal-box {
  max-width: 480px;
  width: 95%;
}

.header-title-left {
  display: flex;
  align-items: center;
  gap: 8px;
}

.current-profile-callout {
  display: flex;
  justify-content: space-between;
  align-items: center;
  background: #ffffff;
  border: 2px solid #000000;
  padding: 8px 12px;
  margin-bottom: 12px;
  font-family: var(--font-mono);
  font-size: 12px;
}

.active-name {
  color: #0077b6;
  font-weight: bold;
}

.profile-cards-list {
  max-height: 240px;
  overflow-y: auto;
  margin-bottom: 14px;
}

.profile-row-item {
  background: #f0f0f0;
  border: 2px solid #000000;
  margin-bottom: 6px;
  box-shadow: 1px 1px 0px #000000;
}

.profile-row-item.active {
  background: #e0f2fe;
  border-color: #0088cc;
}

.profile-content-inline {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 8px 12px;
}

.profile-select-btn {
  display: flex;
  align-items: center;
  gap: 8px;
  background: none;
  border: none;
  cursor: pointer;
  font-family: var(--font-mono);
  font-size: 13px;
  font-weight: 700;
  color: #1a1a1a;
  text-align: left;
  flex: 1;
}

.status-bullet {
  color: #0088cc;
  font-size: 14px;
}

.profile-actions-btns {
  display: flex;
  gap: 4px;
}

.profile-edit-inline, .create-form-inline {
  display: flex;
  align-items: center;
  gap: 6px;
  padding: 8px;
}

.create-section {
  margin-top: 10px;
}

.btn-full {
  width: 100%;
  padding: 10px;
  font-size: 10px;
}

.btn-sm {
  padding: 4px 8px;
  font-size: 9px;
  height: 32px;
}

.danger-text {
  color: #c92a2a;
}

.error-pill {
  background: #fee2e2;
  color: #b91c1c;
  border: 1px solid #dc2626;
  padding: 6px 10px;
  margin-top: 10px;
  font-family: var(--font-mono);
  font-size: 11px;
}
</style>
