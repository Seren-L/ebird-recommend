<template>
  <form class="form" @submit.prevent="submit">
    <div class="fields">
      <div class="field-group">
        <label>Latitude</label>
        <input v-model.number="lat" type="number" step="any" required placeholder="-33.8623" class="input" />
      </div>
      <div class="field-group">
        <label>Longitude</label>
        <input v-model.number="lng" type="number" step="any" required placeholder="151.2077" class="input" />
      </div>
      <button type="button" class="btn-locate" @click="geolocate" title="Use my location">
        📍
      </button>
    </div>

    <div class="fields">
      <div class="field-group">
        <label>Radius (km)</label>
        <input v-model.number="radius" type="number" min="1" max="500" class="input" />
      </div>
      <div class="field-group">
        <label>Days back</label>
        <input v-model.number="days" type="number" min="1" max="30" class="input" />
      </div>
      <div class="field-group">
        <label>Max results</label>
        <input v-model.number="top" type="number" min="1" max="100" class="input" />
      </div>
    </div>

    <div class="fields">
      <div class="field-group">
        <label>New species (lifer)</label>
        <select v-model="lifer" class="input">
          <option value="all">All</option>
          <option value="yes">Lifers only</option>
          <option value="no">Seen before only</option>
        </select>
      </div>
      <div class="field-group">
        <label>eBird Notable</label>
        <select v-model="notable" class="input">
          <option value="all">All</option>
          <option value="yes">Notable only</option>
          <option value="no">Non-notable only</option>
        </select>
      </div>
    </div>

    <p v-if="geoError" class="error">{{ geoError }}</p>

    <button type="submit" class="btn-submit" :disabled="loading">
      <span v-if="loading">Fetching…</span>
      <span v-else>Find birds</span>
    </button>
  </form>
</template>

<script setup lang="ts">
import { ref } from 'vue'
import type { FilterMode, RecommendRequest } from '../types'

const emit = defineEmits<{
  submit: [req: RecommendRequest]
}>()

const props = defineProps<{ loading: boolean }>()

const lat     = ref<number | ''>('')
const lng     = ref<number | ''>('')
const radius  = ref(50)
const days    = ref(14)
const top     = ref(20)
const lifer   = ref<FilterMode>('all')
const notable = ref<FilterMode>('all')
const geoError = ref('')

function geolocate() {
  geoError.value = ''
  if (!navigator.geolocation) {
    geoError.value = 'Geolocation not supported by this browser.'
    return
  }
  navigator.geolocation.getCurrentPosition(
    (pos) => {
      lat.value = Math.round(pos.coords.latitude  * 10000) / 10000
      lng.value = Math.round(pos.coords.longitude * 10000) / 10000
    },
    () => { geoError.value = 'Could not get location. Enter coordinates manually.' },
  )
}

function submit() {
  if (lat.value === '' || lng.value === '') return
  emit('submit', {
    lat: lat.value,
    lng: lng.value,
    radius: radius.value,
    days: days.value,
    top: top.value,
    lifer: lifer.value,
    notable: notable.value,
    life_list: [], // filled in by parent from localStorage
  })
}
</script>

<style scoped>
.form {
  display: flex;
  flex-direction: column;
  gap: .9rem;
}

.fields {
  display: flex;
  gap: .75rem;
  align-items: flex-end;
  flex-wrap: wrap;
}

.field-group {
  display: flex;
  flex-direction: column;
  gap: .25rem;
  flex: 1;
  min-width: 100px;
}

.field-group label {
  font-size: .8rem;
  font-weight: 600;
  color: var(--color-text-muted);
}

.input {
  padding: .5rem .75rem;
  border: 1px solid var(--color-border);
  border-radius: 6px;
  font-size: .95rem;
  background: var(--color-bg);
  color: var(--color-text);
  width: 100%;
  box-sizing: border-box;
}

.btn-locate {
  height: 38px;
  padding: 0 .75rem;
  background: none;
  border: 1px solid var(--color-border);
  border-radius: 6px;
  cursor: pointer;
  font-size: 1.1rem;
  flex-shrink: 0;
}
.btn-locate:hover { background: var(--color-surface); }


.btn-submit {
  padding: .65rem 1.5rem;
  background: var(--color-accent);
  color: #fff;
  border: none;
  border-radius: 8px;
  font-size: 1rem;
  cursor: pointer;
  font-weight: 600;
  align-self: flex-start;
  transition: filter .15s;
}
.btn-submit:hover:not(:disabled) { filter: brightness(1.1); }
.btn-submit:disabled { opacity: .6; cursor: default; }

.error { color: #e55; font-size: .85rem; margin: 0; }
</style>
