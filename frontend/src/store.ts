import type { SeenSpecies } from './types'

const KEY_API_KEY   = 'ebird_api_key'
const KEY_LIFE_LIST = 'ebird_life_list'

// --- API key ---

export function getApiKey(): string {
  return localStorage.getItem(KEY_API_KEY) ?? ''
}

export function setApiKey(key: string): void {
  localStorage.setItem(KEY_API_KEY, key.trim())
}

// --- Life list ---

export function getLifeList(): SeenSpecies[] | null {
  const raw = localStorage.getItem(KEY_LIFE_LIST)
  if (!raw) return null
  try {
    return JSON.parse(raw) as SeenSpecies[]
  } catch {
    return null
  }
}

export function setLifeList(list: SeenSpecies[]): void {
  localStorage.setItem(KEY_LIFE_LIST, JSON.stringify(list))
}

export function clearLifeList(): void {
  localStorage.removeItem(KEY_LIFE_LIST)
}

// --- CSV parser ---
// Replicates Python load_life_list() logic in the browser.

export function parseLifeListCsv(csvText: string): SeenSpecies[] {
  const lines = csvText.split(/\r?\n/)
  if (lines.length < 2) return []

  // Parse header
  const header = parseCsvLine(lines[0]!)
  const colIdx = (name: string) => header.findIndex(h => h.trim() === name)

  const idxSci    = colIdx('Scientific Name')
  const idxCommon = colIdx('Common Name')
  const idxDate   = colIdx('Date')

  if (idxSci < 0) throw new Error('CSV missing "Scientific Name" column')

  const seen = new Map<string, SeenSpecies>()

  for (let i = 1; i < lines.length; i++) {
    const line = lines[i]!.trim()
    if (!line) continue

    const cols = parseCsvLine(line)
    const sci  = cols[idxSci]?.trim()
    if (!sci) continue

    const common   = idxCommon >= 0 ? (cols[idxCommon]?.trim() ?? '') : ''
    const rawDate  = idxDate  >= 0 ? (cols[idxDate]?.trim()  ?? '') : ''
    const obsDate  = parseDate(rawDate)

    const existing = seen.get(sci)
    if (!existing) {
      seen.set(sci, { scientific_name: sci, common_name: common, last_seen: obsDate })
    } else if (obsDate && (!existing.last_seen || obsDate > existing.last_seen)) {
      existing.last_seen = obsDate
    }
  }

  return Array.from(seen.values())
}

// Simple RFC 4180-style CSV line parser (handles quoted fields with commas).
function parseCsvLine(line: string): string[] {
  const result: string[] = []
  let current = ''
  let inQuotes = false

  for (let i = 0; i < line.length; i++) {
    const ch = line[i]
    if (ch === '"') {
      if (inQuotes && line[i + 1] === '"') {
        current += '"'
        i++
      } else {
        inQuotes = !inQuotes
      }
    } else if (ch === ',' && !inQuotes) {
      result.push(current)
      current = ''
    } else {
      current += ch
    }
  }
  result.push(current)
  return result
}

// Returns an ISO date string (YYYY-MM-DD) or undefined.
function parseDate(raw: string): string | undefined {
  if (!raw) return undefined
  // Try YYYY-MM-DD
  if (/^\d{4}-\d{2}-\d{2}$/.test(raw)) return raw
  // Try MM/DD/YYYY
  const mdy = raw.match(/^(\d{1,2})\/(\d{1,2})\/(\d{4})$/)
  if (mdy) return `${mdy[3]!}-${mdy[1]!.padStart(2, '0')}-${mdy[2]!.padStart(2, '0')}`
  return undefined
}
