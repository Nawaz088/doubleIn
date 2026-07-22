import { useState, useEffect } from 'react'
import { useParams, Link } from 'react-router-dom'
import {
  ArrowLeft, CheckCircle2, Circle, Clock, AlertCircle, ChevronDown, ChevronRight,
} from 'lucide-react'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { StatusBadge } from '@/components/ui/status-badge'
import { Button } from '@/components/ui/button'
import { apiFetch } from '@/api/client'
import { cn } from '@/lib/utils'
import type { Task, TaskList } from '@/types'

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

const priorityColors: Record<string, string> = {
  low: 'border-l-muted-foreground',
  medium: 'border-l-blue-500',
  high: 'border-l-amber-500',
  critical: 'border-l-red-500',
}

export function ClosePage() {
  const { id } = useParams<{ id: string }>()
  const [taskLists, setTaskLists] = useState<TaskList[]>([])
  const [tasksByList, setTasksByList] = useState<Record<string, Task[]>>({})
  const [client, setClient] = useState<{ name: string } | null>(null)
  const [loading, setLoading] = useState(true)
  const [expandedLists, setExpandedLists] = useState<Record<string, boolean>>({})

  const load = async () => {
    if (!id) return
    setLoading(true)
    try {
      const [c, tl] = await Promise.all([
        apiFetch<{ name: string }>(`/clients/${id}`),
        apiFetch<TaskList[]>(`/task-lists/?client_id=${id}`),
      ])
      setClient(c)
      setTaskLists(tl.sort((a, b) => a.sort_order - b.sort_order))

      const initialExpanded: Record<string, boolean> = {}
      const tMap: Record<string, Task[]> = {}

      await Promise.all(tl.map(async (list) => {
        initialExpanded[list.id] = true
        try {
          tMap[list.id] = await apiFetch<Task[]>(`/tasks/?task_list_id=${list.id}`)
        } catch {
          tMap[list.id] = []
        }
      }))

      setExpandedLists(initialExpanded)
      setTasksByList(tMap)
    } catch {} finally {
      setLoading(false)
    }
  }

  useEffect(() => { load() }, [id])

  const toggleList = (listId: string) => {
    setExpandedLists((prev) => ({ ...prev, [listId]: !prev[listId] }))
  }

  const allTasks = Object.values(tasksByList).flat()
  const completedCount = allTasks.filter((t) => t.status === 'done').length
  const progress = allTasks.length > 0 ? Math.round((completedCount / allTasks.length) * 100) : 0

  if (loading) {
    return (
      <div className="space-y-4">
        <div className="flex items-center gap-4">
          <div className="skeleton h-5 w-5 rounded" />
          <div>
            <div className="skeleton h-8 w-64 rounded-lg" />
            <div className="skeleton h-4 w-48 rounded-lg mt-2" />
          </div>
        </div>
        <div className="skeleton h-24 w-full rounded-xl" />
        <div className="skeleton h-48 w-full rounded-xl" />
      </div>
    )
  }

  return (
    <div className="space-y-6">
      <div className="flex items-center gap-4">
        <Link to={`/clients/${id}`} className="text-muted-foreground hover:text-foreground">
          <ArrowLeft className="w-5 h-5" />
        </Link>
        <div className="flex-1">
          <h1 className="text-3xl font-bold tracking-tight">
            {client?.name || 'Client'} — Close
          </h1>
          <p className="text-muted-foreground mt-1">Month-end close progress</p>
        </div>
      </div>

      <Card>
        <CardContent className="py-4">
          <div className="flex items-center justify-between mb-2">
            <span className="text-sm font-medium">Overall Progress</span>
            <span className="text-sm text-muted-foreground">{completedCount}/{allTasks.length} tasks</span>
          </div>
          <div className="w-full bg-muted rounded-full h-3">
            <div
              className="bg-primary h-3 rounded-full transition-all"
              style={{ width: `${progress}%` }}
            />
          </div>
        </CardContent>
      </Card>

      {taskLists.length === 0 ? (
        <Card className="p-12 text-center">
          <Circle className="w-12 h-12 mx-auto text-muted-foreground mb-4" />
          <h3 className="text-lg font-medium mb-2">No task lists</h3>
          <p className="text-muted-foreground">
            Create task lists for this client to populate the close page.
          </p>
        </Card>
      ) : (
        <div className="space-y-3">
          {taskLists.map((list) => {
            const tasks = tasksByList[list.id] || []
            const listCompleted = tasks.filter((t) => t.status === 'done').length
            const isExpanded = expandedLists[list.id]

            return (
              <Card key={list.id}>
                <button
                  className="w-full"
                  onClick={() => toggleList(list.id)}
                >
                  <CardHeader className="flex flex-row items-center justify-between py-3 cursor-pointer hover:bg-muted/50 transition-colors rounded-t-xl">
                    <div className="flex items-center gap-2">
                      {isExpanded ? (
                        <ChevronDown className="w-4 h-4 text-muted-foreground" />
                      ) : (
                        <ChevronRight className="w-4 h-4 text-muted-foreground" />
                      )}
                      <CardTitle className="text-base">{list.name}</CardTitle>
                      <span className="text-xs text-muted-foreground">
                        {listCompleted}/{tasks.length}
                      </span>
                    </div>
                  </CardHeader>
                </button>
                {isExpanded && (
                  <CardContent className="pb-3 pt-0">
                    {tasks.length === 0 ? (
                      <p className="text-sm text-muted-foreground py-2">No tasks in this section.</p>
                    ) : (
                      <div className="space-y-1">
                        {tasks.map((task) => {
                          const Icon = statusIcons[task.status] || Circle
                          return (
                            <Link
                              key={task.id}
                              to={`/tasks/${task.id}`}
                              className={cn(
                                'flex items-center gap-3 p-2 rounded-lg border-l-2 hover:bg-muted/50 transition-colors',
                                priorityColors[task.priority],
                              )}
                            >
                              <Icon className={cn('w-4 h-4 shrink-0', statusIconColors[task.status])} />
                              <span className={cn(
                                'flex-1 text-sm',
                                task.status === 'done' && 'line-through text-muted-foreground',
                              )}>
                                {task.name}
                              </span>
                              {task.due_date && (
                                <span className="text-xs text-muted-foreground">
                                  {new Date(task.due_date).toLocaleDateString()}
                                </span>
                              )}
                              <StatusBadge status={task.status} />
                            </Link>
                          )
                        })}
                      </div>
                    )}
                  </CardContent>
                )}
              </Card>
            )
          })}
        </div>
      )}
    </div>
  )
}
