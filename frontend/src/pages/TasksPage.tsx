import * as React from 'react'
import { Link } from 'react-router-dom'
import { Plus, Search, ListTodo, Filter, Calendar, User, Clock, AlertCircle, CheckCircle2 } from 'lucide-react'
import { apiFetch } from '@/api/client'
import type { Task } from '@/types'
import { Button } from '@/components/ui/button'
import { StatusBadge } from '@/components/ui/status-badge'
import { cn } from '@/lib/utils'

const priorityColors: Record<string, string> = {
  critical: 'text-red-500', high: 'text-orange-500', medium: 'text-yellow-500', low: 'text-muted-foreground',
}

const priorityLabels: Record<string, string> = {
  critical: 'Critical', high: 'High', medium: 'Medium', low: 'Low',
}

export function TasksPage() {
  const [tasks, setTasks] = React.useState<Task[]>([])
  const [loading, setLoading] = React.useState(true)
  const [search, setSearch] = React.useState('')
  const [filter, setFilter] = React.useState<string>('all')

  React.useEffect(() => { load() }, [])

  const load = async () => {
    setLoading(true)
    try { setTasks(await apiFetch('/tasks/')) } catch {} finally { setLoading(false) }
  }

  const filtered = tasks.filter((t) => {
    if (search && !t.name.toLowerCase().includes(search.toLowerCase())) return false
    if (filter !== 'all' && t.status !== filter) return false
    return true
  })

  const total = tasks.length
  const done = tasks.filter((t) => t.status === 'done').length
  const progress = total > 0 ? Math.round((done / total) * 100) : 0

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold tracking-tight">Tasks</h1>
          <p className="text-sm text-muted-foreground mt-1">{done}/{total} completed</p>
        </div>
        <Button>
          <Plus className="w-4 h-4 mr-1.5" />
          New Task
        </Button>
      </div>

      <div className="rounded-xl border bg-card p-5">
        <div className="flex items-center justify-between mb-2">
          <span className="text-sm font-medium">Overall Progress</span>
          <span className="text-sm text-muted-foreground">{progress}%</span>
        </div>
        <div className="h-2 rounded-full bg-muted overflow-hidden">
          <div
            className="h-full rounded-full bg-primary transition-all duration-500"
            style={{ width: `${progress}%` }}
          />
        </div>
      </div>

      <div className="flex items-center gap-3">
        <div className="relative flex-1 max-w-sm">
          <Search className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-muted-foreground" />
          <input className="w-full h-9 rounded-lg border bg-card pl-9 pr-3 text-sm placeholder:text-muted-foreground focus:outline-none focus:ring-1 focus:ring-ring" placeholder="Search tasks..." value={search} onChange={(e) => setSearch(e.target.value)} />
        </div>
        <div className="flex gap-1 rounded-lg border p-0.5">
          {['all', 'todo', 'in_progress', 'review', 'done'].map((s) => (
            <button key={s} onClick={() => setFilter(s)} className={cn('px-3 py-1.5 text-xs font-medium rounded-md transition-all', filter === s ? 'bg-primary text-primary-foreground' : 'text-muted-foreground hover:text-foreground')}>
              {s === 'in_progress' ? 'In Progress' : s.charAt(0).toUpperCase() + s.slice(1)}
            </button>
          ))}
        </div>
      </div>

      {loading ? (
        <div className="rounded-xl border divide-y divide-border">
          {Array.from({ length: 5 }).map((_, i) => (
            <div key={i} className="flex items-center gap-4 p-4">
              <div className="skeleton h-4 w-4 rounded" />
              <div className="skeleton h-4 flex-1" />
              <div className="skeleton h-5 w-16 rounded-full" />
              <div className="skeleton h-4 w-20" />
            </div>
          ))}
        </div>
      ) : filtered.length === 0 ? (
        <div className="flex flex-col items-center py-20 text-center rounded-xl border bg-card">
          <ListTodo className="w-12 h-12 text-muted-foreground mb-4" />
          <h3 className="text-lg font-medium mb-1">{search || filter !== 'all' ? 'No matching tasks' : 'No tasks yet'}</h3>
          <p className="text-sm text-muted-foreground">Create a task to get started</p>
        </div>
      ) : (
        <div className="rounded-xl border overflow-hidden">
          <table className="w-full">
            <thead>
              <tr className="border-b bg-muted/50">
                <th className="px-4 py-3 text-left text-xs font-medium text-muted-foreground uppercase tracking-wider w-8" />
                <th className="px-4 py-3 text-left text-xs font-medium text-muted-foreground uppercase tracking-wider">Task</th>
                <th className="px-4 py-3 text-left text-xs font-medium text-muted-foreground uppercase tracking-wider">Status</th>
                <th className="px-4 py-3 text-left text-xs font-medium text-muted-foreground uppercase tracking-wider">Priority</th>
                <th className="px-4 py-3 text-left text-xs font-medium text-muted-foreground uppercase tracking-wider">Due</th>
                <th className="px-4 py-3 text-left text-xs font-medium text-muted-foreground uppercase tracking-wider">Assignee</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-border">
              {filtered.map((t) => (
                <tr key={t.id} className="hover:bg-accent/50 transition-colors">
                  <td className="px-4 py-3">
                    <div className={cn('w-4 h-4 rounded border-2', t.status === 'done' ? 'bg-primary border-primary' : 'border-muted-foreground/30')}>
                      {t.status === 'done' && <CheckCircle2 className="w-3 h-3 text-primary-foreground" />}
                    </div>
                  </td>
                  <td className="px-4 py-3">
                    <Link to={`/tasks/${t.id}`} className="text-sm font-medium hover:text-primary transition-colors">
                      {t.name}
                    </Link>
                  </td>
                  <td className="px-4 py-3"><StatusBadge status={t.status} /></td>
                  <td className="px-4 py-3">
                    <span className={cn('text-xs font-medium', priorityColors[t.priority])}>
                      {priorityLabels[t.priority]}
                    </span>
                  </td>
                  <td className="px-4 py-3">
                    {t.due_date ? (
                      <span className="flex items-center gap-1.5 text-xs text-muted-foreground">
                        <Calendar className="w-3 h-3" />
                        {t.due_date}
                      </span>
                    ) : (
                      <span className="text-xs text-muted-foreground">—</span>
                    )}
                  </td>
                  <td className="px-4 py-3">
                    {t.assignee_id ? (
                      <div className="flex items-center gap-1.5 text-xs text-muted-foreground">
                        <User className="w-3 h-3" />
                        Assigned
                      </div>
                    ) : (
                      <span className="text-xs text-muted-foreground">Unassigned</span>
                    )}
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}
    </div>
  )
}
