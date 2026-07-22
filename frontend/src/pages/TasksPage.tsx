import { useState, useEffect } from 'react'
import { Link } from 'react-router-dom'
import { Plus, Search, ChevronRight, CheckCircle2, Circle, Clock, AlertCircle, User } from 'lucide-react'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import { Badge } from '@/components/ui/badge'
import { apiFetch } from '@/api/client'
import { cn } from '@/lib/utils'
import type { Task, TaskList, Client } from '@/types'

const statusConfig: Record<string, { label: string; variant: 'success' | 'warning' | 'outline' | 'danger' }> = {
  todo: { label: 'To Do', variant: 'outline' },
  in_progress: { label: 'In Progress', variant: 'warning' },
  review: { label: 'Review', variant: 'danger' },
  done: { label: 'Done', variant: 'success' },
}

const priorityColors: Record<string, string> = {
  low: 'text-muted-foreground',
  medium: 'text-blue-400',
  high: 'text-amber-400',
  critical: 'text-red-400',
}

const priorityBadges: Record<string, string> = {
  low: 'bg-muted',
  medium: 'bg-blue-500/20',
  high: 'bg-amber-500/20',
  critical: 'bg-red-500/20',
}

const statusIcons: Record<string, React.ElementType> = {
  todo: Circle,
  in_progress: Clock,
  review: AlertCircle,
  done: CheckCircle2,
}

const statusIconColors: Record<string, string> = {
  todo: 'text-muted-foreground',
  in_progress: 'text-blue-400',
  review: 'text-amber-400',
  done: 'text-emerald-400',
}

export function TasksPage() {
  const [tasks, setTasks] = useState<Task[]>([])
  const [taskLists, setTaskLists] = useState<TaskList[]>([])
  const [clients, setClients] = useState<Client[]>([])
  const [loading, setLoading] = useState(true)
  const [search, setSearch] = useState('')
  const [selectedClientId, setSelectedClientId] = useState('')
  const [selectedListId, setSelectedListId] = useState('')
  const [selectedTask, setSelectedTask] = useState<Task | null>(null)
  const [showCreate, setShowCreate] = useState(false)
  const [createForm, setCreateForm] = useState({
    name: '',
    task_list_id: '',
    priority: 'medium',
    status: 'todo',
    due_date: '',
    description: '',
  })

  const load = async () => {
    setLoading(true)
    try {
      const [t, cl, tl] = await Promise.all([
        apiFetch<Task[]>('/tasks/'),
        apiFetch<Client[]>('/clients/'),
        apiFetch<TaskList[]>('/task-lists/'),
      ])
      setTasks(t)
      setClients(cl)
      setTaskLists(tl)
    } catch {} finally {
      setLoading(false)
    }
  }

  useEffect(() => { load() }, [])

  const handleCreate = async (e: React.FormEvent) => {
    e.preventDefault()
    await apiFetch('/tasks/', {
      method: 'POST',
      body: JSON.stringify(createForm),
    })
    setShowCreate(false)
    setCreateForm({ name: '', task_list_id: '', priority: 'medium', status: 'todo', due_date: '', description: '' })
    load()
  }

  const filtered = tasks.filter((t) => {
    if (selectedClientId) {
      const list = taskLists.find((l) => l.id === t.task_list_id)
      if (!list || list.client_id !== selectedClientId) return false
    }
    if (selectedListId && t.task_list_id !== selectedListId) return false
    if (search && !t.name.toLowerCase().includes(search.toLowerCase())) return false
    return true
  })

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
          <h1 className="text-3xl font-bold tracking-tight">Tasks</h1>
          <p className="text-muted-foreground mt-1">Manage tasks across all clients.</p>
        </div>
        <Button size="sm" className="gap-2" onClick={() => setShowCreate(true)}>
          <Plus className="w-4 h-4" />
          New Task
        </Button>
      </div>

      <div className="flex items-center gap-3 flex-wrap">
        <div className="relative flex-1 max-w-sm">
          <Search className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-muted-foreground" />
          <Input
            placeholder="Search tasks..."
            value={search}
            onChange={(e) => setSearch(e.target.value)}
            className="pl-9"
          />
        </div>
        <select
          className="flex h-9 rounded-md border border-input bg-background px-3 py-1 text-sm shadow-sm focus-visible:outline-none focus-visible:ring-1 focus-visible:ring-ring"
          value={selectedClientId}
          onChange={(e) => setSelectedClientId(e.target.value)}
        >
          <option value="">All Clients</option>
          {clients.map((c) => (
            <option key={c.id} value={c.id}>{c.name}</option>
          ))}
        </select>
        <select
          className="flex h-9 rounded-md border border-input bg-background px-3 py-1 text-sm shadow-sm focus-visible:outline-none focus-visible:ring-1 focus-visible:ring-ring"
          value={selectedListId}
          onChange={(e) => setSelectedListId(e.target.value)}
        >
          <option value="">All Lists</option>
          {taskLists.map((l) => (
            <option key={l.id} value={l.id}>{l.name}</option>
          ))}
        </select>
      </div>

      {filtered.length === 0 ? (
        <Card className="p-12 text-center">
          <Circle className="w-12 h-12 mx-auto text-muted-foreground mb-4" />
          <h3 className="text-lg font-medium mb-2">No tasks found</h3>
          <p className="text-muted-foreground">Tasks will appear here when created for your clients.</p>
        </Card>
      ) : (
        <Card>
          <div className="overflow-x-auto">
            <table className="w-full">
              <thead>
                <tr className="border-b text-left">
                  <th className="p-3 text-sm font-medium text-muted-foreground w-10"></th>
                  <th className="p-3 text-sm font-medium text-muted-foreground">Name</th>
                  <th className="p-3 text-sm font-medium text-muted-foreground">Status</th>
                  <th className="p-3 text-sm font-medium text-muted-foreground">Priority</th>
                  <th className="p-3 text-sm font-medium text-muted-foreground">Assignee</th>
                  <th className="p-3 text-sm font-medium text-muted-foreground">Due Date</th>
                </tr>
              </thead>
              <tbody>
                {filtered.map((task) => {
                  const Icon = statusIcons[task.status] || Circle
                  return (
                    <tr
                      key={task.id}
                      className="border-b last:border-0 hover:bg-muted/50 transition-colors cursor-pointer"
                      onClick={() => setSelectedTask(task)}
                    >
                      <td className="p-3">
                        <Icon className={cn('w-4 h-4', statusIconColors[task.status])} />
                      </td>
                      <td className="p-3">
                        <span className={cn('font-medium', task.status === 'done' && 'line-through text-muted-foreground')}>
                          {task.name}
                        </span>
                      </td>
                      <td className="p-3">
                        <Badge variant={statusConfig[task.status]?.variant || 'outline'}>
                          {statusConfig[task.status]?.label || task.status}
                        </Badge>
                      </td>
                      <td className="p-3">
                        <span className={cn('text-xs font-medium px-2 py-0.5 rounded', priorityBadges[task.priority], priorityColors[task.priority])}>
                          {task.priority}
                        </span>
                      </td>
                      <td className="p-3">
                        <div className="flex items-center gap-2 text-sm text-muted-foreground">
                          <User className="w-3.5 h-3.5" />
                          {task.assignee_id ? 'Assigned' : 'Unassigned'}
                        </div>
                      </td>
                      <td className="p-3 text-sm text-muted-foreground">
                        {task.due_date ? new Date(task.due_date).toLocaleDateString() : '—'}
                      </td>
                    </tr>
                  )
                })}
              </tbody>
            </table>
          </div>
        </Card>
      )}

      {selectedTask && (
        <div className="fixed inset-0 z-50 flex">
          <div className="absolute inset-0 bg-black/50" onClick={() => setSelectedTask(null)} />
          <div className="relative ml-auto w-full max-w-lg bg-card border-l h-full overflow-y-auto p-6 space-y-6">
            <div className="flex items-center justify-between">
              <h2 className="text-xl font-bold">{selectedTask.name}</h2>
              <Button variant="ghost" size="icon" onClick={() => setSelectedTask(null)}>
                <ChevronRight className="w-5 h-5" />
              </Button>
            </div>
            {selectedTask.description && (
              <p className="text-sm text-muted-foreground">{selectedTask.description}</p>
            )}
            <div className="flex items-center gap-4 text-sm">
              <div>
                <p className="text-muted-foreground">Status</p>
                <Badge variant={statusConfig[selectedTask.status]?.variant || 'outline'}>
                  {statusConfig[selectedTask.status]?.label || selectedTask.status}
                </Badge>
              </div>
              <div>
                <p className="text-muted-foreground">Priority</p>
                <p className={priorityColors[selectedTask.priority]}>{selectedTask.priority}</p>
              </div>
              <div>
                <p className="text-muted-foreground">Due Date</p>
                <p>{selectedTask.due_date ? new Date(selectedTask.due_date).toLocaleDateString() : '—'}</p>
              </div>
            </div>
            {selectedTask.tags && selectedTask.tags.length > 0 && (
              <div className="flex gap-1 flex-wrap">
                {selectedTask.tags.map((tag) => (
                  <Badge key={tag} variant="secondary">{tag}</Badge>
                ))}
              </div>
            )}
            <Link to={`/tasks/${selectedTask.id}`}>
              <Button variant="outline" className="w-full">View Full Details</Button>
            </Link>
          </div>
        </div>
      )}

      {showCreate && (
        <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/50">
          <Card className="w-full max-w-lg mx-4">
            <CardHeader><CardTitle>New Task</CardTitle></CardHeader>
            <CardContent>
              <form onSubmit={handleCreate} className="space-y-4">
                <div>
                  <label className="text-sm font-medium block mb-1">Task Name</label>
                  <Input value={createForm.name} onChange={(e) => setCreateForm((f) => ({ ...f, name: e.target.value }))} required />
                </div>
                <div>
                  <label className="text-sm font-medium block mb-1">Task List</label>
                  <select
                    className="flex h-9 w-full rounded-md border border-input bg-background px-3 py-1 text-sm shadow-sm focus-visible:outline-none focus-visible:ring-1 focus-visible:ring-ring"
                    value={createForm.task_list_id}
                    onChange={(e) => setCreateForm((f) => ({ ...f, task_list_id: e.target.value }))}
                    required
                  >
                    <option value="">Select task list</option>
                    {taskLists.map((l) => (
                      <option key={l.id} value={l.id}>{l.name}</option>
                    ))}
                  </select>
                </div>
                <div className="grid grid-cols-2 gap-4">
                  <div>
                    <label className="text-sm font-medium block mb-1">Priority</label>
                    <select
                      className="flex h-9 w-full rounded-md border border-input bg-background px-3 py-1 text-sm shadow-sm focus-visible:outline-none focus-visible:ring-1 focus-visible:ring-ring"
                      value={createForm.priority}
                      onChange={(e) => setCreateForm((f) => ({ ...f, priority: e.target.value }))}
                    >
                      <option value="low">Low</option>
                      <option value="medium">Medium</option>
                      <option value="high">High</option>
                      <option value="critical">Critical</option>
                    </select>
                  </div>
                  <div>
                    <label className="text-sm font-medium block mb-1">Status</label>
                    <select
                      className="flex h-9 w-full rounded-md border border-input bg-background px-3 py-1 text-sm shadow-sm focus-visible:outline-none focus-visible:ring-1 focus-visible:ring-ring"
                      value={createForm.status}
                      onChange={(e) => setCreateForm((f) => ({ ...f, status: e.target.value }))}
                    >
                      <option value="todo">To Do</option>
                      <option value="in_progress">In Progress</option>
                      <option value="review">Review</option>
                      <option value="done">Done</option>
                    </select>
                  </div>
                </div>
                <div>
                  <label className="text-sm font-medium block mb-1">Due Date</label>
                  <Input type="date" value={createForm.due_date} onChange={(e) => setCreateForm((f) => ({ ...f, due_date: e.target.value }))} />
                </div>
                <div>
                  <label className="text-sm font-medium block mb-1">Description</label>
                  <Input value={createForm.description} onChange={(e) => setCreateForm((f) => ({ ...f, description: e.target.value }))} />
                </div>
                <div className="flex justify-end gap-2">
                  <Button type="button" variant="outline" onClick={() => setShowCreate(false)}>Cancel</Button>
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
