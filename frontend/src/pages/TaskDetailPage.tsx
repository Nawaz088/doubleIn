import { useState, useEffect } from 'react'
import { useParams, Link } from 'react-router-dom'
import {
  ArrowLeft, Send, Paperclip, MessageSquare, User, Calendar, Tag,
  ChevronDown, CheckCircle2, Circle, Clock, AlertCircle,
} from 'lucide-react'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import { StatusBadge } from '@/components/ui/status-badge'
import { apiFetch } from '@/api/client'
import { cn } from '@/lib/utils'
import type { TaskDetail, TaskComment } from '@/types'

const priorityColors: Record<string, string> = {
  low: 'text-muted-foreground',
  medium: 'text-blue-400',
  high: 'text-amber-400',
  critical: 'text-red-400',
}

export function TaskDetailPage() {
  const { id } = useParams<{ id: string }>()
  const [task, setTask] = useState<TaskDetail | null>(null)
  const [loading, setLoading] = useState(true)
  const [commentText, setCommentText] = useState('')

  const load = async () => {
    if (!id) return
    setLoading(true)
    try {
      const data = await apiFetch<TaskDetail>(`/tasks/${id}`)
      setTask(data)
    } catch {} finally {
      setLoading(false)
    }
  }

  useEffect(() => { load() }, [id])

  const handleStatusChange = async (status: string) => {
    if (!id) return
    await apiFetch(`/tasks/${id}`, { method: 'PUT', body: JSON.stringify({ status }) })
    load()
  }

  const handlePriorityChange = async (priority: string) => {
    if (!id) return
    await apiFetch(`/tasks/${id}`, { method: 'PUT', body: JSON.stringify({ priority }) })
    load()
  }

  const handleAddComment = async () => {
    if (!id || !commentText.trim()) return
    await apiFetch(`/tasks/${id}/comments`, {
      method: 'POST',
      body: JSON.stringify({ content: commentText }),
    })
    setCommentText('')
    load()
  }

  if (loading) {
    return (
      <div className="space-y-4">
        <div className="flex items-center gap-4">
          <div className="skeleton h-5 w-5 rounded" />
          <div className="skeleton h-8 w-64 rounded-lg flex-1" />
          <div className="skeleton h-6 w-24 rounded-full" />
        </div>
        <div className="grid grid-cols-3 gap-6">
          <div className="col-span-2 space-y-4">
            <div className="skeleton h-32 rounded-xl" />
            <div className="skeleton h-48 rounded-xl" />
          </div>
          <div className="skeleton h-64 rounded-xl" />
        </div>
      </div>
    )
  }

  if (!task) return null

  return (
    <div className="space-y-6">
      <div className="flex items-center gap-4">
        <Link to="/tasks" className="text-muted-foreground hover:text-foreground">
          <ArrowLeft className="w-5 h-5" />
        </Link>
        <div className="flex-1">
          <h1 className="text-3xl font-bold tracking-tight">{task.name}</h1>
        </div>
        <StatusBadge status={task.status} />
      </div>

      <div className="grid grid-cols-3 gap-6">
        <div className="col-span-2 space-y-6">
          {task.description && (
            <Card>
              <CardHeader><CardTitle className="text-base">Description</CardTitle></CardHeader>
              <CardContent>
                <p className="text-sm text-muted-foreground whitespace-pre-wrap">{task.description}</p>
              </CardContent>
            </Card>
          )}

          {task.sub_tasks && task.sub_tasks.length > 0 && (
            <Card>
              <CardHeader><CardTitle className="text-base">Sub-tasks</CardTitle></CardHeader>
              <CardContent className="space-y-2">
                {task.sub_tasks.map((st) => (
                  <div key={st.id} className="flex items-center gap-3 text-sm">
                    {st.status === 'done' ? (
                      <CheckCircle2 className="w-4 h-4 text-emerald-400" />
                    ) : (
                      <Circle className="w-4 h-4 text-muted-foreground" />
                    )}
                    <span className={st.status === 'done' ? 'line-through text-muted-foreground' : ''}>
                      {st.name}
                    </span>
                  </div>
                ))}
              </CardContent>
            </Card>
          )}

          <Card>
            <CardHeader><CardTitle className="text-base">Comments</CardTitle></CardHeader>
            <CardContent className="space-y-4">
              {task.comments.length === 0 ? (
                <p className="text-sm text-muted-foreground">No comments yet.</p>
              ) : (
                task.comments.map((c: TaskComment) => (
                  <div key={c.id} className="flex gap-3 text-sm">
                    <div className="w-7 h-7 rounded-full bg-primary/20 flex items-center justify-center text-xs font-bold shrink-0">
                      U
                    </div>
                    <div>
                      <p>{c.content}</p>
                      <p className="text-xs text-muted-foreground mt-0.5">
                        {new Date(c.created_at).toLocaleString()}
                      </p>
                    </div>
                  </div>
                ))
              )}
              <div className="flex gap-2 pt-2">
                <Input
                  placeholder="Add a comment..."
                  value={commentText}
                  onChange={(e) => setCommentText(e.target.value)}
                  className="text-sm"
                  onKeyDown={(e) => e.key === 'Enter' && handleAddComment()}
                />
                <Button size="icon" variant="ghost" onClick={handleAddComment}>
                  <Send className="w-4 h-4" />
                </Button>
              </div>
            </CardContent>
          </Card>

          {task.attachments.length > 0 && (
            <Card>
              <CardHeader><CardTitle className="text-base">Attachments</CardTitle></CardHeader>
              <CardContent className="space-y-2">
                {task.attachments.map((a) => (
                  <div key={a.id} className="flex items-center gap-2 text-sm">
                    <Paperclip className="w-4 h-4 text-muted-foreground" />
                    <span>{a.file_name}</span>
                    <span className="text-xs text-muted-foreground">{a.file_type}</span>
                  </div>
                ))}
              </CardContent>
            </Card>
          )}
        </div>

        <div className="space-y-4">
          <Card>
            <CardHeader><CardTitle className="text-base">Details</CardTitle></CardHeader>
            <CardContent className="space-y-4">
              <div>
                <p className="text-xs text-muted-foreground mb-1 flex items-center gap-1">
                  <Calendar className="w-3 h-3" /> Status
                </p>
                <select
                  className="flex h-9 w-full rounded-md border border-input bg-background px-3 py-1 text-sm shadow-sm focus-visible:outline-none focus-visible:ring-1 focus-visible:ring-ring"
                  value={task.status}
                  onChange={(e) => handleStatusChange(e.target.value)}
                >
                  <option value="todo">To Do</option>
                  <option value="in_progress">In Progress</option>
                  <option value="review">Review</option>
                  <option value="done">Done</option>
                </select>
              </div>

              <div>
                <p className="text-xs text-muted-foreground mb-1 flex items-center gap-1">
                  <AlertCircle className="w-3 h-3" /> Priority
                </p>
                <select
                  className="flex h-9 w-full rounded-md border border-input bg-background px-3 py-1 text-sm shadow-sm focus-visible:outline-none focus-visible:ring-1 focus-visible:ring-ring"
                  value={task.priority}
                  onChange={(e) => handlePriorityChange(e.target.value)}
                >
                  <option value="low">Low</option>
                  <option value="medium">Medium</option>
                  <option value="high">High</option>
                  <option value="critical">Critical</option>
                </select>
              </div>

              <div>
                <p className="text-xs text-muted-foreground mb-1 flex items-center gap-1">
                  <User className="w-3 h-3" /> Assignee
                </p>
                <p className="text-sm">
                  {task.assignee ? task.assignee.name : 'Unassigned'}
                </p>
              </div>

              <div>
                <p className="text-xs text-muted-foreground mb-1 flex items-center gap-1">
                  <Calendar className="w-3 h-3" /> Due Date
                </p>
                <p className="text-sm">
                  {task.due_date ? new Date(task.due_date).toLocaleDateString() : 'No due date'}
                </p>
              </div>

              {task.tags.length > 0 && (
                <div>
                  <p className="text-xs text-muted-foreground mb-1 flex items-center gap-1">
                    <Tag className="w-3 h-3" /> Tags
                  </p>
                  <div className="flex gap-1 flex-wrap">
                    {task.tags.map((tag) => (
                      <StatusBadge key={tag} status="todo" label={tag} />
                    ))}
                  </div>
                </div>
              )}
            </CardContent>
          </Card>
        </div>
      </div>
    </div>
  )
}
