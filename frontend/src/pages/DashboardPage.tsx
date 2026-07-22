import { useState, useEffect } from 'react'
import { Link } from 'react-router-dom'
import { Plus, TrendingUp, CheckCircle2, Clock, AlertTriangle } from 'lucide-react'
import { Card, CardHeader, CardTitle, CardDescription, CardContent } from '@/components/ui/card'
import { Button } from '@/components/ui/button'
import { Badge } from '@/components/ui/badge'
import { scorecardApi } from '@/api/scorecards'
import type { Scorecard } from '@/types'
import { cn } from '@/lib/utils'

const statusConfig: Record<string, { label: string; className: string }> = {
  draft: { label: 'Draft', className: 'bg-muted text-muted-foreground' },
  in_review: { label: 'In Review', className: 'bg-blue-500/20 text-blue-400' },
  published: { label: 'Published', className: 'bg-emerald-500/20 text-emerald-400' },
  archived: { label: 'Archived', className: 'bg-muted text-muted-foreground' },
}

export function DashboardPage() {
  const [scorecards, setScorecards] = useState<Scorecard[]>([])

  useEffect(() => {
    scorecardApi.list().then(setScorecards).catch(() => {})
  }, [])

  const activeScorecard = scorecards.find((s) => s.status !== 'archived')

  return (
    <div className="space-y-8">
      <div>
        <h1 className="text-3xl font-bold tracking-tight">Dashboard</h1>
        <p className="text-muted-foreground mt-1">Welcome back. Here&apos;s your firm at a glance.</p>
      </div>

      <div className="grid grid-cols-4 gap-4">
        <Card>
          <CardHeader className="pb-2">
            <CardDescription>Active Clients</CardDescription>
            <CardTitle className="text-2xl">0</CardTitle>
          </CardHeader>
        </Card>
        <Card>
          <CardHeader className="pb-2">
            <CardDescription>Open Tasks</CardDescription>
            <CardTitle className="text-2xl">0</CardTitle>
          </CardHeader>
        </Card>
        <Card>
          <CardHeader className="pb-2">
            <CardDescription>Scorecards</CardDescription>
            <CardTitle className="text-2xl">{scorecards.length}</CardTitle>
          </CardHeader>
        </Card>
        <Card>
          <CardHeader className="pb-2">
            <CardDescription>Pending Reviews</CardDescription>
            <CardTitle className="text-2xl">0</CardTitle>
          </CardHeader>
        </Card>
      </div>

      <div>
        <div className="flex items-center justify-between mb-4">
          <h2 className="text-xl font-semibold">Recent Scorecards</h2>
          <Link to="/scorecards/new">
            <Button size="sm" className="gap-2">
              <Plus className="w-4 h-4" />
              New Scorecard
            </Button>
          </Link>
        </div>

        {scorecards.length === 0 ? (
          <Card className="p-12 text-center">
            <TrendingUp className="w-12 h-12 mx-auto text-muted-foreground mb-4" />
            <h3 className="text-lg font-medium mb-2">No scorecards yet</h3>
            <p className="text-muted-foreground mb-4">
              Create your first scorecard to start tracking KPIs for board meetings.
            </p>
            <Link to="/scorecards/new">
              <Button className="gap-2">
                <Plus className="w-4 h-4" />
                Create Scorecard
              </Button>
            </Link>
          </Card>
        ) : (
          <div className="grid gap-4">
            {scorecards.slice(0, 3).map((sc) => (
              <Link key={sc.id} to={`/scorecards/${sc.id}`}>
                <Card className="hover:border-primary/50 transition-colors cursor-pointer">
                  <CardContent className="flex items-center justify-between py-4">
                    <div>
                      <h3 className="font-medium">{sc.name}</h3>
                      <p className="text-sm text-muted-foreground">
                        {sc.period_start} ― {sc.period_end}
                      </p>
                    </div>
                    <Badge className={cn(statusConfig[sc.status]?.className)}>
                      {statusConfig[sc.status]?.label || sc.status}
                    </Badge>
                  </CardContent>
                </Card>
              </Link>
            ))}
          </div>
        )}
      </div>
    </div>
  )
}
