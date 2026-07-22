import { useState, useEffect } from 'react'
import { useNavigate } from 'react-router-dom'
import { ArrowLeft, Plus, Trash2, GripVertical } from 'lucide-react'
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from '@/components/ui/card'
import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import { StatusBadge } from '@/components/ui/status-badge'
import { scorecardApi } from '@/api/scorecards'
import type { KpiDefinition } from '@/types'

export function KpiDefinitionsPage() {
  const navigate = useNavigate()
  const [definitions, setDefinitions] = useState<KpiDefinition[]>([])
  const [loading, setLoading] = useState(true)
  const [showForm, setShowForm] = useState(false)
  const [form, setForm] = useState({ name: '', category: 'custom', unit: '', description: '' })

  useEffect(() => {
    scorecardApi.definitions.list()
      .then(setDefinitions)
      .catch(() => {})
      .finally(() => setLoading(false))
  }, [])

  const handleCreate = async (e: React.FormEvent) => {
    e.preventDefault()
    try {
      const def = await scorecardApi.definitions.create(form)
      setDefinitions([...definitions, def])
      setShowForm(false)
      setForm({ name: '', category: 'custom', unit: '', description: '' })
    } catch (err: unknown) {
      console.error(err)
    }
  }

  const handleDelete = async (id: string) => {
    await scorecardApi.definitions.delete(id)
    setDefinitions(definitions.filter((d) => d.id !== id))
  }

  const byCategory = definitions.reduce<Record<string, KpiDefinition[]>>((acc, def) => {
    (acc[def.category] ||= []).push(def)
    return acc
  }, {})

  return (
    <div className="max-w-3xl space-y-6">
      <div className="flex items-center gap-4">
        <button onClick={() => navigate(-1)} className="text-muted-foreground hover:text-foreground">
          <ArrowLeft className="w-5 h-5" />
        </button>
        <div className="flex-1">
          <h1 className="text-3xl font-bold tracking-tight">KPI Definitions</h1>
          <p className="text-muted-foreground mt-1">
            Manage the KPIs that appear in your scorecards. Pre-built KPIs are auto-computed.
          </p>
        </div>
        <Button size="sm" className="gap-2" onClick={() => setShowForm(true)}>
          <Plus className="w-4 h-4" />
          Add KPI
        </Button>
      </div>

      {showForm && (
        <Card>
          <form onSubmit={handleCreate}>
            <CardContent className="space-y-4 pt-6">
              <div className="grid grid-cols-2 gap-4">
                <div>
                  <label className="text-sm font-medium block mb-1">Name</label>
                  <Input value={form.name} onChange={(e) => setForm({ ...form, name: e.target.value })} required />
                </div>
                <div>
                  <label className="text-sm font-medium block mb-1">Unit</label>
                  <Input placeholder="%, count, $, hours..." value={form.unit} onChange={(e) => setForm({ ...form, unit: e.target.value })} />
                </div>
              </div>
              <div>
                <label className="text-sm font-medium block mb-1">Category</label>
                <select
                  className="w-full rounded-md border bg-background px-3 py-2 text-sm"
                  value={form.category}
                  onChange={(e) => setForm({ ...form, category: e.target.value })}
                >
                  <option value="productivity">Productivity</option>
                  <option value="financial">Financial</option>
                  <option value="client_health">Client Health</option>
                  <option value="custom">Custom</option>
                </select>
              </div>
              <div>
                <label className="text-sm font-medium block mb-1">Description (optional)</label>
                <Input value={form.description} onChange={(e) => setForm({ ...form, description: e.target.value })} />
              </div>
              <div className="flex gap-2">
                <Button type="submit" size="sm">Save</Button>
                <Button type="button" variant="ghost" size="sm" onClick={() => setShowForm(false)}>Cancel</Button>
              </div>
            </CardContent>
          </form>
        </Card>
      )}

      {loading ? (
        <div className="flex items-center justify-center h-32">
          <div className="animate-spin rounded-full h-6 w-6 border-b-2 border-primary" />
        </div>
      ) : (
        Object.entries(byCategory).map(([category, defs]) => (
          <div key={category}>
            <h2 className="text-sm font-medium text-muted-foreground uppercase tracking-wider mb-3">
              {category.replace('_', ' ')}
            </h2>
            <div className="space-y-2">
              {defs.map((def) => (
                <Card key={def.id}>
                  <CardContent className="flex items-center gap-3 py-3">
                    <div className="flex-1">
                      <div className="flex items-center gap-2">
                        <span className="font-medium">{def.name}</span>
                        <StatusBadge status={def.category === 'custom' ? 'todo' : def.category} label={def.category.replace('_', ' ')} />
                        {def.is_prebuilt && (
                          <StatusBadge status="todo" label="Auto" />
                        )}
                      </div>
                      {def.description && (
                        <p className="text-xs text-muted-foreground mt-0.5">{def.description}</p>
                      )}
                    </div>
                    <span className="text-xs text-muted-foreground">{def.unit}</span>
                    {!def.is_prebuilt && (
                      <Button variant="ghost" size="icon" onClick={() => handleDelete(def.id)}>
                        <Trash2 className="w-3.5 h-3.5 text-muted-foreground" />
                      </Button>
                    )}
                  </CardContent>
                </Card>
              ))}
            </div>
          </div>
        ))
      )}

      {definitions.length === 0 && !loading && (
        <Card className="p-12 text-center">
          <h3 className="text-lg font-medium mb-2">No KPIs defined</h3>
          <p className="text-muted-foreground mb-4">
            Pre-built KPIs are auto-seeded when your organization is created.
          </p>
        </Card>
      )}
    </div>
  )
}
