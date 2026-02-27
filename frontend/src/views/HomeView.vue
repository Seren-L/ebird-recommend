<template>
  <main class="main">
    <!-- Setup prompt -->
    <div v-if="!isReady" class="setup-prompt card">
      <h2>Get started</h2>
      <p>Open <strong>Settings</strong> (top right) to:</p>
      <ol>
        <li>Paste your <a href="https://ebird.org/api/keygen" target="_blank" rel="noopener">eBird API key</a></li>
        <li>Upload your life list CSV from <a href="https://ebird.org/downloadMyData" target="_blank" rel="noopener">ebird.org/downloadMyData</a></li>
      </ol>
    </div>

    <!-- Main interface -->
    <template v-else>
      <div class="card">
        <h2 class="section-title">Find birds near me</h2>
        <RecommendForm :loading="loading" @submit="onSubmit" />
      </div>

      <div v-if="error" class="card error-card">
        <strong>Error:</strong> {{ error }}
      </div>

      <div v-if="results.length" class="card">
        <ResultsTable :results="results" />
      </div>

      <div v-else-if="submitted && !loading" class="card">
        <p class="empty">No recommendations found. Try a wider radius or more days.</p>
      </div>
    </template>
  </main>
</template>

<script setup lang="ts">
import { ref, computed } from 'vue'
import RecommendForm from '../components/RecommendForm.vue'
import ResultsTable  from '../components/ResultsTable.vue'
import { fetchRecommendations } from '../api'
import { getApiKey, getLifeList } from '../store'
import type { Recommendation, RecommendRequest } from '../types'

const loading   = ref(false)
const error     = ref('')
const submitted = ref(false)
const results   = ref<Recommendation[]>([])

const apiKey   = ref(getApiKey())
const lifeList = ref(getLifeList())
const isReady  = computed(() => !!apiKey.value && !!lifeList.value?.length)

// Re-read from storage when settings change (App.vue emits settingsChanged)
window.addEventListener('settings-changed', () => {
  apiKey.value   = getApiKey()
  lifeList.value = getLifeList()
})

async function onSubmit(req: RecommendRequest) {
  if (!isReady.value) return

  error.value     = ''
  loading.value   = true
  submitted.value = true
  results.value   = []

  try {
    req.life_list = lifeList.value!
    results.value = await fetchRecommendations(apiKey.value, req)
  } catch (err: any) {
    error.value = err.message
  } finally {
    loading.value = false
  }
}
</script>

<style scoped>
.main {
  flex: 1;
  max-width: 860px;
  width: 100%;
  margin: 0 auto;
  padding: 1.5rem 1rem 3rem;
  display: flex;
  flex-direction: column;
  gap: 1.25rem;
}

.card {
  background: var(--color-surface);
  border: 1px solid var(--color-border);
  border-radius: 10px;
  padding: 1.5rem;
}

.section-title {
  margin: 0 0 1rem;
  font-size: 1.05rem;
  font-weight: 700;
}

.setup-prompt h2 { margin: 0 0 .75rem; }
.setup-prompt ol { margin: .5rem 0 0; padding-left: 1.25rem; line-height: 1.9; }
.setup-prompt a  { color: var(--color-accent); }

.error-card { border-color: #f99; background: #fff5f5; color: #c00; }

.empty { color: var(--color-text-muted); margin: 0; font-size: .95rem; }
</style>
