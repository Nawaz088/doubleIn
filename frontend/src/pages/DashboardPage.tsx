import * as React from 'react'
import { Link } from 'react-router-dom'
import { Users, ListTodo, Banknote, FileText, TrendingUp, ArrowRight, Clock, CheckCircle2, AlertCircle } from 'lucide-react'
import { apiFetch } from '@/api/client'
import { StatCard } from '@/components/ui/stat-card'
import { StatusBadge } from '@/components/ui/status-badge'
import { Button } from '@/components/ui/button'

interface DashboardStats {
  total_clients: number
  active_clients: number
  total_tasks: number
  completed_tasks: number
  pending_reviews: number
  bank_transactions: number
  upcoming_deadlines: { id: string; title: string; due_date: string; client_name: string }[]
  recent_activity: { id: string; action: string; client_name: string; time: string }[]
}

export function DashboardPage() {
  const [stats, setStats] = React.useState<DashboardStats | null>(null)
  const [loading, setLoading] = React.useState(true)

  React.useEffect(() => {
    apiFetch<{ data: DashboardStats }>('/clients/dashboard-summary')
      .then((r) => setStats(r?.data || r))
      .catch(() => {})
      .finally(() => setLoading(false))
  }, [])

  return (
    <div className="space-y-8">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold tracking-tight">Dashboard</h1>
          <p className="text-sm text-muted-foreground mt-1">Overview of your practice</p>
        </div>
        <div className="flex items-center gap-2">
          <Button variant="outline" size="sm">
            <Clock className="w-4 h-4 mr-1.5" />
            This Month
          </Button>
        </div>
      </div>

      <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-4">
        {loading ? (
          Array.from({ length: 4 }).map((_, i) => (
            <div key={i} className="rounded-xl border bg-card p-5">
              <div className="skeleton h-3 w-20 mb-3" />
              <div className="skeleton h-8 w-16 mb-2" />
              <div className="skeleton h-3 w-24" />
            </div>
          ))
        ) : (
          <>
            <StatCard
              title="Total Clients"
              value={stats?.total_clients ?? 0}
              subtitle={`${stats?.active_clients ?? 0} active`}
              icon={<Users className="w-5 h-5" />}
              trend="up"
              trendValue="+12% this month"
            />
            <StatCard
              title="Open Tasks"
              value={(stats?.total_tasks ?? 0) - (stats?.completed_tasks ?? 0)}
              subtitle={`${stats?.completed_tasks ?? 0} completed`}
              icon={<ListTodo className="w-5 h-5" />}
              trend={stats && stats.completed_tasks > stats.total_tasks * 0.5 ? 'up' : 'down'}
              trendValue={`${stats ? Math.round(stats.completed_tasks / Math.max(stats.total_tasks, 1) * 100) : 0}% done`}
            />
            <StatCard
              title="Pending Reviews"
              value={stats?.pending_reviews ?? 0}
              subtitle="Awaiting approval"
              icon={<FileText className="w-5 h-5" />}
              trend="neutral"
              trendValue={stats?.pending_reviews ? 'Needs attention' : 'All clear'}
            />
            <StatCard
              title="Bank Transactions"
              value={stats?.bank_transactions ?? 0}
              subtitle="This month"
              icon={<Banknote className="w-5 h-5" />}
              trend="up"
              trendValue="+8% vs last month"
            />
          </>
        )}
      </div>

      <div className="grid gap-6 lg:grid-cols-2">
        <div className="rounded-xl border bg-card">
          <div className="flex items-center justify-between px-5 py-4 border-b">
            <h2 className="text-sm font-semibold">Upcoming Deadlines</h2>
            <Button variant="ghost" size="sm" asChild>
              <Link to="/tasks" className="gap-1">
                View all <ArrowRight className="w-3 h-3" />
              </Link>
            </Button>
          </div>
          <div className="divide-y divide-border">
            {loading ? (
              Array.from({ length: 4 }).map((_, i) => (
                <div key={i} className="flex items-center gap-3 p-4">
                  <div className="skeleton h-8 w-8 rounded-full" />
                  <div className="flex-1 space-y-1">
                    <div className="skeleton h-4 w-40" />
                    <div className="skeleton h-3 w-24" />
                  </div>
                </div>
              ))
            ) : !stats?.upcoming_deadlines?.length ? (
              <div className="flex flex-col items-center py-12 text-center">
                <CheckCircle2 className="w-8 h-8 text-emerald-500 mb-3" />
                <p className="text-sm text-muted-foreground">No upcoming deadlines</p>
              </div>
            ) : (
              stats.upcoming_deadlines.map((d) => (
                <div key={d.id} className="flex items-center gap-3 p-4 hover:bg-accent/50 transition-colors">
                  <div className="flex items-center justify-center w-8 h-8 rounded-full bg-yellow-500/10 text-yellow-500 shrink-0">
                    <AlertCircle className="w-4 h-4" />
                  </div>
                  <div className="flex-1 min-w-0">
                    <p className="text-sm font-medium truncate">{d.title}</p>
                    <p className="text-xs text-muted-foreground">{d.client_name}</p>
                  </div>
                  <div className="text-xs text-muted-foreground shrink-0">{d.due_date}</div>
                </div>
              ))
            )}
          </div>
        </div>

        <div className="rounded-xl border bg-card">
          <div className="flex items-center justify-between px-5 py-4 border-b">
            <h2 className="text-sm font-semibold">Recent Activity</h2>
            <Button variant="ghost" size="sm">
              <TrendingUp className="w-3 h-3 mr-1" /> Activity
            </Button>
          </div>
          <div className="divide-y divide-border">
            {loading ? (
              Array.from({ length: 4 }).map((_, i) => (
                <div key={i} className="flex items-center gap-3 p-4">
                  <div className="skeleton h-8 w-8 rounded-full" />
                  <div className="flex-1 space-y-1">
                    <div className="skeleton h-4 w-40" />
                    <div className="skeleton h-3 w-24" />
                  </div>
                </div>
              ))
            ) : !stats?.recent_activity?.length ? (
              <div className="flex flex-col items-center py-12 text-center">
                <Clock className="w-8 h-8 text-muted-foreground mb-3" />
                <p className="text-sm text-muted-foreground">No recent activity</p>
              </div>
            ) : (
              stats.recent_activity.map((a) => (
                <div key={a.id} className="flex items-center gap-3 p-4 hover:bg-accent/50 transition-colors">
                  <div className="flex items-center justify-center w-8 h-8 rounded-full bg-primary/10 text-primary shrink-0">
                    <CheckCircle2 className="w-4 h-4" />
                  </div>
                  <div className="flex-1 min-w-0">
                    <p className="text-sm truncate">{a.action}</p>
                    <p className="text-xs text-muted-foreground">{a.client_name}</p>
                  </div>
                  <div className="text-xs text-muted-foreground shrink-0">{a.time}</div>
                </div>
              ))
            )}
          </div>
        </div>
      </div>
    </div>
  )
}
