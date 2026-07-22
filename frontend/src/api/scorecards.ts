import { apiFetch } from './client'
import type { Scorecard, ScorecardDetail, ScorecardTemplate, KpiDefinition, KpiEntry } from '../types'

export const scorecardApi = {
  list: (status?: string) =>
    apiFetch<Scorecard[]>(`/scorecards/${status ? `?status=${status}` : ''}`),

  get: (id: string) =>
    apiFetch<ScorecardDetail>(`/scorecards/${id}`),

  create: (data: {
    name: string
    period_start: string
    period_end: string
    template_id?: string
    meeting_date?: string
    meeting_notes?: string
  }) =>
    apiFetch<ScorecardDetail>('/scorecards/', {
      method: 'POST',
      body: JSON.stringify(data),
    }),

  update: (id: string, data: Record<string, unknown>) =>
    apiFetch<ScorecardDetail>(`/scorecards/${id}`, {
      method: 'PUT',
      body: JSON.stringify(data),
    }),

  publish: (id: string) =>
    apiFetch<ScorecardDetail>(`/scorecards/${id}/publish`, { method: 'POST' }),

  refresh: (id: string) =>
    apiFetch<ScorecardDetail>(`/scorecards/${id}/refresh`, { method: 'POST' }),

  updateEntry: (scorecardId: string, entryId: string, data: Record<string, unknown>) =>
    apiFetch<KpiEntry>(`/scorecards/${scorecardId}/entries/${entryId}`, {
      method: 'PUT',
      body: JSON.stringify(data),
    }),

  definitions: {
    list: () => apiFetch<KpiDefinition[]>('/scorecards/definitions'),
    create: (data: Record<string, unknown>) =>
      apiFetch<KpiDefinition>('/scorecards/definitions', {
        method: 'POST',
        body: JSON.stringify(data),
      }),
    update: (id: string, data: Record<string, unknown>) =>
      apiFetch<KpiDefinition>(`/scorecards/definitions/${id}`, {
        method: 'PUT',
        body: JSON.stringify(data),
      }),
    delete: (id: string) =>
      apiFetch(`/scorecards/definitions/${id}`, { method: 'DELETE' }),
  },

  templates: {
    list: () => apiFetch<ScorecardTemplate[]>('/scorecards/templates'),
    create: (data: Record<string, unknown>) =>
      apiFetch<ScorecardTemplate>('/scorecards/templates', {
        method: 'POST',
        body: JSON.stringify(data),
      }),
    update: (id: string, data: Record<string, unknown>) =>
      apiFetch<ScorecardTemplate>(`/scorecards/templates/${id}`, {
        method: 'PUT',
        body: JSON.stringify(data),
      }),
    delete: (id: string) =>
      apiFetch(`/scorecards/templates/${id}`, { method: 'DELETE' }),
  },
}
