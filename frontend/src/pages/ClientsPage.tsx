import * as React from 'react'
import { Link } from 'react-router-dom'
import { Plus, Search, Users, Building2, MoreHorizontal, ChevronDown } from 'lucide-react'
import { apiFetch } from '@/api/client'
import type { Client } from '@/types'
import { Button } from '@/components/ui/button'
import { StatusBadge } from '@/components/ui/status-badge'
import { cn } from '@/lib/utils'

const entityTypeLabels: Record<string, string> = {
  llc: 'LLC', corp: 'Corporation', sole_prop: 'Sole Prop',
  private_limited: 'Pvt Ltd', public_limited: 'Public Ltd',
  limited_liability_partnership: 'LLP', partnership_firm: 'Partnership',
  sole_proprietorship: 'Sole Prop', one_person_company: 'OPC',
  section_8_company: 'Section 8', hindu_undivided_family: 'HUF',
  trust: 'Trust', cooperative_society: 'Co-op',
  government_body: 'Govt', foreign_company: 'Foreign Co.',
}

export function ClientsPage() {
  const [clients, setClients] = React.useState<Client[]>([])
  const [loading, setLoading] = React.useState(true)
  const [search, setSearch] = React.useState('')
  const [showModal, setShowModal] = React.useState(false)
  const [editingClient, setEditingClient] = React.useState<Client | null>(null)
  const [form, setForm] = React.useState({ name: '', entity_type: 'private_limited', status: 'active', close_day: 1, properties: '{}' })

  React.useEffect(() => { load() }, [])

  const load = async () => {
    setLoading(true)
    try { setClients(await apiFetch('/clients/')) } catch {} finally { setLoading(false) }
  }

  const filtered = clients.filter((c) =>
    c.name.toLowerCase().includes(search.toLowerCase()) ||
    c.entity_type?.toLowerCase().includes(search.toLowerCase())
  )

  const openEdit = (c: Client) => {
    setEditingClient(c)
    setForm({ name: c.name, entity_type: c.entity_type, status: c.status, close_day: c.close_day || 1, properties: JSON.stringify(c.properties || {}, null, 2) })
    setShowModal(true)
  }

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    let properties: Record<string, unknown> = {}
    try { properties = JSON.parse(form.properties) } catch {}
    const payload = { name: form.name, entity_type: form.entity_type, status: form.status, close_day: form.close_day, properties }
    if (editingClient) await apiFetch(`/clients/${editingClient.id}`, { method: 'PUT', body: JSON.stringify(payload) })
    else await apiFetch('/clients/', { method: 'POST', body: JSON.stringify(payload) })
    setShowModal(false)
    load()
  }

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold tracking-tight">Clients</h1>
          <p className="text-sm text-muted-foreground mt-1">{clients.length} client{clients.length !== 1 ? 's' : ''}</p>
        </div>
        <Button onClick={() => { setEditingClient(null); setForm({ name: '', entity_type: 'private_limited', status: 'active', close_day: 1, properties: '{}' }); setShowModal(true) }}>
          <Plus className="w-4 h-4 mr-1.5" />
          Add Client
        </Button>
      </div>

      <div className="flex items-center gap-3">
        <div className="relative flex-1 max-w-sm">
          <Search className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-muted-foreground" />
          <input
            className="w-full h-9 rounded-lg border bg-card pl-9 pr-3 text-sm placeholder:text-muted-foreground focus:outline-none focus:ring-1 focus:ring-ring"
            placeholder="Search clients..."
            value={search}
            onChange={(e) => setSearch(e.target.value)}
          />
        </div>
      </div>

      {loading ? (
        <div className="rounded-xl border divide-y divide-border">
          {Array.from({ length: 5 }).map((_, i) => (
            <div key={i} className="flex items-center gap-4 p-4">
              <div className="skeleton h-8 w-8 rounded-full" />
              <div className="skeleton h-4 flex-1" />
              <div className="skeleton h-4 w-20" />
              <div className="skeleton h-4 w-16" />
            </div>
          ))}
        </div>
      ) : filtered.length === 0 ? (
        <div className="flex flex-col items-center py-20 text-center rounded-xl border bg-card">
          <Building2 className="w-12 h-12 text-muted-foreground mb-4" />
          <h3 className="text-lg font-medium mb-1">{search ? 'No matching clients' : 'No clients yet'}</h3>
          <p className="text-sm text-muted-foreground mb-4">
            {search ? 'Try a different search term' : 'Add your first client to get started'}
          </p>
          {!search && (
            <Button onClick={() => setShowModal(true)}>
              <Plus className="w-4 h-4 mr-1.5" />
              Add Client
            </Button>
          )}
        </div>
      ) : (
        <div className="rounded-xl border overflow-hidden">
          <table className="w-full">
            <thead>
              <tr className="border-b bg-muted/50">
                <th className="px-4 py-3 text-left text-xs font-medium text-muted-foreground uppercase tracking-wider">Name</th>
                <th className="px-4 py-3 text-left text-xs font-medium text-muted-foreground uppercase tracking-wider">Type</th>
                <th className="px-4 py-3 text-left text-xs font-medium text-muted-foreground uppercase tracking-wider">Status</th>
                <th className="px-4 py-3 text-left text-xs font-medium text-muted-foreground uppercase tracking-wider">Close Day</th>
                <th className="px-4 py-3 w-16" />
              </tr>
            </thead>
            <tbody className="divide-y divide-border">
              {filtered.map((c) => (
                <tr key={c.id} className="hover:bg-accent/50 transition-colors">
                  <td className="px-4 py-3">
                    <Link to={`/clients/${c.id}`} className="flex items-center gap-3">
                      <div className="flex items-center justify-center w-8 h-8 rounded-full bg-primary/10 text-primary text-xs font-bold shrink-0">
                        {c.name.charAt(0).toUpperCase()}
                      </div>
                      <span className="text-sm font-medium">{c.name}</span>
                    </Link>
                  </td>
                  <td className="px-4 py-3 text-sm text-muted-foreground">{entityTypeLabels[c.entity_type] || c.entity_type}</td>
                  <td className="px-4 py-3"><StatusBadge status={c.status} /></td>
                  <td className="px-4 py-3 text-sm text-muted-foreground">{c.close_day || 1}</td>
                  <td className="px-4 py-3">
                    <Button variant="ghost" size="icon" className="w-7 h-7" onClick={() => openEdit(c)}>
                      <MoreHorizontal className="w-4 h-4" />
                    </Button>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}

      {showModal && (
        <div className="fixed inset-0 z-50 flex items-start justify-center pt-[15vh] bg-black/60 backdrop-blur-sm">
          <div className="w-full max-w-lg mx-4 rounded-xl border bg-card shadow-2xl">
            <div className="px-6 py-4 border-b">
              <h2 className="text-lg font-semibold">{editingClient ? 'Edit Client' : 'Add Client'}</h2>
            </div>
            <form onSubmit={handleSubmit} className="p-6 space-y-4">
              <div>
                <label className="text-sm font-medium block mb-1.5">Client Name</label>
                <input className="w-full h-9 rounded-lg border bg-background px-3 text-sm focus:outline-none focus:ring-1 focus:ring-ring" value={form.name} onChange={(e) => setForm((f) => ({ ...f, name: e.target.value }))} required />
              </div>
              <div>
                <label className="text-sm font-medium block mb-1.5">Entity Type</label>
                <select className="w-full h-9 rounded-lg border bg-background px-3 text-sm focus:outline-none focus:ring-1 focus:ring-ring" value={form.entity_type} onChange={(e) => setForm((f) => ({ ...f, entity_type: e.target.value }))}>
                  <option value="private_limited">Private Limited</option>
                  <option value="public_limited">Public Limited</option>
                  <option value="limited_liability_partnership">LLP</option>
                  <option value="partnership_firm">Partnership Firm</option>
                  <option value="sole_proprietorship">Sole Proprietorship</option>
                  <option value="one_person_company">OPC</option>
                  <option value="section_8_company">Section 8 Company</option>
                  <option value="hindu_undivided_family">HUF</option>
                  <option value="trust">Trust</option>
                  <option value="cooperative_society">Cooperative Society</option>
                  <option value="government_body">Government Body</option>
                  <option value="foreign_company">Foreign Company</option>
                </select>
              </div>
              <div>
                <label className="text-sm font-medium block mb-1.5">Status</label>
                <select className="w-full h-9 rounded-lg border bg-background px-3 text-sm focus:outline-none focus:ring-1 focus:ring-ring" value={form.status} onChange={(e) => setForm((f) => ({ ...f, status: e.target.value }))}>
                  <option value="active">Active</option>
                  <option value="inactive">Inactive</option>
                  <option value="quarterly">Quarterly</option>
                </select>
              </div>
              <div>
                <label className="text-sm font-medium block mb-1.5">Close Day</label>
                <input type="number" min={1} max={31} className="w-full h-9 rounded-lg border bg-background px-3 text-sm focus:outline-none focus:ring-1 focus:ring-ring" value={form.close_day} onChange={(e) => setForm((f) => ({ ...f, close_day: parseInt(e.target.value) || 1 }))} />
              </div>
              <div className="flex justify-end gap-2 pt-2">
                <Button type="button" variant="outline" onClick={() => setShowModal(false)}>Cancel</Button>
                <Button type="submit">{editingClient ? 'Update' : 'Create'}</Button>
              </div>
            </form>
          </div>
        </div>
      )}
    </div>
  )
}
