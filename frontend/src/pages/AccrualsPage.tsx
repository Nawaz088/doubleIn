import { useState, useEffect } from 'react'
import { Plus, FileClock, Calendar, CircleDollarSign } from 'lucide-react'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import { StatusBadge } from '@/components/ui/status-badge'
import { apiFetch } from '@/api/client'
import type { AccrualSchedule, AccrualScheduleDetail, AccrualEntry, Client } from '@/types'

const typeLabels: Record<string, string> = {
  prepaid_expense: 'Prepaid Expense',
  fixed_asset: 'Fixed Asset',
  accrued_expense: 'Accrued Expense',
  deferred_revenue: 'Deferred Revenue',
}

export function AccrualsPage() {
  const [schedules, setSchedules] = useState<AccrualSchedule[]>([])
  const [clients, setClients] = useState<Client[]>([])
  const [loading, setLoading] = useState(true)
  const [showModal, setShowModal] = useState(false)
  const [selectedSchedule, setSelectedSchedule] = useState<AccrualScheduleDetail | null>(null)
  const [form, setForm] = useState({
    client_id: '',
    name: '',
    type: 'prepaid_expense',
    total_amount: 0,
    start_date: '',
    end_date: '',
    recognition_method: 'straight_line',
  })

  const load = async () => {
    setLoading(true)
    try {
      const [s, c] = await Promise.all([
        apiFetch<AccrualSchedule[]>('/accruals/schedules'),
        apiFetch<Client[]>('/clients/'),
      ])
      setSchedules(s)
      setClients(c)
    } catch {} finally {
      setLoading(false)
    }
  }

  useEffect(() => { load() }, [])

  const handleCreate = async (e: React.FormEvent) => {
    e.preventDefault()
    await apiFetch('/accruals/schedules', {
      method: 'POST',
      body: JSON.stringify(form),
    })
    setShowModal(false)
    setForm({ client_id: '', name: '', type: 'prepaid_expense', total_amount: 0, start_date: '', end_date: '', recognition_method: 'straight_line' })
    load()
  }

  const handleSelect = async (scheduleId: string) => {
    try {
      const data = await apiFetch<AccrualScheduleDetail>(`/accruals/schedules/${scheduleId}`)
      setSelectedSchedule(data)
    } catch {}
  }

  const handleGenerateEntries = async (scheduleId: string) => {
    await apiFetch(`/accruals/schedules/${scheduleId}/entries/generate`, { method: 'POST' })
    if (selectedSchedule) handleSelect(scheduleId)
  }

  if (loading) {
    return (
      <div className="space-y-4">
        <div className="flex items-center justify-between">
          <div>
            <div className="skeleton h-8 w-48 rounded-lg" />
            <div className="skeleton h-4 w-64 rounded-lg mt-2" />
          </div>
          <div className="skeleton h-9 w-32 rounded-lg" />
        </div>
        <div className="skeleton h-24 w-full rounded-xl" />
        <div className="skeleton h-48 w-full rounded-xl" />
      </div>
    )
  }

  if (selectedSchedule) {
    return (
      <div className="space-y-6">
        <div className="flex items-center gap-4">
          <Button variant="ghost" size="sm" onClick={() => setSelectedSchedule(null)}>Back</Button>
          <div className="flex-1">
            <h1 className="text-3xl font-bold tracking-tight">{selectedSchedule.name}</h1>
            <p className="text-muted-foreground">{typeLabels[selectedSchedule.type] || selectedSchedule.type}</p>
          </div>
          <StatusBadge status={selectedSchedule.status} />
          <Button size="sm" onClick={() => handleGenerateEntries(selectedSchedule.id)}>
            <Plus className="w-4 h-4 mr-1" /> Generate Entries
          </Button>
        </div>

        <div className="grid grid-cols-3 gap-4">
          <Card>
            <CardHeader className="pb-2">
              <p className="text-sm text-muted-foreground">Total Amount</p>
              <p className="text-2xl font-bold">${selectedSchedule.total_amount.toLocaleString()}</p>
            </CardHeader>
          </Card>
          <Card>
            <CardHeader className="pb-2">
              <p className="text-sm text-muted-foreground">Start Date</p>
              <p className="text-2xl font-bold">{new Date(selectedSchedule.start_date).toLocaleDateString()}</p>
            </CardHeader>
          </Card>
          <Card>
            <CardHeader className="pb-2">
              <p className="text-sm text-muted-foreground">Recognition</p>
              <p className="text-2xl font-bold capitalize">{selectedSchedule.recognition_method.replace('_', ' ')}</p>
            </CardHeader>
          </Card>
        </div>

        <Card>
          <CardHeader><CardTitle className="text-base">Entries</CardTitle></CardHeader>
          <CardContent>
            {selectedSchedule.entries.length === 0 ? (
              <p className="text-sm text-muted-foreground">No entries yet. Click "Generate Entries" to create them.</p>
            ) : (
              <div className="rounded-xl border overflow-hidden">
                <table className="w-full">
                  <thead>
                    <tr className="border-b bg-muted/50">
                      <th className="p-3 text-xs font-medium text-muted-foreground uppercase tracking-wider">Period</th>
                      <th className="p-3 text-xs font-medium text-muted-foreground uppercase tracking-wider">Amount</th>
                      <th className="p-3 text-xs font-medium text-muted-foreground uppercase tracking-wider">Status</th>
                      <th className="p-3 text-xs font-medium text-muted-foreground uppercase tracking-wider">Posted</th>
                    </tr>
                  </thead>
                  <tbody className="divide-y divide-border">
                    {selectedSchedule.entries.map((entry: AccrualEntry) => (
                      <tr key={entry.id} className="hover:bg-accent/50 transition-colors">
                        <td className="p-3 text-sm">{new Date(entry.period_date).toLocaleDateString()}</td>
                        <td className="p-3 text-sm font-mono">
                          ${entry.recognized_amount.toLocaleString('en-US', { minimumFractionDigits: 2 })}
                        </td>
                        <td className="p-3">
                          <StatusBadge status={entry.status} />
                        </td>
                        <td className="p-3 text-sm text-muted-foreground">
                          {entry.posted_at ? new Date(entry.posted_at).toLocaleDateString() : '—'}
                        </td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            )}
          </CardContent>
        </Card>
      </div>
    )
  }

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold tracking-tight">Accruals</h1>
          <p className="text-muted-foreground mt-1">Manage prepaid expenses, fixed assets, and accrual schedules.</p>
        </div>
        <Button size="sm" className="gap-2" onClick={() => setShowModal(true)}>
          <Plus className="w-4 h-4" />
          New Schedule
        </Button>
      </div>

      {schedules.length === 0 ? (
        <Card className="p-12 text-center">
          <FileClock className="w-12 h-12 mx-auto text-muted-foreground mb-4" />
          <h3 className="text-lg font-medium mb-2">No accrual schedules</h3>
          <p className="text-muted-foreground mb-4">
            Create accrual schedules for prepaid expenses, amortization, and deferrals.
          </p>
          <Button className="gap-2" onClick={() => setShowModal(true)}>
            <Plus className="w-4 h-4" />
            New Schedule
          </Button>
        </Card>
      ) : (
        <div className="space-y-3">
          {schedules.map((s) => (
            <Card
              key={s.id}
              className="hover:border-primary/50 transition-colors cursor-pointer"
              onClick={() => handleSelect(s.id)}
            >
              <CardContent className="p-4 flex items-center justify-between">
                <div className="flex items-center gap-4">
                  <CircleDollarSign className="w-8 h-8 text-primary" />
                  <div>
                    <h3 className="font-semibold">{s.name}</h3>
                    <p className="text-sm text-muted-foreground">
                      {typeLabels[s.type] || s.type} · ${s.total_amount.toLocaleString()}
                    </p>
                  </div>
                </div>
                <div className="flex items-center gap-4 text-sm">
                  <span className="text-muted-foreground">
                    {new Date(s.start_date).toLocaleDateString()}
                    {s.end_date && ` — ${new Date(s.end_date).toLocaleDateString()}`}
                  </span>
                  <StatusBadge status={s.status} />
                </div>
              </CardContent>
            </Card>
          ))}
        </div>
      )}

      {showModal && (
        <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/50">
          <Card className="w-full max-w-lg mx-4">
            <CardHeader><CardTitle>New Accrual Schedule</CardTitle></CardHeader>
            <CardContent>
              <form onSubmit={handleCreate} className="space-y-4">
                <div>
                  <label className="text-sm font-medium block mb-1">Client</label>
                  <select
                    className="flex h-9 w-full rounded-md border border-input bg-background px-3 py-1 text-sm shadow-sm focus-visible:outline-none focus-visible:ring-1 focus-visible:ring-ring"
                    value={form.client_id}
                    onChange={(e) => setForm((f) => ({ ...f, client_id: e.target.value }))}
                    required
                  >
                    <option value="">Select client</option>
                    {clients.map((c) => (
                      <option key={c.id} value={c.id}>{c.name}</option>
                    ))}
                  </select>
                </div>
                <div>
                  <label className="text-sm font-medium block mb-1">Name</label>
                  <Input value={form.name} onChange={(e) => setForm((f) => ({ ...f, name: e.target.value }))} required />
                </div>
                <div>
                  <label className="text-sm font-medium block mb-1">Type</label>
                  <select
                    className="flex h-9 w-full rounded-md border border-input bg-background px-3 py-1 text-sm shadow-sm focus-visible:outline-none focus-visible:ring-1 focus-visible:ring-ring"
                    value={form.type}
                    onChange={(e) => setForm((f) => ({ ...f, type: e.target.value }))}
                  >
                    {Object.entries(typeLabels).map(([k, v]) => (
                      <option key={k} value={k}>{v}</option>
                    ))}
                  </select>
                </div>
                <div>
                  <label className="text-sm font-medium block mb-1">Total Amount</label>
                  <Input type="number" value={form.total_amount} onChange={(e) => setForm((f) => ({ ...f, total_amount: parseFloat(e.target.value) || 0 }))} required />
                </div>
                <div className="grid grid-cols-2 gap-4">
                  <div>
                    <label className="text-sm font-medium block mb-1">Start Date</label>
                    <Input type="date" value={form.start_date} onChange={(e) => setForm((f) => ({ ...f, start_date: e.target.value }))} required />
                  </div>
                  <div>
                    <label className="text-sm font-medium block mb-1">End Date</label>
                    <Input type="date" value={form.end_date} onChange={(e) => setForm((f) => ({ ...f, end_date: e.target.value }))} />
                  </div>
                </div>
                <div>
                  <label className="text-sm font-medium block mb-1">Recognition Method</label>
                  <select
                    className="flex h-9 w-full rounded-md border border-input bg-background px-3 py-1 text-sm shadow-sm focus-visible:outline-none focus-visible:ring-1 focus-visible:ring-ring"
                    value={form.recognition_method}
                    onChange={(e) => setForm((f) => ({ ...f, recognition_method: e.target.value }))}
                  >
                    <option value="straight_line">Straight Line</option>
                    <option value="custom">Custom</option>
                  </select>
                </div>
                <div className="flex justify-end gap-2">
                  <Button type="button" variant="outline" onClick={() => setShowModal(false)}>Cancel</Button>
                  <Button type="submit">Create</Button>
                </div>
              </form>
            </CardContent>
          </Card>
        </div>
      )}
    </div>
  )
}
