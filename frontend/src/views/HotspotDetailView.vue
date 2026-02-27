<template>
  <main class="main">
    <div class="card">
      <!-- Header -->
      <div class="detail-header">
        <RouterLink to="/" class="back-link">← Back</RouterLink>
        <div>
          <h2 class="loc-name">{{ data?.recent[0]?.locName ?? data?.notable[0]?.locName ?? locId }}</h2>
          <a :href="`https://ebird.org/hotspot/${locId}`" target="_blank" rel="noopener" class="ebird-link">
            View on eBird ↗
          </a>
        </div>
      </div>

      <!-- Loading -->
      <div v-if="loading" class="status">Loading…</div>
      <div v-else-if="error" class="error">{{ error }}</div>

      <!-- No API key -->
      <div v-else-if="!apiKey" class="status">
        Open Settings (⚙️) and enter your eBird API key to view hotspot details.
      </div>

      <template v-else-if="data">
        <!-- Notable -->
        <section class="section">
          <h3 class="section-title">Notable <span class="count">({{ data.notable.length }})</span></h3>
          <p v-if="!data.notable.length" class="empty">No notable observations in this period.</p>
          <table v-else class="obs-table">
            <thead><tr><th>Species</th><th>Date</th><th>Count</th><th>Flags</th></tr></thead>
            <tbody>
              <tr v-for="obs in data.notable" :key="obs.subId + obs.speciesCode">
                <td>
                  <a :href="`https://ebird.org/species/${obs.speciesCode}`" target="_blank" rel="noopener" class="species-link">
                    {{ obs.comName }}
                  </a>
                  <div class="sci-name">{{ obs.sciName }}</div>
                </td>
                <td class="num">{{ obs.obsDt.slice(0, 10) }}</td>
                <td class="num">{{ obs.howMany ?? '–' }}</td>
                <td>
                  <span class="badge notable">Notable</span>
                  <span v-if="isLifer(obs.sciName)" class="badge lifer">Lifer</span>
                </td>
              </tr>
            </tbody>
          </table>
        </section>

        <!-- All Species -->
        <section class="section">
          <h3 class="section-title">All Species <span class="count">({{ data.recent.length }})</span></h3>
          <p v-if="!data.recent.length" class="empty">No observations in this period.</p>
          <table v-else class="obs-table">
            <thead><tr><th>Species</th><th>Date</th><th>Count</th><th>Flags</th></tr></thead>
            <tbody>
              <tr v-for="obs in data.recent" :key="obs.subId + obs.speciesCode">
                <td>
                  <a :href="`https://ebird.org/species/${obs.speciesCode}`" target="_blank" rel="noopener" class="species-link">
                    {{ obs.comName }}
                  </a>
                  <div class="sci-name">{{ obs.sciName }}</div>
                </td>
                <td class="num">{{ obs.obsDt.slice(0, 10) }}</td>
                <td class="num">{{ obs.howMany ?? '–' }}</td>
                <td>
                  <span v-if="isLifer(obs.sciName)" class="badge lifer">Lifer</span>
                </td>
              </tr>
            </tbody>
          </table>
        </section>

        <!-- Checklists -->
        <section class="section">
          <h3 class="section-title">Recent Checklists <span class="count">({{ data.checklists.length }})</span></h3>
          <p v-if="!data.checklists.length" class="empty">No checklists found.</p>
          <table v-else class="obs-table">
            <thead><tr><th>Date</th><th>Species</th><th>Observers</th><th>Duration</th><th></th></tr></thead>
            <tbody>
              <tr v-for="cl in data.checklists" :key="cl.sub_id">
                <td class="num">{{ cl.obs_dt.slice(0, 10) }}{{ cl.obs_time ? ' ' + cl.obs_time : '' }}</td>
                <td class="num">{{ cl.num_species }}</td>
                <td class="num">{{ cl.num_observers ?? '–' }}</td>
                <td class="num">{{ cl.duration_hrs != null ? cl.duration_hrs + 'h' : '–' }}</td>
                <td>
                  <a :href="`https://ebird.org/checklist/${cl.sub_id}`" target="_blank" rel="noopener" class="ebird-link">
                    View ↗
                  </a>
                </td>
              </tr>
            </tbody>
          </table>
        </section>
      </template>
    </div>
  </main>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { useRoute } from 'vue-router'
import { fetchHotspotDetail } from '../api'
import { getApiKey, getLifeList } from '../store'
import type { HotspotDetail } from '../types'

const route  = useRoute()
const locId  = route.params.locId as string
const apiKey = getApiKey()

const loading = ref(false)
const error   = ref('')
const data    = ref<HotspotDetail | null>(null)

const lifeListSet = new Set(
  (getLifeList() ?? []).map(s => s.scientific_name)
)
function isLifer(sciName: string): boolean {
  return !lifeListSet.has(sciName)
}

onMounted(async () => {
  if (!apiKey) return
  loading.value = true
  try {
    data.value = await fetchHotspotDetail(apiKey, locId)
  } catch (err: any) {
    error.value = err.message
  } finally {
    loading.value = false
  }
})
</script>

<style scoped>
.main {
  flex: 1;
  max-width: 960px;
  width: 100%;
  margin: 0 auto;
  padding: 1.5rem 1rem 3rem;
}

.card {
  background: var(--color-surface);
  border: 1px solid var(--color-border);
  border-radius: 10px;
  padding: 1.5rem;
  display: flex;
  flex-direction: column;
  gap: 2rem;
}

.detail-header {
  display: flex;
  align-items: flex-start;
  gap: 1rem;
}

.back-link {
  color: var(--color-accent);
  text-decoration: none;
  font-size: .9rem;
  white-space: nowrap;
  padding-top: .2rem;
}
.back-link:hover { text-decoration: underline; }

.loc-name { margin: 0 0 .25rem; font-size: 1.2rem; }

.ebird-link { color: var(--color-accent); font-size: .85rem; text-decoration: none; }
.ebird-link:hover { text-decoration: underline; }

.section { display: flex; flex-direction: column; gap: .75rem; }

.section-title {
  margin: 0;
  font-size: 1rem;
  font-weight: 700;
  border-bottom: 2px solid var(--color-border);
  padding-bottom: .4rem;
}
.count { font-weight: 400; color: var(--color-text-muted); font-size: .85rem; }

.obs-table { width: 100%; border-collapse: collapse; font-size: .9rem; }
.obs-table th {
  text-align: left;
  padding: .4rem .6rem;
  font-size: .8rem;
  color: var(--color-text-muted);
  white-space: nowrap;
}
.obs-table td {
  padding: .45rem .6rem;
  border-bottom: 1px solid var(--color-border);
  vertical-align: top;
}
.obs-table tr:hover td { background: color-mix(in srgb, var(--color-accent) 5%, transparent); }

.species-link { color: var(--color-accent); text-decoration: none; font-weight: 500; }
.species-link:hover { text-decoration: underline; }

.sci-name {
  font-style: italic;
  font-size: .78rem;
  color: var(--color-text-muted);
  margin-top: .1rem;
}

.num { text-align: right; white-space: nowrap; }

.badge {
  display: inline-block;
  padding: .15rem .45rem;
  border-radius: 4px;
  font-size: .75rem;
  font-weight: 600;
  margin-right: .2rem;
}
.lifer   { background: #dbeafe; color: #1d4ed8; }
.notable { background: #fef3c7; color: #92400e; }

.status, .empty { color: var(--color-text-muted); font-size: .95rem; }
.error { color: #c00; }
</style>
