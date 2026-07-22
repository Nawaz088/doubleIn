import { useState, useEffect } from 'react'
import { useParams, Link, useNavigate } from 'react-router-dom'
import {
  ArrowLeft,
  RefreshCw,
  Send,
  Maximize2,
  UserPlus,
  CheckCircle2,
  AlertTriangle,
  Clock,
  TrendingUp,
  TrendingDown,
  Minus,
  MessageSquare,
  FileDown,
} from 'lucide-react'
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from '@/components/ui/card'
import { Button } from '@/components/ui/button'
import { StatusBadge } from '@/components/ui/status-badge'
import { Input } from '@/components/ui/input'
import { scorecardApi } from '@/api/scorecards'
import { cn } from '@/lib/utils'
import type { ScorecardDetail, KpiEntry } from '@/types'

const kpiStatusIcons: Record<string, React.ElementType> = {
  on_track: CheckCircle2,
  at_risk: AlertTriangle,
  behind: Clock,
  achieved: CheckCircle2,
}

const kpiStatusColors: Record<string, string> = {
  on_track: 'text-emerald-400 bg-emerald-500/10',
  at_risk: 'text-amber-400 bg-amber-500/10',
  behind: 'text-red-400 bg-red-500/10',
  achieved: 'text-emerald-400 bg-emerald-500/10',
}

const kpiCategoryColors: Record<string, string> = {
  productivity: 'border-l-blue-500',
  financial: 'border-l-green-500',
  client_health: 'border-l-purple-500',
  custom: 'border-l-gray-500',
}

export function ScorecardDetailPage() {
  const { id } = useParams<{ id: string }>()
  const navigate = useNavigate()
  const [scorecard, setScorecard] = useState<ScorecardDetail | null>(null)
  const [loading, setLoading] = useState(true)
  const [commentText, setCommentText] = useState('')
  const [actionItemTitle, setActionItemTitle] = useState('')
  const [isFullscreen, setIsFullscreen] = useState(false)

  const load = async () => {
    if (!id) return
    setLoading(true)
    try {
      const data = await scorecardApi.get(id)
      setScorecard(data)
    } catch {
      navigate('/scorecards')
    } finally {
      setLoading(false)
    }
  }

  useEffect(() => { load() }, [id])

  const handleRefresh = async () => {
    if (!id) return
    const data = await scorecardApi.refresh(id)
    setScorecard(data)
  }

  const handlePublish = async () => {
    if (!id) return
    const data = await scorecardApi.publish(id)
    setScorecard(data)
  }

  const handleUpdateEntry = async (entryId: string, updates: Record<string, unknown>) => {
    if (!id) return
    const entry = await scorecardApi.updateEntry(id, entryId, updates)
    if (scorecard) {
      setScorecard({
        ...scorecard,
        kpi_entries: scorecard.kpi_entries.map((e) =>
          e.id === entry.id ? { ...e, ...entry } : e,
        ),
      })
    }
  }

  const handleAddComment = async () => {
    if (!id || !commentText.trim()) return
    const { apiFetch } = await import('@/api/client')
    try {
      await apiFetch(`/scorecards/${id}/comments`, {
        method: 'POST',
        body: JSON.stringify({ content: commentText }),
      })
      setCommentText('')
      load()
    } catch {}
  }

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
        <div className="grid grid-cols-3 gap-6">
          <div className="col-span-2 grid gap-4 md:grid-cols-2">
            <div className="skeleton h-40 rounded-xl" />
            <div className="skeleton h-40 rounded-xl" />
          </div>
          <div className="skeleton h-64 rounded-xl" />
        </div>
      </div>
    )
  }

  if (!scorecard) return null

  const byCategory = scorecard.kpi_entries.reduce<Record<string, KpiEntry[]>>((acc, entry) => {
    (acc[entry.kpi_category] ||= []).push(entry)
    return acc
  }, {})

  if (isFullscreen) {
    return (
      <div className="fixed inset-0 z-50 bg-background overflow-y-auto">
        <div className="sticky top-0 z-10 bg-background border-b px-6 py-4 flex items-center justify-between">
          <h1 className="text-2xl font-bold">{scorecard.name}</h1>
          <Button variant="outline" size="sm" onClick={() => setIsFullscreen(false)}>Exit Fullscreen</Button>
        </div>
        <div className="p-6 grid gap-6 md:grid-cols-3 auto-rows-min">
          {scorecard.kpi_entries.map((entry) => (
            <div key={entry.id} className="p-6 rounded-xl border bg-card text-card-foreground shadow">
              <h3 className="text-2xl font-bold">{entry.actual_value ?? '—'}{entry.kpi_unit}</h3>
              <p className="text-muted-foreground mb-2">{entry.kpi_name}</p>
              {entry.target_value !== null && entry.target_value !== undefined && entry.actual_value !== null && entry.actual_value !== undefined && (
                <div className="w-full bg-muted rounded-full h-2">
                  <div
                    className="bg-primary h-2 rounded-full"
                    style={{ width: `${Math.min(100, (entry.actual_value / entry.target_value) * 100)}%` }}
                  />
                </div>
              )}
            </div>
          ))}
        </div>
      </div>
    )
  }

  return (
    <div className="space-y-6">
      <div className="flex items-center gap-4">
        <Link to="/scorecards" className="text-muted-foreground hover:text-foreground">
          <ArrowLeft className="w-5 h-5" />
        </Link>
        <div className="flex-1">
          <h1 className="text-3xl font-bold tracking-tight">{scorecard.name}</h1>
          <p className="text-muted-foreground">
            {scorecard.period_start} ― {scorecard.period_end}
          </p>
        </div>
        <StatusBadge status={scorecard.status} />
        <Button variant="outline" size="sm" onClick={() => setIsFullscreen(true)}>
          <Maximize2 className="w-4 h-4 mr-1" /> Meeting View
        </Button>
        <Button variant="outline" size="sm" onClick={handleRefresh}>
          <RefreshCw className="w-4 h-4 mr-1" /> Refresh
        </Button>
        <Button variant="outline" size="sm">
          <FileDown className="w-4 h-4 mr-1" /> Export
        </Button>
        {scorecard.status === 'draft' && (
          <Button size="sm" onClick={handlePublish} className="gap-1">
            <Send className="w-4 h-4" /> Publish
          </Button>
        )}
      </div>

      <div className="grid grid-cols-3 gap-6">
        <div className="col-span-2 space-y-6">
          {Object.entries(byCategory).map(([category, entries]) => (
            <div key={category}>
              <h2 className="text-sm font-medium text-muted-foreground uppercase tracking-wider mb-3">
                {category.replace('_', ' ')}
              </h2>
              <div className="grid gap-4 md:grid-cols-2">
                {entries.map((entry) => {
                  const StatusIcon = kpiStatusIcons[entry.status || ''] || Minus
                  const trend = entry.previous_value !== null && entry.previous_value !== undefined && entry.actual_value !== null && entry.actual_value !== undefined
                    ? entry.actual_value > entry.previous_value ? 'up' : entry.actual_value < entry.previous_value ? 'down' : 'flat'
                    : null

                  return (
                    <Card
                      key={entry.id}
                      className={cn('border-l-4 transition-colors', kpiCategoryColors[entry.kpi_category] || '')}
                    >
                      <CardContent className="p-4">
                        <div className="flex items-start justify-between mb-2">
                          <h3 className="text-sm font-medium text-muted-foreground">{entry.kpi_name}</h3>
                          {entry.status && (
                            <div className={cn('flex items-center gap-1 px-2 py-0.5 rounded text-xs', kpiStatusColors[entry.status])}>
                              <StatusIcon className="w-3 h-3" />
                              {entry.status.replace('_', ' ')}
                            </div>
                          )}
                        </div>

                        <div className="flex items-baseline gap-2 mb-1">
                          <span className="text-3xl font-bold">
                            {entry.actual_value ?? '—'}
                          </span>
                          {entry.kpi_unit && (
                            <span className="text-sm text-muted-foreground">{entry.kpi_unit}</span>
                          )}
                          {trend && (
                            <span className={cn(
                              'text-xs flex items-center gap-0.5',
                              trend === 'up' ? 'text-emerald-400' : trend === 'down' ? 'text-red-400' : 'text-muted-foreground',
                            )}>
                              {trend === 'up' ? <TrendingUp className="w-3 h-3" /> : trend === 'down' ? <TrendingDown className="w-3 h-3" /> : <Minus className="w-3 h-3" />}
                            </span>
                          )}
                        </div>

                        {entry.target_value !== null && entry.target_value !== undefined && (
                          <div className="w-full bg-muted rounded-full h-1.5 mb-2">
                            <div
                              className={cn(
                                'h-1.5 rounded-full transition-all',
                                (entry.actual_value || 0) >= (entry.target_value || 0) ? 'bg-emerald-500' : (entry.actual_value || 0) >= (entry.target_value || 0) * 0.7 ? 'bg-amber-500' : 'bg-red-500',
                              )}
                              style={{ width: `${Math.min(100, Math.max(0, ((entry.actual_value || 0) / (entry.target_value || 1)) * 100))}%` }}
                            />
                          </div>
                        )}

                        <div className="flex items-center justify-between text-xs text-muted-foreground">
                          <span>Target: {entry.target_value ?? '—'}{entry.kpi_unit}</span>
                          {entry.previous_value !== null && entry.previous_value !== undefined && (
                            <span>Prev: {entry.previous_value}{entry.kpi_unit}</span>
                          )}
                        </div>

                        {scorecard.status !== 'published' && (
                          <div className="mt-3 flex gap-2">
                            <Input
                              type="text"
                              placeholder="Add note..."
                              className="h-8 text-xs"
                              value={entry.notes || ''}
                              onChange={(e) => handleUpdateEntry(entry.id, { notes: e.target.value })}
                              onBlur={(e) => {
                                if (e.target.value !== (entry.notes || '')) {
                                  handleUpdateEntry(entry.id, { notes: e.target.value })
                                }
                              }}
                            />
                          </div>
                        )}
                      </CardContent>
                    </Card>
                  )
                })}
              </div>
            </div>
          ))}
        </div>

        <div className="space-y-4">
          <Card>
            <CardHeader>
              <CardTitle className="text-base">Comments</CardTitle>
            </CardHeader>
            <CardContent className="space-y-3">
              {scorecard.comments.map((c) => (
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
              ))}
              {scorecard.comments.length === 0 && (
                <p className="text-sm text-muted-foreground">No comments yet</p>
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

          <Card>
            <CardHeader>
              <CardTitle className="text-base">Action Items</CardTitle>
            </CardHeader>
            <CardContent className="space-y-3">
              {scorecard.action_items.map((ai) => (
                <div key={ai.id} className="flex items-start gap-3 text-sm">
                  <input type="checkbox" className="mt-0.5" checked={ai.status === 'completed'} readOnly />
                  <div className="flex-1">
                    <p className={ai.status === 'completed' ? 'line-through text-muted-foreground' : ''}>
                      {ai.title}
                    </p>
                    {ai.description && (
                      <p className="text-xs text-muted-foreground mt-0.5">{ai.description}</p>
                    )}
                  </div>
                  <StatusBadge status={ai.status} />
                </div>
              ))}
              {scorecard.action_items.length === 0 && (
                <p className="text-sm text-muted-foreground">No action items</p>
              )}
            </CardContent>
          </Card>
        </div>
      </div>
    </div>
  )
}
