<template>
  <div class="app">
    <header class="header">
      <div class="header-inner">
        <RouterLink to="/" class="logo">🦜 eBird Recommender</RouterLink>
        <button class="settings-btn" @click="showSettings = true" title="Settings">⚙️</button>
      </div>
    </header>

    <RouterView />

    <SettingsPanel v-if="showSettings" @close="onSettingsClose" />
  </div>
</template>

<script setup lang="ts">
import { ref } from 'vue'
import SettingsPanel from './components/SettingsPanel.vue'

const showSettings = ref(false)

function onSettingsClose() {
  showSettings.value = false
  window.dispatchEvent(new Event('settings-changed'))
}
</script>

<style scoped>
.app {
  min-height: 100vh;
  display: flex;
  flex-direction: column;
}

.header {
  background: var(--color-surface);
  border-bottom: 1px solid var(--color-border);
  position: sticky;
  top: 0;
  z-index: 10;
}
.header-inner {
  max-width: 960px;
  margin: 0 auto;
  padding: .75rem 1rem;
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.logo {
  font-size: 1.1rem;
  font-weight: 700;
  color: inherit;
  text-decoration: none;
}
.logo:hover { opacity: .8; }

.settings-btn {
  background: none;
  border: none;
  font-size: 1.3rem;
  cursor: pointer;
  padding: .25rem;
  border-radius: 6px;
}
.settings-btn:hover { background: var(--color-border); }
</style>
