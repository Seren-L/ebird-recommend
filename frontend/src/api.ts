import type { HotspotDetail, Recommendation, RecommendRequest } from './types'

const BASE_URL = import.meta.env.VITE_API_URL ?? 'http://localhost:8000'

function headers(apiKey: string): Record<string, string> {
  return {
    'Content-Type': 'application/json',
    'X-EBird-Api-Token': apiKey,
  }
}

export async function fetchRecommendations(
  apiKey: string,
  req: RecommendRequest,
): Promise<Recommendation[]> {
  const res = await fetch(`${BASE_URL}/recommend`, {
    method: 'POST',
    headers: headers(apiKey),
    body: JSON.stringify(req),
  })

  if (res.status === 401) throw new Error('Invalid or missing eBird API key.')
  if (!res.ok) {
    const detail = await res.json().catch(() => ({ detail: res.statusText }))
    throw new Error(detail?.detail ?? 'API error')
  }

  return res.json()
}

export async function fetchHotspotDetail(
  apiKey: string,
  locId: string,
  days = 14,
  limit = 10,
): Promise<HotspotDetail> {
  const res = await fetch(`${BASE_URL}/hotspot/${locId}?days=${days}&limit=${limit}`, {
    headers: headers(apiKey),
  })

  if (res.status === 401) throw new Error('Invalid or missing eBird API key.')
  if (!res.ok) {
    const detail = await res.json().catch(() => ({ detail: res.statusText }))
    throw new Error(detail?.detail ?? 'API error')
  }

  return res.json()
}
