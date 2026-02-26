<template>
  <div class="overlay" @click.self="$emit('close')">
    <div class="panel">
      <div class="panel-header">
        <h2>Settings</h2>
        <button class="close-btn" @click="$emit('close')">✕</button>
      </div>

      <section>
        <label class="field-label">eBird API Key</label>
        <p class="hint">
          Get yours at
          <a href="https://ebird.org/api/keygen" target="_blank" rel="noopener">ebird.org/api/keygen</a>.
          Stored only in your browser.
        </p>
        <div class="row">
          <input
            v-model="localKey"
            type="password"
            placeholder="Paste your API key"
            class="input"
          />
          <button class="btn-primary" @click="saveKey">Save</button>
        </div>
        <p v-if="keySaved" class="success">Saved.</p>
      </section>

      <section>
        <label class="field-label">Life List CSV</label>
        <p class="hint">
          Download from
          <a href="https://ebird.org/downloadMyData" target="_blank" rel="noopener">ebird.org/downloadMyData</a>
          (My eBird → Download My Data). Parsed in your browser — never uploaded.
        </p>

        <div
          class="drop-zone"
          :class="{ 'drop-active': isDragging }"
          @dragover.prevent="isDragging = true"
          @dragleave="isDragging = false"
          @drop.prevent="onDrop"
          @click="fileInput?.click()"
        >
          <span v-if="!speciesCount">Drop CSV here or click to choose</span>
          <span v-else class="success">{{ speciesCount }} species loaded ✓</span>
        </div>
        <input ref="fileInput" type="file" accept=".csv" hidden @change="onFileChange" />

        <p v-if="parseError" class="error">{{ parseError }}</p>
        <button v-if="speciesCount" class="btn-danger" @click="clearList">Clear life list</button>
      </section>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { getApiKey, setApiKey, getLifeList, setLifeList, clearLifeList as storeClear, parseLifeListCsv } from '../store'

const emit = defineEmits<{ close: [] }>()

const localKey    = ref('')
const keySaved    = ref(false)
const speciesCount = ref(0)
const parseError  = ref('')
const isDragging  = ref(false)
const fileInput   = ref<HTMLInputElement | null>(null)

onMounted(() => {
  localKey.value = getApiKey()
  speciesCount.value = getLifeList()?.length ?? 0
})

function saveKey() {
  setApiKey(localKey.value)
  keySaved.value = true
  setTimeout(() => { keySaved.value = false }, 2000)
}

function onDrop(e: DragEvent) {
  isDragging.value = false
  const file = e.dataTransfer?.files[0]
  if (file) loadFile(file)
}

function onFileChange(e: Event) {
  const file = (e.target as HTMLInputElement).files?.[0]
  if (file) loadFile(file)
}

function loadFile(file: File) {
  parseError.value = ''
  const reader = new FileReader()
  reader.onload = () => {
    try {
      const list = parseLifeListCsv(reader.result as string)
      setLifeList(list)
      speciesCount.value = list.length
    } catch (err: any) {
      parseError.value = err.message
    }
  }
  reader.readAsText(file, 'utf-8')
}

function clearList() {
  storeClear()
  speciesCount.value = 0
}
</script>

<style scoped>
.overlay {
  position: fixed;
  inset: 0;
  background: rgba(0,0,0,.45);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 100;
}

.panel {
  background: var(--color-surface);
  border-radius: 10px;
  padding: 1.5rem 2rem 2rem;
  width: min(480px, 95vw);
  display: flex;
  flex-direction: column;
  gap: 1.5rem;
}

.panel-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.panel-header h2 { margin: 0; font-size: 1.2rem; }

.close-btn {
  background: none;
  border: none;
  font-size: 1.1rem;
  cursor: pointer;
  color: var(--color-text-muted);
  padding: 0.25rem;
}

section { display: flex; flex-direction: column; gap: .5rem; }

.field-label { font-weight: 600; font-size: .95rem; }

.hint { margin: 0; font-size: .8rem; color: var(--color-text-muted); }
.hint a { color: var(--color-accent); }

.row { display: flex; gap: .5rem; }

.input {
  flex: 1;
  padding: .5rem .75rem;
  border: 1px solid var(--color-border);
  border-radius: 6px;
  font-size: .9rem;
  background: var(--color-bg);
  color: var(--color-text);
}

.drop-zone {
  border: 2px dashed var(--color-border);
  border-radius: 8px;
  padding: 1.5rem;
  text-align: center;
  cursor: pointer;
  font-size: .9rem;
  color: var(--color-text-muted);
  transition: border-color .15s, background .15s;
}
.drop-zone:hover, .drop-active {
  border-color: var(--color-accent);
  background: color-mix(in srgb, var(--color-accent) 8%, transparent);
}

.btn-primary {
  padding: .5rem 1rem;
  background: var(--color-accent);
  color: #fff;
  border: none;
  border-radius: 6px;
  cursor: pointer;
  font-size: .9rem;
}
.btn-primary:hover { filter: brightness(1.1); }

.btn-danger {
  align-self: flex-start;
  padding: .35rem .8rem;
  background: none;
  border: 1px solid #e55;
  color: #e55;
  border-radius: 6px;
  cursor: pointer;
  font-size: .85rem;
}
.btn-danger:hover { background: #e5515110; }

.success { color: #3a3; font-size: .85rem; margin: 0; }
.error   { color: #e55; font-size: .85rem; margin: 0; }
</style>
