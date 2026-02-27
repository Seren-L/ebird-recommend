<template>
  <div class="results">
    <p class="summary">{{ results.length }} recommendation{{ results.length === 1 ? '' : 's' }}</p>
    <div class="table-wrap">
      <table>
        <thead>
          <tr>
            <th>#</th>
            <th>Species</th>
            <th>Location</th>
            <th>Dist (km)</th>
            <th>Last seen</th>
            <th>Reports</th>
            <th>Flags</th>
          </tr>
        </thead>
        <tbody>
          <tr v-for="(rec, i) in results" :key="rec.species_code + rec.loc_id">
            <td class="rank">{{ i + 1 }}</td>
            <td>
              <a :href="rec.species_url" target="_blank" rel="noopener" class="species-link">
                {{ rec.common_name }}
              </a>
              <div class="sci-name">{{ rec.scientific_name }}</div>
            </td>
            <td>
              <RouterLink :to="`/hotspot/${rec.loc_id}`" class="loc-link">
                {{ rec.loc_name }}
              </RouterLink>
              <div class="reason">{{ rec.reason }}</div>
            </td>
            <td class="num">{{ rec.distance_km.toFixed(1) }}</td>
            <td class="num">{{ formatDate(rec.last_reported) }}</td>
            <td class="num">{{ rec.report_count }}</td>
            <td class="flags">
              <span v-if="rec.is_lifer"  class="badge lifer">Lifer</span>
              <span v-if="rec.is_notable" class="badge notable">Notable</span>
            </td>
          </tr>
        </tbody>
      </table>
    </div>
  </div>
</template>

<script setup lang="ts">
import type { Recommendation } from '../types'

defineProps<{ results: Recommendation[] }>()

function formatDate(dt: string): string {
  // dt is like "2025-01-15 14:32" or "2025-01-15"
  return dt.slice(0, 10)
}
</script>

<style scoped>
.results { display: flex; flex-direction: column; gap: .75rem; }

.summary { font-size: .9rem; color: var(--color-text-muted); margin: 0; }

.table-wrap { overflow-x: auto; }

table {
  width: 100%;
  border-collapse: collapse;
  font-size: .9rem;
}

th {
  text-align: left;
  padding: .5rem .75rem;
  border-bottom: 2px solid var(--color-border);
  font-size: .8rem;
  color: var(--color-text-muted);
  white-space: nowrap;
}

td {
  padding: .55rem .75rem;
  border-bottom: 1px solid var(--color-border);
  vertical-align: top;
}

tr:hover td { background: color-mix(in srgb, var(--color-accent) 5%, transparent); }

.rank { color: var(--color-text-muted); font-size: .85rem; width: 2rem; }

.species-link, .loc-link {
  color: var(--color-accent);
  text-decoration: none;
  font-weight: 500;
}
.species-link:hover, .loc-link:hover { text-decoration: underline; }

.sci-name {
  font-style: italic;
  font-size: .78rem;
  color: var(--color-text-muted);
  margin-top: .15rem;
}

.reason {
  font-size: .78rem;
  color: var(--color-text-muted);
  margin-top: .15rem;
}

.num { text-align: right; white-space: nowrap; width: 6rem; }

.flags { white-space: nowrap; width: 8rem; }

.badge {
  display: inline-block;
  padding: .15rem .45rem;
  border-radius: 4px;
  font-size: .75rem;
  font-weight: 600;
  margin-right: .25rem;
}
.lifer   { background: #dbeafe; color: #1d4ed8; }
.notable { background: #fef3c7; color: #92400e; }
</style>
