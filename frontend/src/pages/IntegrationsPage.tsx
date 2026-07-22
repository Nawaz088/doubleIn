import { useState, useEffect } from 'react'
import { Plug, RefreshCw, CheckCircle2, XCircle, Clock, ExternalLink, IndianRupee, Building2, Smartphone } from 'lucide-react'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { Button } from '@/components/ui/button'
import { Badge } from '@/components/ui/badge'
import { apiFetch } from '@/api/client'
import type { Integration, SyncLog } from '@/types'

const providerLabels: Record<string, { label: string; color: string }> = {
  qbo: { label: 'QuickBooks Online', color: 'text-emerald-400' },
  xero: { label: 'Xero', color: 'text-blue-400' },
  netsuite: { label: 'NetSuite', color: 'text-orange-400' },
  sage: { label: 'Sage', color: 'text-green-400' },
}

const syncStatusConfig: Record<string, { label: string; variant: 'success' | 'warning' | 'danger' | 'outline' }> = {
  running: { label: 'Running', variant: 'warning' },
  success: { label: 'Success', variant: 'success' },
  partial: { label: 'Partial', variant: 'warning' },
  error: { label: 'Error', variant: 'danger' },
}

export function IntegrationsPage() {
  const [integrations, setIntegrations] = useState<Integration[]>([])
  const [syncLogs, setSyncLogs] = useState<Record<string, SyncLog[]>>({})
  const [loading, setLoading] = useState(true)
  const [selectedProvider, setSelectedProvider] = useState<string | null>(null)

  const load = async () => {
    setLoading(true)
    try {
      const data = await apiFetch<Integration[]>('/integrations/')
      setIntegrations(data || [])
    } catch {
      setIntegrations([])
    } finally {
      setLoading(false)
    }
  }

  useEffect(() => { load() }, [])

  const handleConnect = async (provider: string) => {
    try {
      await apiFetch(`/integrations/${provider}/auth`, { method: 'POST' })
      load()
    } catch {}
  }

  const handleDisconnect = async (id: string) => {
    await apiFetch(`/integrations/${id}/disconnect`, { method: 'POST' })
    load()
  }

  const handleSync = async (id: string) => {
    await apiFetch(`/integrations/${id}/sync`, { method: 'POST' })
    load()
  }

  const showLogs = async (integrationId: string) => {
    try {
      const logs = await apiFetch<SyncLog[]>(`/integrations/${integrationId}/sync-logs`)
      setSyncLogs((prev) => ({ ...prev, [integrationId]: logs }))
      setSelectedProvider(integrationId)
    } catch {}
  }

  const activeIntegration = integrations.find((i) => i.is_active)

  if (loading) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-primary" />
      </div>
    )
  }

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-3xl font-bold tracking-tight">Integrations</h1>
        <p className="text-muted-foreground mt-1">Connect your accounting software and sync data.</p>
      </div>

      <div className="grid gap-4 md:grid-cols-2">
        {Object.entries(providerLabels).map(([provider, { label, color }]) => {
          const integration = integrations.find((i) => i.provider === provider)
          const isConnected = integration?.is_active

          return (
            <Card key={provider}>
              <CardContent className="p-6">
                <div className="flex items-start justify-between mb-4">
                  <div>
                    <h3 className={`font-semibold text-lg ${color}`}>{label}</h3>
                    <div className="flex items-center gap-2 mt-1">
                      {isConnected ? (
                        <>
                          <CheckCircle2 className="w-4 h-4 text-emerald-400" />
                          <span className="text-sm text-emerald-400">Connected</span>
                        </>
                      ) : (
                        <>
                          <XCircle className="w-4 h-4 text-muted-foreground" />
                          <span className="text-sm text-muted-foreground">Not Connected</span>
                        </>
                      )}
                    </div>
                  </div>
                  {integration && (
                    <div className="flex items-center gap-2">
                      <Badge variant={isConnected ? 'success' : 'outline'}>
                        {isConnected ? 'Active' : 'Inactive'}
                      </Badge>
                    </div>
                  )}
                </div>

                {integration?.last_sync_at && (
                  <div className="flex items-center gap-2 text-sm text-muted-foreground mb-4">
                    <Clock className="w-3.5 h-3.5" />
                    Last sync: {new Date(integration.last_sync_at).toLocaleString()}
                  </div>
                )}

                <div className="flex items-center gap-2">
                  {isConnected ? (
                    <>
                      <Button variant="outline" size="sm" onClick={() => handleSync(integration!.id)}>
                        <RefreshCw className="w-4 h-4 mr-1" /> Sync Now
                      </Button>
                      <Button variant="outline" size="sm" onClick={() => handleDisconnect(integration!.id)}>
                        Disconnect
                      </Button>
                    </>
                  ) : (
                    <Button size="sm" onClick={() => handleConnect(provider)}>
                      <Plug className="w-4 h-4 mr-1" /> Connect
                    </Button>
                  )}
                  {integration && (
                    <Button variant="ghost" size="sm" onClick={() => showLogs(integration.id)}>
                      <ExternalLink className="w-4 h-4" />
                    </Button>
                  )}
                </div>
              </CardContent>
            </Card>
          )
        })}
      </div>

      <div className="pt-6 border-t">
        <h2 className="text-xl font-semibold mb-4 flex items-center gap-2">
          <IndianRupee className="w-5 h-5" />
          Indian Integrations
        </h2>
        <div className="grid gap-4 md:grid-cols-2">
          <Card>
            <CardContent className="p-6">
              <div className="flex items-start justify-between mb-4">
                <div>
                  <h3 className="font-semibold text-lg text-green-600">Zoho Books</h3>
                  <p className="text-sm text-muted-foreground mt-1">Connect Zoho Books accounts</p>
                </div>
              </div>
              <Button size="sm" variant="outline">
                <Plug className="w-4 h-4 mr-1" /> Connect
              </Button>
            </CardContent>
          </Card>

          <Card>
            <CardContent className="p-6">
              <div className="flex items-start justify-between mb-4">
                <div>
                  <h3 className="font-semibold text-lg text-orange-600">Tally</h3>
                  <p className="text-sm text-muted-foreground mt-1">XML/TDL integration with Tally ERP</p>
                </div>
              </div>
              <Button size="sm" variant="outline">
                <Plug className="w-4 h-4 mr-1" /> Configure
              </Button>
            </CardContent>
          </Card>

          <Card>
            <CardContent className="p-6">
              <div className="flex items-start justify-between mb-4">
                <div>
                  <h3 className="font-semibold text-lg text-blue-600">Indian Banks</h3>
                  <p className="text-sm text-muted-foreground mt-1">Connect HDFC, ICICI, SBI accounts</p>
                </div>
              </div>
              <Button size="sm" variant="outline">
                <Building2 className="w-4 h-4 mr-1" /> Link Bank
              </Button>
            </CardContent>
          </Card>

          <Card>
            <CardContent className="p-6">
              <div className="flex items-start justify-between mb-4">
                <div>
                  <h3 className="font-semibold text-lg text-purple-600">UPI / Razorpay</h3>
                  <p className="text-sm text-muted-foreground mt-1">UPI payments and Razorpay gateway</p>
                </div>
              </div>
              <Button size="sm" variant="outline">
                <Smartphone className="w-4 h-4 mr-1" /> Connect
              </Button>
            </CardContent>
          </Card>
        </div>
      </div>

      {selectedProvider && syncLogs[selectedProvider] && (
        <Card>
          <CardHeader className="flex flex-row items-center justify-between">
            <CardTitle className="text-base">Sync Logs</CardTitle>
            <Button variant="ghost" size="sm" onClick={() => setSelectedProvider(null)}>Close</Button>
          </CardHeader>
          <CardContent>
            {syncLogs[selectedProvider].length === 0 ? (
              <p className="text-sm text-muted-foreground">No sync logs found.</p>
            ) : (
              <div className="overflow-x-auto">
                <table className="w-full">
                  <thead>
                    <tr className="border-b text-left">
                      <th className="p-3 text-sm font-medium text-muted-foreground">Entity</th>
                      <th className="p-3 text-sm font-medium text-muted-foreground">Status</th>
                      <th className="p-3 text-sm font-medium text-muted-foreground">Records</th>
                      <th className="p-3 text-sm font-medium text-muted-foreground">Started</th>
                      <th className="p-3 text-sm font-medium text-muted-foreground">Completed</th>
                    </tr>
                  </thead>
                  <tbody>
                    {syncLogs[selectedProvider].map((log) => (
                      <tr key={log.id} className="border-b last:border-0">
                        <td className="p-3 text-sm">{log.entity_type}</td>
                        <td className="p-3">
                          <Badge variant={syncStatusConfig[log.status]?.variant || 'outline'}>
                            {syncStatusConfig[log.status]?.label || log.status}
                          </Badge>
                        </td>
                        <td className="p-3 text-sm">{log.records_synced}</td>
                        <td className="p-3 text-sm">{new Date(log.started_at).toLocaleString()}</td>
                        <td className="p-3 text-sm">
                          {log.completed_at ? new Date(log.completed_at).toLocaleString() : '—'}
                        </td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            )}
          </CardContent>
        </Card>
      )}
    </div>
  )
}
