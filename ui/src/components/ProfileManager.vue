<template>
  <div class="profile-manager">
    <!-- FAB Button -->
    <button class="profile-fab" @click="toggleMenu" :class="{ active: isMenuOpen }">
      <svg v-if="!isMenuOpen" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
        <path d="M20 21v-2a4 4 0 0 0-4-4H8a4 4 0 0 0-4 4v2"></path>
        <circle cx="12" cy="7" r="4"></circle>
      </svg>
      <svg v-else width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
        <line x1="18" y1="6" x2="6" y2="18"></line>
        <line x1="6" y1="6" x2="18" y2="18"></line>
      </svg>
    </button>

    <!-- Dropdown Menu -->
    <transition name="slide-fade">
      <div v-if="isMenuOpen" class="profile-menu">
        <div class="profile-menu-header">
          <h3>Perfiles</h3>
          <span class="active-indicator">{{ activeProfile }}</span>
        </div>

        <!-- Profile List -->
        <div class="profile-list">
          <div 
            v-for="profile in profiles" 
            :key="profile"
            class="profile-item"
            :class="{ active: profile === activeProfile }"
          >
            <div v-if="editingProfile === profile" class="profile-edit">
              <input 
                v-model="newProfileName" 
                @keyup.enter="confirmRename(profile)"
                @keyup.esc="cancelEdit"
                ref="editInput"
                class="profile-input"
                placeholder="Nuevo nombre"
              />
              <button @click="confirmRename(profile)" class="btn-confirm">✓</button>
              <button @click="cancelEdit" class="btn-cancel">✕</button>
            </div>
            <div v-else class="profile-content">
              <button @click="switchProfile(profile)" class="profile-name">
                <span class="profile-icon">{{ profile === activeProfile ? '●' : '○' }}</span>
                {{ profile }}
              </button>
              <div class="profile-actions">
                <button 
                  v-if="profile !== 'Default'" 
                  @click="startRename(profile)" 
                  class="btn-action"
                  title="Renombrar"
                >
                  ✎
                </button>
                <button 
                  v-if="profile !== 'Default' && profile !== activeProfile" 
                  @click="confirmDelete(profile)" 
                  class="btn-action btn-delete"
                  title="Eliminar"
                >
                  🗑
                </button>
              </div>
            </div>
          </div>
        </div>

        <!-- Create New Profile -->
        <div class="profile-create">
          <div v-if="isCreating" class="profile-edit">
            <input 
              v-model="newProfileName" 
              @keyup.enter="createProfile"
              @keyup.esc="cancelCreate"
              ref="createInput"
              class="profile-input"
              placeholder="Nombre del perfil"
            />
            <button @click="createProfile" class="btn-confirm">✓</button>
            <button @click="cancelCreate" class="btn-cancel">✕</button>
          </div>
          <button v-else @click="startCreate" class="btn-create">
            <span class="plus-icon">+</span>
            Nuevo Perfil
          </button>
        </div>

        <!-- Error Message -->
        <div v-if="errorMessage" class="error-message">
          {{ errorMessage }}
        </div>
      </div>
    </transition>
  </div>
</template>

<script setup>
import { ref, onMounted, nextTick, watch } from 'vue'
import { ProfileService } from '../services/ProfileService'

const isMenuOpen = ref(false)
const profiles = ref([])
const activeProfile = ref('Default')
const isCreating = ref(false)
const editingProfile = ref(null)
const newProfileName = ref('')
const errorMessage = ref('')
const createInput = ref(null)
const editInput = ref(null)

const emit = defineEmits(['profile-changed'])

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

const toggleMenu = () => {
  isMenuOpen.value = !isMenuOpen.value
  if (!isMenuOpen.value) {
    cancelCreate()
    cancelEdit()
    errorMessage.value = ''
  }
}

const switchProfile = async (profile) => {
  if (profile === activeProfile.value) return
  
  try {
    await ProfileService.setActiveProfile(profile)
    activeProfile.value = profile
    errorMessage.value = ''
    emit('profile-changed', profile)
    
    // Reload the page to refresh all data
    setTimeout(() => {
      window.location.reload()
    }, 300)
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
.profile-manager {
  position: fixed;
  top: 20px;
  right: 20px;
  z-index: 1000;
}

.profile-fab {
  width: 56px;
  height: 56px;
  border-radius: 50%;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  border: none;
  color: white;
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
  box-shadow: 0 4px 12px rgba(102, 126, 234, 0.4);
  transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
}

.profile-fab:hover {
  transform: scale(1.05);
  box-shadow: 0 6px 20px rgba(102, 126, 234, 0.6);
}

.profile-fab.active {
  background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%);
}

.profile-menu {
  position: absolute;
  top: 70px;
  right: 0;
  width: 320px;
  background: rgba(255, 255, 255, 0.98);
  backdrop-filter: blur(10px);
  border-radius: 16px;
  box-shadow: 0 8px 32px rgba(0, 0, 0, 0.15);
  overflow: hidden;
  border: 1px solid rgba(255, 255, 255, 0.3);
}

.profile-menu-header {
  padding: 20px;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: white;
}

.profile-menu-header h3 {
  margin: 0 0 8px 0;
  font-size: 18px;
  font-weight: 600;
}

.active-indicator {
  font-size: 13px;
  opacity: 0.9;
  display: flex;
  align-items: center;
  gap: 6px;
}

.active-indicator::before {
  content: '●';
  font-size: 10px;
}

.profile-list {
  max-height: 300px;
  overflow-y: auto;
}

.profile-item {
  border-bottom: 1px solid rgba(0, 0, 0, 0.05);
  transition: background 0.2s;
}

.profile-item:hover {
  background: rgba(102, 126, 234, 0.05);
}

.profile-item.active {
  background: rgba(102, 126, 234, 0.1);
}

.profile-content {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 12px 20px;
}

.profile-name {
  flex: 1;
  background: none;
  border: none;
  text-align: left;
  font-size: 15px;
  cursor: pointer;
  color: #2d3748;
  display: flex;
  align-items: center;
  gap: 10px;
  padding: 0;
  transition: color 0.2s;
}

.profile-name:hover {
  color: #667eea;
}

.profile-icon {
  font-size: 12px;
  color: #667eea;
}

.profile-actions {
  display: flex;
  gap: 8px;
}

.btn-action {
  background: none;
  border: none;
  cursor: pointer;
  font-size: 16px;
  padding: 4px 8px;
  border-radius: 6px;
  transition: all 0.2s;
  opacity: 0.6;
}

.btn-action:hover {
  opacity: 1;
  background: rgba(102, 126, 234, 0.1);
}

.btn-delete:hover {
  background: rgba(245, 87, 108, 0.1);
}

.profile-edit {
  display: flex;
  gap: 8px;
  padding: 12px 20px;
  align-items: center;
}

.profile-input {
  flex: 1;
  padding: 8px 12px;
  border: 2px solid #667eea;
  border-radius: 8px;
  font-size: 14px;
  outline: none;
  transition: border-color 0.2s;
}

.profile-input:focus {
  border-color: #764ba2;
}

.btn-confirm,
.btn-cancel {
  width: 32px;
  height: 32px;
  border: none;
  border-radius: 6px;
  cursor: pointer;
  font-size: 16px;
  transition: all 0.2s;
}

.btn-confirm {
  background: #48bb78;
  color: white;
}

.btn-confirm:hover {
  background: #38a169;
}

.btn-cancel {
  background: #f56565;
  color: white;
}

.btn-cancel:hover {
  background: #e53e3e;
}

.profile-create {
  padding: 16px 20px;
  border-top: 1px solid rgba(0, 0, 0, 0.05);
}

.btn-create {
  width: 100%;
  padding: 12px;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: white;
  border: none;
  border-radius: 10px;
  font-size: 15px;
  font-weight: 600;
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 8px;
  transition: all 0.3s;
}

.btn-create:hover {
  transform: translateY(-2px);
  box-shadow: 0 4px 12px rgba(102, 126, 234, 0.3);
}

.plus-icon {
  font-size: 20px;
  font-weight: bold;
}

.error-message {
  padding: 12px 20px;
  background: #fed7d7;
  color: #c53030;
  font-size: 13px;
  border-top: 1px solid rgba(0, 0, 0, 0.05);
}

/* Scrollbar styling */
.profile-list::-webkit-scrollbar {
  width: 6px;
}

.profile-list::-webkit-scrollbar-track {
  background: rgba(0, 0, 0, 0.05);
}

.profile-list::-webkit-scrollbar-thumb {
  background: rgba(102, 126, 234, 0.3);
  border-radius: 3px;
}

.profile-list::-webkit-scrollbar-thumb:hover {
  background: rgba(102, 126, 234, 0.5);
}

/* Transitions */
.slide-fade-enter-active {
  transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
}

.slide-fade-leave-active {
  transition: all 0.2s cubic-bezier(0.4, 0, 1, 1);
}

.slide-fade-enter-from {
  transform: translateY(-10px);
  opacity: 0;
}

.slide-fade-leave-to {
  transform: translateY(-5px);
  opacity: 0;
}

/* Responsive */
@media (max-width: 768px) {
  .profile-manager {
    top: 10px;
    right: 10px;
  }

  .profile-fab {
    width: 48px;
    height: 48px;
  }

  .profile-menu {
    width: calc(100vw - 40px);
    right: -10px;
  }
}
</style>
