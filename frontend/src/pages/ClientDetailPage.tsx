import { useState, useEffect } from 'react'
import { useParams, Link } from 'react-router-dom'
import { ArrowLeft, Pencil, Save } from 'lucide-react'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import { StatusBadge } from '@/components/ui/status-badge'
import { apiFetch } from '@/api/client'
import type { Client, ClientDashboard, TaskList } from '@/types'

type Tab = 'overview' | 'tasks' | 'dashboard'

export function ClientDetailPage() {
  const { id } = useParams<{ id: string }>()
  const [client, setClient] = useState<Client | null>(null)
  const [dashboard, setDashboard] = useState<ClientDashboard | null>(null)
  const [taskLists, setTaskLists] = useState<TaskList[]>([])
  const [loading, setLoading] = useState(true)
  const [activeTab, setActiveTab] = useState<Tab>('overview')
  const [editing, setEditing] = useState(false)
  const [form, setForm] = useState({ name: '', entity_type: 'llc', status: 'active', close_day: 1 })

  const load = async () => {
    if (!id) return
    setLoading(true)
    try {
      const [c, d, tl] = await Promise.all([
        apiFetch<Client>(`/clients/${id}`),
        apiFetch<ClientDashboard>(`/clients/${id}/dashboard`),
        apiFetch<TaskList[]>(`/task-lists/?client_id=${id}`),
      ])
      setClient(c)
      setDashboard(d)
      setTaskLists(tl)
      setForm({ name: c.name, entity_type: c.entity_type, status: c.status, close_day: c.close_day || 1 })
    } catch {} finally {
      setLoading(false)
    }
  }

  useEffect(() => { load() }, [id])

  const handleSave = async () => {
    if (!id || !client) return
    await apiFetch(`/clients/${id}`, {
      method: 'PUT',
      body: JSON.stringify(form),
    })
    setEditing(false)
    load()
  }

  if (loading) {
    return (
      <div className="space-y-4">
        <div className="flex items-center gap-4">
          <div className="skeleton h-5 w-5 rounded" />
          <div className="skeleton h-8 w-64 rounded-lg flex-1" />
          <div className="skeleton h-6 w-20 rounded-full" />
        </div>
        <div className="skeleton h-10 w-full rounded-xl" />
        <div className="skeleton h-64 w-full rounded-xl" />
      </div>
    )
  }

  if (!client) return null

  return (
    <div className="space-y-6">
      <div className="flex items-center gap-4">
        <Link to="/clients" className="text-muted-foreground hover:text-foreground">
          <ArrowLeft className="w-5 h-5" />
        </Link>
        <div className="flex-1">
          <h1 className="text-3xl font-bold tracking-tight">{client.name}</h1>
        </div>
        <StatusBadge status={client.status} />
        <Link to={`/clients/${id}/close`}>
          <Button variant="outline" size="sm">Close Page</Button>
        </Link>
      </div>

      <div className="flex gap-1 border-b">
        {(['overview', 'tasks', 'dashboard'] as Tab[]).map((tab) => (
          <button
            key={tab}
            onClick={() => setActiveTab(tab)}
            className={`px-4 py-2 text-sm font-medium border-b-2 transition-colors ${
              activeTab === tab
                ? 'border-primary text-primary'
                : 'border-transparent text-muted-foreground hover:text-foreground'
            }`}
          >
            {tab.charAt(0).toUpperCase() + tab.slice(1)}
          </button>
        ))}
      </div>

      {activeTab === 'overview' && (
        <Card>
          <CardHeader className="flex flex-row items-center justify-between">
            <CardTitle>Client Information</CardTitle>
            {!editing ? (
              <Button variant="outline" size="sm" onClick={() => setEditing(true)}>
                <Pencil className="w-4 h-4 mr-1" /> Edit
              </Button>
            ) : (
              <Button size="sm" onClick={handleSave}>
                <Save className="w-4 h-4 mr-1" /> Save
              </Button>
            )}
          </CardHeader>
          <CardContent>
            {editing ? (
              <div className="space-y-4 max-w-md">
                <div>
                  <label className="text-sm font-medium block mb-1">Name</label>
                  <Input value={form.name} onChange={(e) => setForm((f) => ({ ...f, name: e.target.value }))} />
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
                  <Input type="number" min={1} max={31} value={form.close_day} onChange={(e) => setForm((f) => ({ ...f, close_day: parseInt(e.target.value) || 1 }))} />
                </div>
              </div>
            ) : (
              <div className="grid grid-cols-2 gap-4 max-w-md">
                <div>
                  <p className="text-sm text-muted-foreground">Entity Type</p>
                  <p className="font-medium">{client.entity_type}</p>
                </div>
                <div>
                  <p className="text-sm text-muted-foreground">Close Day</p>
                  <p className="font-medium">{client.close_day || 1}</p>
                </div>
              </div>
            )}
          </CardContent>
        </Card>
      )}

      {activeTab === 'tasks' && (
        <Card>
          <CardHeader>
            <CardTitle>Task Lists</CardTitle>
          </CardHeader>
          <CardContent>
            {taskLists.length === 0 ? (
              <p className="text-sm text-muted-foreground">No task lists for this client.</p>
            ) : (
              <div className="space-y-2">
                {taskLists.map((tl) => (
                  <Link
                    key={tl.id}
                    to={`/tasks?client_id=${tl.client_id}&list_id=${tl.id}`}
                    className="flex items-center gap-3 p-3 rounded-lg border hover:border-primary/50 transition-colors"
                  >
                    <span className="font-medium">{tl.name}</span>
                    {tl.is_template && <StatusBadge status="todo" label="Template" />}
                  </Link>
                ))}
              </div>
            )}
          </CardContent>
        </Card>
      )}

      {activeTab === 'dashboard' && (
        <div className="grid grid-cols-3 gap-4">
          <Card>
            <CardHeader className="pb-2">
              <p className="text-sm text-muted-foreground">Tasks</p>
              <p className="text-2xl font-bold">{dashboard?.completed_tasks || 0}/{dashboard?.task_count || 0}</p>
            </CardHeader>
          </Card>
          <Card>
            <CardHeader className="pb-2">
              <p className="text-sm text-muted-foreground">Bank Transactions</p>
              <p className="text-2xl font-bold">{dashboard?.bank_transaction_count || 0}</p>
            </CardHeader>
          </Card>
          <Card>
            <CardHeader className="pb-2">
              <p className="text-sm text-muted-foreground">Journal Entries</p>
              <p className="text-2xl font-bold">{dashboard?.journal_entry_count || 0}</p>
            </CardHeader>
          </Card>
        </div>
      )}
    </div>
  )
}
