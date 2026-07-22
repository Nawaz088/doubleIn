import { useState, useEffect } from 'react'
import { Plus, FileText, Send, Trash2, Calendar } from 'lucide-react'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import { StatusBadge } from '@/components/ui/status-badge'
import { apiFetch } from '@/api/client'
import type { JournalEntry, Client } from '@/types'

const sourceConfig: Record<string, string> = {
  manual: 'Manual',
  recurring: 'Recurring',
  accrual: 'Accrual',
}

interface LineItem {
  id: string
  account_name: string
  debit_amount: number
  credit_amount: number
}

export function JournalEntriesPage() {
  const [entries, setEntries] = useState<JournalEntry[]>([])
  const [clients, setClients] = useState<Client[]>([])
  const [loading, setLoading] = useState(true)
  const [showForm, setShowForm] = useState(false)

  const [form, setForm] = useState({
    client_id: '',
    description: '',
    date: new Date().toISOString().split('T')[0],
    lines: [{ id: crypto.randomUUID(), account_name: '', debit_amount: 0, credit_amount: 0 }] as LineItem[],
  })

  const load = async () => {
    setLoading(true)
    try {
      const [je, cl] = await Promise.all([
        apiFetch<JournalEntry[]>('/journal-entries/'),
        apiFetch<Client[]>('/clients/'),
      ])
      setEntries(je)
      setClients(cl)
    } catch {} finally {
      setLoading(false)
    }
  }

  useEffect(() => { load() }, [])

  const handlePost = async (id: string) => {
    await apiFetch(`/journal-entries/${id}/post`, { method: 'POST' })
    load()
  }

  const addLine = () => {
    setForm((f) => ({
      ...f,
      lines: [...f.lines, { id: crypto.randomUUID(), account_name: '', debit_amount: 0, credit_amount: 0 }],
    }))
  }

  const removeLine = (lineId: string) => {
    setForm((f) => ({ ...f, lines: f.lines.filter((l) => l.id !== lineId) }))
  }

  const updateLine = (lineId: string, field: keyof LineItem, value: string | number) => {
    setForm((f) => ({
      ...f,
      lines: f.lines.map((l) => (l.id === lineId ? { ...l, [field]: value } : l)),
    }))
  }

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    await apiFetch('/journal-entries/', {
      method: 'POST',
      body: JSON.stringify({
        client_id: form.client_id,
        description: form.description,
        date: form.date,
        lines: form.lines.map((l) => ({
          account_name: l.account_name,
          debit_amount: l.debit_amount,
          credit_amount: l.credit_amount,
        })),
      }),
    })
    setShowForm(false)
    setForm({
      client_id: '',
      description: '',
      date: new Date().toISOString().split('T')[0],
      lines: [{ id: crypto.randomUUID(), account_name: '', debit_amount: 0, credit_amount: 0 }],
    })
    load()
  }

  if (loading) {
    return (
      <div className="space-y-4">
        <div className="flex items-center justify-between">
          <div>
            <div className="skeleton h-8 w-48 rounded-lg" />
            <div className="skeleton h-4 w-64 rounded-lg mt-2" />
          </div>
          <div className="skeleton h-9 w-28 rounded-lg" />
        </div>
        <div className="skeleton h-64 w-full rounded-xl" />
      </div>
    )
  }

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold tracking-tight">Journal Entries</h1>
          <p className="text-muted-foreground mt-1">Create and post journal entries to the ledger.</p>
        </div>
        <Button size="sm" className="gap-2" onClick={() => setShowForm(true)}>
          <Plus className="w-4 h-4" />
          New Entry
        </Button>
      </div>

      {entries.length === 0 ? (
        <Card className="p-12 text-center">
          <FileText className="w-12 h-12 mx-auto text-muted-foreground mb-4" />
          <h3 className="text-lg font-medium mb-2">No journal entries</h3>
          <p className="text-muted-foreground mb-4">
            Create your first journal entry to start recording transactions.
          </p>
          <Button className="gap-2" onClick={() => setShowForm(true)}>
            <Plus className="w-4 h-4" />
            New Entry
          </Button>
        </Card>
      ) : (
        <div className="rounded-xl border overflow-hidden">
          <table className="w-full">
            <thead>
              <tr className="border-b bg-muted/50">
                <th className="p-3 text-xs font-medium text-muted-foreground uppercase tracking-wider">Date</th>
                <th className="p-3 text-xs font-medium text-muted-foreground uppercase tracking-wider">Description</th>
                <th className="p-3 text-xs font-medium text-muted-foreground uppercase tracking-wider">Source</th>
                <th className="p-3 text-xs font-medium text-muted-foreground uppercase tracking-wider">Status</th>
                <th className="p-3 text-xs font-medium text-muted-foreground uppercase tracking-wider">Actions</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-border">
              {entries.map((je) => (
                <tr key={je.id} className="hover:bg-accent/50 transition-colors">
                  <td className="p-3 text-sm">
                    <div className="flex items-center gap-2">
                      <Calendar className="w-3.5 h-3.5 text-muted-foreground" />
                      {new Date(je.date).toLocaleDateString()}
                    </div>
                  </td>
                  <td className="p-3 text-sm max-w-[300px] truncate">{je.description}</td>
                  <td className="p-3 text-sm text-muted-foreground">{sourceConfig[je.source] || je.source}</td>
                  <td className="p-3">
                    <StatusBadge status={je.status} />
                  </td>
                  <td className="p-3">
                    <div className="flex items-center gap-1">
                      {je.status === 'draft' && (
                        <Button variant="ghost" size="sm" onClick={() => handlePost(je.id)}>
                          <Send className="w-4 h-4 mr-1" /> Post
                        </Button>
                      )}
                    </div>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}

      {showForm && (
        <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/50">
          <Card className="w-full max-w-3xl mx-4 max-h-[90vh] overflow-y-auto">
            <CardHeader>
              <CardTitle>New Journal Entry</CardTitle>
            </CardHeader>
            <CardContent>
              <form onSubmit={handleSubmit} className="space-y-4">
                <div>
                  <label className="text-sm font-medium block mb-1">Client</label>
                  <select
                    className="flex h-9 w-full rounded-md border border-input bg-background px-3 py-1 text-sm shadow-sm focus-visible:outline-none focus-visible:ring-1 focus-visible:ring-ring"
                    value={form.client_id}
                    onChange={(e) => setForm((f) => ({ ...f, client_id: e.target.value }))}
                    required
                  >
                    <option value="">Select a client</option>
                    {clients.map((c) => (
                      <option key={c.id} value={c.id}>{c.name}</option>
                    ))}
                  </select>
                </div>
                <div>
                  <label className="text-sm font-medium block mb-1">Date</label>
                  <Input type="date" value={form.date} onChange={(e) => setForm((f) => ({ ...f, date: e.target.value }))} required />
                </div>
                <div>
                  <label className="text-sm font-medium block mb-1">Description</label>
                  <Input value={form.description} onChange={(e) => setForm((f) => ({ ...f, description: e.target.value }))} required />
                </div>

                <div>
                  <div className="flex items-center justify-between mb-2">
                    <label className="text-sm font-medium">Line Items</label>
                    <Button type="button" variant="outline" size="sm" onClick={addLine}>
                      <Plus className="w-3 h-3 mr-1" /> Add Line
                    </Button>
                  </div>
                  <div className="space-y-2">
                    {form.lines.map((line) => (
                      <div key={line.id} className="flex items-center gap-2">
                        <Input
                          placeholder="Account"
                          value={line.account_name}
                          onChange={(e) => updateLine(line.id, 'account_name', e.target.value)}
                          className="flex-1"
                          required
                        />
                        <Input
                          type="number"
                          placeholder="Debit"
                          value={line.debit_amount || ''}
                          onChange={(e) => updateLine(line.id, 'debit_amount', parseFloat(e.target.value) || 0)}
                          className="w-28"
                        />
                        <Input
                          type="number"
                          placeholder="Credit"
                          value={line.credit_amount || ''}
                          onChange={(e) => updateLine(line.id, 'credit_amount', parseFloat(e.target.value) || 0)}
                          className="w-28"
                        />
                        {form.lines.length > 1 && (
                          <Button type="button" variant="ghost" size="icon" onClick={() => removeLine(line.id)}>
                            <Trash2 className="w-4 h-4 text-red-400" />
                          </Button>
                        )}
                      </div>
                    ))}
                  </div>
                </div>

                <div className="flex justify-end gap-2 pt-4">
                  <Button type="button" variant="outline" onClick={() => setShowForm(false)}>Cancel</Button>
                  <Button type="submit">Create Entry</Button>
                </div>
              </form>
            </CardContent>
          </Card>
        </div>
      )}
    </div>
  )
}
