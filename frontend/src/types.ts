export interface SeenSpecies {
  scientific_name: string
  common_name: string
  species_code?: string
  last_seen?: string // ISO date string
}

export type FilterMode = 'all' | 'yes' | 'no'

export interface RecommendRequest {
  life_list: SeenSpecies[]
  lat: number
  lng: number
  radius?: number
  days?: number
  top?: number
  lifer?: FilterMode    // "all" | "yes" = lifers only | "no" = seen only
  notable?: FilterMode  // "all" | "yes" = rare only   | "no" = non-rare only
}

export interface Recommendation {
  species_code: string
  common_name: string
  scientific_name: string
  loc_id: string
  loc_name: string
  lat: number
  lng: number
  distance_km: number
  last_reported: string
  report_count: number
  is_notable: boolean
  is_lifer: boolean
  score: number
  reason: string
  species_url: string
  hotspot_url: string
}
