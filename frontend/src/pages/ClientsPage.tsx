import { useState, useEffect } from 'react'
import { Link } from 'react-router-dom'
import { Plus, Search, Pencil, Users, X } from 'lucide-react'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import { Badge } from '@/components/ui/badge'
import { apiFetch } from '@/api/client'
import type { Client } from '@/types'

const entityTypeLabels: Record<string, string> = {
  llc: 'LLC',
  corp: 'Corporation',
  sole_prop: 'Sole Proprietorship',
}

const statusConfig: Record<string, { label: string; variant: 'success' | 'warning' | 'outline' }> = {
  active: { label: 'Active', variant: 'success' },
  inactive: { label: 'Inactive', variant: 'outline' },
  quarterly: { label: 'Quarterly', variant: 'warning' },
}

export function ClientsPage() {
  const [clients, setClients] = useState<Client[]>([])
  const [loading, setLoading] = useState(true)
  const [search, setSearch] = useState('')
  const [showModal, setShowModal] = useState(false)
  const [editingClient, setEditingClient] = useState<Client | null>(null)

  const [form, setForm] = useState({
    name: '',
    entity_type: 'llc',
    status: 'active',
    close_day: 1,
    properties: '{}',
  })

  const load = async () => {
    setLoading(true)
    try {
      const data = await apiFetch<Client[]>('/clients/')
      setClients(data)
    } catch {} finally {
      setLoading(false)
    }
  }

  useEffect(() => { load() }, [])

  const filtered = clients.filter((c) =>
    c.name.toLowerCase().includes(search.toLowerCase())
  )

  const openCreate = () => {
    setEditingClient(null)
    setForm({ name: '', entity_type: 'llc', status: 'active', close_day: 1, properties: '{}' })
    setShowModal(true)
  }

  const openEdit = (c: Client) => {
    setEditingClient(c)
    setForm({
      name: c.name,
      entity_type: c.entity_type,
      status: c.status,
      close_day: c.close_day || 1,
      properties: JSON.stringify(c.properties || {}, null, 2),
    })
    setShowModal(true)
  }

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    let properties: Record<string, unknown> = {}
    try { properties = JSON.parse(form.properties) } catch {}

    const payload = {
      name: form.name,
      entity_type: form.entity_type,
      status: form.status,
      close_day: form.close_day,
      properties,
    }

    if (editingClient) {
      await apiFetch(`/clients/${editingClient.id}`, {
        method: 'PUT',
        body: JSON.stringify(payload),
      })
    } else {
      await apiFetch('/clients/', {
        method: 'POST',
        body: JSON.stringify(payload),
      })
    }
    setShowModal(false)
    load()
  }

  const handleDeactivate = async (id: string) => {
    await apiFetch(`/clients/${id}`, { method: 'DELETE' })
    load()
  }

  if (loading) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-primary" />
      </div>
    )
  }

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold tracking-tight">Clients</h1>
          <p className="text-muted-foreground mt-1">Manage your client portfolio.</p>
        </div>
        <Button size="sm" className="gap-2" onClick={openCreate}>
          <Plus className="w-4 h-4" />
          Create Client
        </Button>
      </div>

      <div className="flex items-center gap-2">
        <div className="relative flex-1 max-w-md">
          <Search className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-muted-foreground" />
          <Input
            placeholder="Search clients..."
            value={search}
            onChange={(e) => setSearch(e.target.value)}
            className="pl-9"
          />
        </div>
      </div>

      {filtered.length === 0 ? (
        <Card className="p-12 text-center">
          <Users className="w-12 h-12 mx-auto text-muted-foreground mb-4" />
          <h3 className="text-lg font-medium mb-2">No clients yet</h3>
          <p className="text-muted-foreground mb-4">
            Add your first client to start managing their books.
          </p>
          <Button className="gap-2" onClick={openCreate}>
            <Plus className="w-4 h-4" />
            Create Client
          </Button>
        </Card>
      ) : (
        <Card>
          <div className="overflow-x-auto">
            <table className="w-full">
              <thead>
                <tr className="border-b text-left">
                  <th className="p-3 text-sm font-medium text-muted-foreground">Name</th>
                  <th className="p-3 text-sm font-medium text-muted-foreground">Entity Type</th>
                  <th className="p-3 text-sm font-medium text-muted-foreground">Status</th>
                  <th className="p-3 text-sm font-medium text-muted-foreground">Close Day</th>
                  <th className="p-3 text-sm font-medium text-muted-foreground">Actions</th>
                </tr>
              </thead>
              <tbody>
                {filtered.map((c) => (
                  <tr key={c.id} className="border-b last:border-0 hover:bg-muted/50 transition-colors">
                    <td className="p-3">
                      <Link to={`/clients/${c.id}`} className="font-medium hover:text-primary transition-colors">
                        {c.name}
                      </Link>
                    </td>
                    <td className="p-3 text-sm text-muted-foreground">
                      {entityTypeLabels[c.entity_type] || c.entity_type}
                    </td>
                    <td className="p-3">
                      <Badge variant={statusConfig[c.status]?.variant || 'outline'}>
                        {statusConfig[c.status]?.label || c.status}
                      </Badge>
                    </td>
                    <td className="p-3 text-sm text-muted-foreground">{c.close_day || 1}</td>
                    <td className="p-3">
                      <div className="flex items-center gap-1">
                        <Button variant="ghost" size="icon" onClick={() => openEdit(c)}>
                          <Pencil className="w-4 h-4" />
                        </Button>
                        <Button variant="ghost" size="icon" onClick={() => handleDeactivate(c.id)}>
                          <X className="w-4 h-4" />
                        </Button>
                      </div>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </Card>
      )}

      {showModal && (
        <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/50">
          <Card className="w-full max-w-lg mx-4">
            <CardHeader>
              <CardTitle>{editingClient ? 'Edit Client' : 'Create Client'}</CardTitle>
            </CardHeader>
            <CardContent>
              <form onSubmit={handleSubmit} className="space-y-4">
                <div>
                  <label className="text-sm font-medium block mb-1">Name</label>
                  <Input
                    value={form.name}
                    onChange={(e) => setForm((f) => ({ ...f, name: e.target.value }))}
                    required
                  />
                </div>
                <div>
                  <label className="text-sm font-medium block mb-1">Entity Type</label>
                  <select
                    className="flex h-9 w-full rounded-md border border-input bg-background px-3 py-1 text-sm shadow-sm focus-visible:outline-none focus-visible:ring-1 focus-visible:ring-ring"
                    value={form.entity_type}
                    onChange={(e) => setForm((f) => ({ ...f, entity_type: e.target.value }))}
                  >
                    <option value="llc">LLC</option>
                    <option value="corp">Corporation</option>
                    <option value="sole_prop">Sole Proprietorship</option>
                  </select>
                </div>
                <div>
                  <label className="text-sm font-medium block mb-1">Status</label>
                  <select
                    className="flex h-9 w-full rounded-md border border-input bg-background px-3 py-1 text-sm shadow-sm focus-visible:outline-none focus-visible:ring-1 focus-visible:ring-ring"
                    value={form.status}
                    onChange={(e) => setForm((f) => ({ ...f, status: e.target.value }))}
                  >
                    <option value="active">Active</option>
                    <option value="inactive">Inactive</option>
                    <option value="quarterly">Quarterly</option>
                  </select>
                </div>
                <div>
                  <label className="text-sm font-medium block mb-1">Close Day</label>
                  <Input
                    type="number"
                    min={1}
                    max={31}
                    value={form.close_day}
                    onChange={(e) => setForm((f) => ({ ...f, close_day: parseInt(e.target.value) || 1 }))}
                  />
                </div>
                <div>
                  <label className="text-sm font-medium block mb-1">Properties (JSON)</label>
                  <textarea
                    className="flex w-full rounded-md border border-input bg-background px-3 py-2 text-sm shadow-sm placeholder:text-muted-foreground focus-visible:outline-none focus-visible:ring-1 focus-visible:ring-ring min-h-[100px] font-mono"
                    value={form.properties}
                    onChange={(e) => setForm((f) => ({ ...f, properties: e.target.value }))}
                  />
                </div>
                <div className="flex justify-end gap-2">
                  <Button type="button" variant="outline" onClick={() => setShowModal(false)}>
                    Cancel
                  </Button>
                  <Button type="submit">
                    {editingClient ? 'Update' : 'Create'}
                  </Button>
                </div>
              </form>
            </CardContent>
          </Card>
        </div>
      )}
    </div>
  )
}
