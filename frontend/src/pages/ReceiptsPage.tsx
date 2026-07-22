import { useState, useEffect } from 'react'
import { Upload, FileImage, Search, ExternalLink } from 'lucide-react'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import { Badge } from '@/components/ui/badge'
import { apiFetch } from '@/api/client'
import type { Receipt, Client } from '@/types'

const statusConfig: Record<string, { label: string; variant: 'success' | 'warning' | 'outline' }> = {
  processing: { label: 'Processing', variant: 'warning' },
  ready: { label: 'Ready', variant: 'outline' },
  matched: { label: 'Matched', variant: 'success' },
  posted: { label: 'Posted', variant: 'success' },
}

const methodLabels: Record<string, string> = {
  portal: 'Portal',
  email: 'Email',
  text: 'Text',
  mobile: 'Mobile',
  api: 'API',
}

export function ReceiptsPage() {
  const [receipts, setReceipts] = useState<Receipt[]>([])
  const [clients, setClients] = useState<Client[]>([])
  const [loading, setLoading] = useState(true)
  const [search, setSearch] = useState('')
  const [showUpload, setShowUpload] = useState(false)
  const [selectedReceipt, setSelectedReceipt] = useState<Receipt | null>(null)
  const [form, setForm] = useState({ client_id: '', file_url: '', file_name: '' })

  const load = async () => {
    setLoading(true)
    try {
      const [r, c] = await Promise.all([
        apiFetch<Receipt[]>('/receipts/'),
        apiFetch<Client[]>('/clients/'),
      ])
      setReceipts(r)
      setClients(c)
    } catch {} finally {
      setLoading(false)
    }
  }

  useEffect(() => { load() }, [])

  const handleUpload = async (e: React.FormEvent) => {
    e.preventDefault()
    await apiFetch('/receipts/upload', {
      method: 'POST',
      body: JSON.stringify(form),
    })
    setShowUpload(false)
    setForm({ client_id: '', file_url: '', file_name: '' })
    load()
  }

  const handlePost = async (id: string) => {
    await apiFetch(`/receipts/${id}/post`, { method: 'POST' })
    load()
  }

  const filtered = receipts.filter((r) =>
    r.file_name.toLowerCase().includes(search.toLowerCase()) ||
    (r.ocr_text && r.ocr_text.toLowerCase().includes(search.toLowerCase()))
  )

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
          <h1 className="text-3xl font-bold tracking-tight">Receipts</h1>
          <p className="text-muted-foreground mt-1">Upload, OCR, and post receipts to the ledger.</p>
        </div>
        <Button size="sm" className="gap-2" onClick={() => setShowUpload(true)}>
          <Upload className="w-4 h-4" />
          Upload Receipt
        </Button>
      </div>

      <div className="relative max-w-sm">
        <Search className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-muted-foreground" />
        <Input placeholder="Search receipts..." value={search} onChange={(e) => setSearch(e.target.value)} className="pl-9" />
      </div>

      {filtered.length === 0 ? (
        <Card className="p-12 text-center">
          <FileImage className="w-12 h-12 mx-auto text-muted-foreground mb-4" />
          <h3 className="text-lg font-medium mb-2">No receipts yet</h3>
          <p className="text-muted-foreground mb-4">Upload receipts to extract data via OCR.</p>
          <Button className="gap-2" onClick={() => setShowUpload(true)}>
            <Upload className="w-4 h-4" />
            Upload Receipt
          </Button>
        </Card>
      ) : (
        <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-3">
          {filtered.map((r) => (
            <Card
              key={r.id}
              className="hover:border-primary/50 transition-colors cursor-pointer"
              onClick={() => setSelectedReceipt(r)}
            >
              <CardContent className="p-6 space-y-3">
                <div className="flex items-start justify-between">
                  <FileImage className="w-8 h-8 text-muted-foreground" />
                  <Badge variant={statusConfig[r.status]?.variant || 'outline'}>
                    {statusConfig[r.status]?.label || r.status}
                  </Badge>
                </div>
                <div>
                  <h3 className="font-medium text-sm truncate">{r.file_name}</h3>
                  <p className="text-xs text-muted-foreground mt-1">
                    {methodLabels[r.upload_method] || r.upload_method}
                  </p>
                </div>
                {r.ocr_text && (
                  <p className="text-xs text-muted-foreground line-clamp-2">{r.ocr_text}</p>
                )}
              </CardContent>
            </Card>
          ))}
        </div>
      )}

      {showUpload && (
        <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/50">
          <Card className="w-full max-w-lg mx-4">
            <CardHeader><CardTitle>Upload Receipt</CardTitle></CardHeader>
            <CardContent>
              <form onSubmit={handleUpload} className="space-y-4">
                <div>
                  <label className="text-sm font-medium block mb-1">Client</label>
                  <select
                    className="flex h-9 w-full rounded-md border border-input bg-background px-3 py-1 text-sm shadow-sm focus-visible:outline-none focus-visible:ring-1 focus-visible:ring-ring"
                    value={form.client_id}
                    onChange={(e) => setForm((f) => ({ ...f, client_id: e.target.value }))}
                    required
                  >
                    <option value="">Select client</option>
                    {clients.map((c) => (
                      <option key={c.id} value={c.id}>{c.name}</option>
                    ))}
                  </select>
                </div>
                <div>
                  <label className="text-sm font-medium block mb-1">File Name</label>
                  <Input value={form.file_name} onChange={(e) => setForm((f) => ({ ...f, file_name: e.target.value }))} required />
                </div>
                <div>
                  <label className="text-sm font-medium block mb-1">File URL</label>
                  <Input value={form.file_url} onChange={(e) => setForm((f) => ({ ...f, file_url: e.target.value }))} required placeholder="https://..." />
                </div>
                <div className="flex justify-end gap-2">
                  <Button type="button" variant="outline" onClick={() => setShowUpload(false)}>Cancel</Button>
                  <Button type="submit">Upload</Button>
                </div>
              </form>
            </CardContent>
          </Card>
        </div>
      )}

      {selectedReceipt && (
        <div className="fixed inset-0 z-50 flex">
          <div className="absolute inset-0 bg-black/50" onClick={() => setSelectedReceipt(null)} />
          <div className="relative ml-auto w-full max-w-lg bg-card border-l h-full overflow-y-auto p-6 space-y-6">
            <div className="flex items-center justify-between">
              <h2 className="text-xl font-bold">{selectedReceipt.file_name}</h2>
              <Button variant="ghost" size="icon" onClick={() => setSelectedReceipt(null)}>
                <ExternalLink className="w-5 h-5" />
              </Button>
            </div>
            <div>
              <p className="text-xs text-muted-foreground mb-1">Status</p>
              <Badge variant={statusConfig[selectedReceipt.status]?.variant || 'outline'}>
                {statusConfig[selectedReceipt.status]?.label || selectedReceipt.status}
              </Badge>
            </div>
            <div>
              <p className="text-xs text-muted-foreground mb-1">Upload Method</p>
              <p className="text-sm">{methodLabels[selectedReceipt.upload_method] || selectedReceipt.upload_method}</p>
            </div>
            {selectedReceipt.ocr_text && (
              <div>
                <p className="text-xs text-muted-foreground mb-1">OCR Text</p>
                <Card className="p-3 bg-muted/50">
                  <p className="text-sm whitespace-pre-wrap">{selectedReceipt.ocr_text}</p>
                </Card>
              </div>
            )}
            {selectedReceipt.extracted_data && (
              <div>
                <p className="text-xs text-muted-foreground mb-1">Extracted Data</p>
                <Card className="p-3 bg-muted/50">
                  <pre className="text-xs whitespace-pre-wrap">
                    {JSON.stringify(selectedReceipt.extracted_data, null, 2)}
                  </pre>
                </Card>
              </div>
            )}
            {selectedReceipt.status === 'ready' && (
              <Button size="sm" onClick={() => handlePost(selectedReceipt.id)}>Post to Ledger</Button>
            )}
          </div>
        </div>
      )}
    </div>
  )
}
