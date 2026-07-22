import { useState, useEffect } from 'react'
import { Send, MessageSquare, FileText, Palette, Upload } from 'lucide-react'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import { Badge } from '@/components/ui/badge'
import { apiFetch } from '@/api/client'
import type { PortalMessage, PortalDocument, PortalBranding, Client } from '@/types'

export function PortalPage() {
  const [activeTab, setActiveTab] = useState<'messages' | 'documents' | 'branding'>('messages')
  const [messages, setMessages] = useState<PortalMessage[]>([])
  const [documents, setDocuments] = useState<PortalDocument[]>([])
  const [clients, setClients] = useState<Client[]>([])
  const [branding, setBranding] = useState<PortalBranding>({})
  const [loading, setLoading] = useState(true)
  const [messageForm, setMessageForm] = useState({ client_id: '', content: '' })
  const [docForm, setDocForm] = useState({ client_id: '', file_url: '', file_name: '', doc_type: 'other' })
  const [brandingForm, setBrandingForm] = useState({ logo_url: '', primary_color: '', domain: '' })

  const load = async () => {
    setLoading(true)
    try {
      const [msg, docs, cl] = await Promise.all([
        apiFetch<PortalMessage[]>('/portal/messages'),
        apiFetch<PortalDocument[]>('/portal/documents'),
        apiFetch<Client[]>('/clients/'),
      ])
      setMessages(msg)
      setDocuments(docs)
      setClients(cl)
      try {
        const br = await apiFetch<PortalBranding>('/portal/branding')
        setBranding(br)
        setBrandingForm({ logo_url: br.logo_url || '', primary_color: br.primary_color || '', domain: br.domain || '' })
      } catch {}
    } catch {} finally {
      setLoading(false)
    }
  }

  useEffect(() => { load() }, [])

  const handleSendMessage = async (e: React.FormEvent) => {
    e.preventDefault()
    await apiFetch('/portal/messages', {
      method: 'POST',
      body: JSON.stringify({ ...messageForm, message_type: 'general' }),
    })
    setMessageForm({ client_id: '', content: '' })
    load()
  }

  const handleUploadDoc = async (e: React.FormEvent) => {
    e.preventDefault()
    await apiFetch('/portal/documents/upload', {
      method: 'POST',
      body: JSON.stringify(docForm),
    })
    setDocForm({ client_id: '', file_url: '', file_name: '', doc_type: 'other' })
    load()
  }

  const handleSaveBranding = async (e: React.FormEvent) => {
    e.preventDefault()
    await apiFetch('/portal/branding', {
      method: 'PUT',
      body: JSON.stringify(brandingForm),
    })
    load()
  }

  const handleMarkRead = async (msgId: string) => {
    await apiFetch(`/portal/messages/${msgId}/read`, { method: 'PUT' })
    load()
  }

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
        <h1 className="text-3xl font-bold tracking-tight">Client Portal</h1>
        <p className="text-muted-foreground mt-1">Manage client communications, documents, and branding.</p>
      </div>

      <div className="flex gap-1 border-b">
        {(['messages', 'documents', 'branding'] as const).map((tab) => {
          const icons: Record<string, React.ElementType> = {
            messages: MessageSquare,
            documents: FileText,
            branding: Palette,
          }
          const Icon = icons[tab]
          return (
            <button
              key={tab}
              onClick={() => setActiveTab(tab)}
              className={`flex items-center gap-2 px-4 py-2 text-sm font-medium border-b-2 transition-colors ${
                activeTab === tab ? 'border-primary text-primary' : 'border-transparent text-muted-foreground hover:text-foreground'
              }`}
            >
              <Icon className="w-4 h-4" />
              {tab.charAt(0).toUpperCase() + tab.slice(1)}
            </button>
          )
        })}
      </div>

      {activeTab === 'messages' && (
        <div className="grid grid-cols-2 gap-6">
          <div>
            <Card>
              <CardHeader><CardTitle className="text-base">Messages</CardTitle></CardHeader>
              <CardContent className="space-y-3">
                {messages.length === 0 ? (
                  <p className="text-sm text-muted-foreground">No messages yet.</p>
                ) : (
                  messages.map((m) => (
                    <div
                      key={m.id}
                      className="p-3 rounded-lg border hover:bg-muted/50 transition-colors cursor-pointer"
                      onClick={() => handleMarkRead(m.id)}
                    >
                      <div className="flex items-center justify-between mb-1">
                        <Badge variant="outline" className="text-xs">{m.sender_type}</Badge>
                        {!m.is_read && <Badge variant="success" className="text-xs">New</Badge>}
                      </div>
                      <p className="text-sm">{m.content}</p>
                      <p className="text-xs text-muted-foreground mt-1">
                        {new Date(m.created_at).toLocaleString()}
                      </p>
                    </div>
                  ))
                )}
              </CardContent>
            </Card>
          </div>
          <div>
            <Card>
              <CardHeader><CardTitle className="text-base">Send Message</CardTitle></CardHeader>
              <CardContent>
                <form onSubmit={handleSendMessage} className="space-y-4">
                  <div>
                    <label className="text-sm font-medium block mb-1">Client</label>
                    <select
                      className="flex h-9 w-full rounded-md border border-input bg-background px-3 py-1 text-sm shadow-sm focus-visible:outline-none focus-visible:ring-1 focus-visible:ring-ring"
                      value={messageForm.client_id}
                      onChange={(e) => setMessageForm((f) => ({ ...f, client_id: e.target.value }))}
                      required
                    >
                      <option value="">Select client</option>
                      {clients.map((c) => (
                        <option key={c.id} value={c.id}>{c.name}</option>
                      ))}
                    </select>
                  </div>
                  <div>
                    <label className="text-sm font-medium block mb-1">Message</label>
                    <textarea
                      className="flex w-full rounded-md border border-input bg-background px-3 py-2 text-sm shadow-sm placeholder:text-muted-foreground focus-visible:outline-none focus-visible:ring-1 focus-visible:ring-ring min-h-[100px]"
                      value={messageForm.content}
                      onChange={(e) => setMessageForm((f) => ({ ...f, content: e.target.value }))}
                      required
                    />
                  </div>
                  <Button type="submit" size="sm" className="gap-2">
                    <Send className="w-4 h-4" /> Send
                  </Button>
                </form>
              </CardContent>
            </Card>
          </div>
        </div>
      )}

      {activeTab === 'documents' && (
        <div className="grid grid-cols-2 gap-6">
          <div>
            <Card>
              <CardHeader><CardTitle className="text-base">Documents</CardTitle></CardHeader>
              <CardContent className="space-y-3">
                {documents.length === 0 ? (
                  <p className="text-sm text-muted-foreground">No documents uploaded.</p>
                ) : (
                  documents.map((d) => (
                    <div key={d.id} className="flex items-center gap-3 p-3 rounded-lg border">
                      <FileText className="w-8 h-8 text-muted-foreground shrink-0" />
                      <div className="flex-1 min-w-0">
                        <p className="text-sm font-medium truncate">{d.file_name}</p>
                        <div className="flex items-center gap-2 text-xs text-muted-foreground">
                          <span>{d.doc_type}</span>
                          <span>{d.uploaded_by}</span>
                        </div>
                      </div>
                    </div>
                  ))
                )}
              </CardContent>
            </Card>
          </div>
          <div>
            <Card>
              <CardHeader><CardTitle className="text-base">Upload Document</CardTitle></CardHeader>
              <CardContent>
                <form onSubmit={handleUploadDoc} className="space-y-4">
                  <div>
                    <label className="text-sm font-medium block mb-1">Client</label>
                    <select
                      className="flex h-9 w-full rounded-md border border-input bg-background px-3 py-1 text-sm shadow-sm focus-visible:outline-none focus-visible:ring-1 focus-visible:ring-ring"
                      value={docForm.client_id}
                      onChange={(e) => setDocForm((f) => ({ ...f, client_id: e.target.value }))}
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
                    <Input value={docForm.file_name} onChange={(e) => setDocForm((f) => ({ ...f, file_name: e.target.value }))} required />
                  </div>
                  <div>
                    <label className="text-sm font-medium block mb-1">File URL</label>
                    <Input value={docForm.file_url} onChange={(e) => setDocForm((f) => ({ ...f, file_url: e.target.value }))} required />
                  </div>
                  <div>
                    <label className="text-sm font-medium block mb-1">Type</label>
                    <select
                      className="flex h-9 w-full rounded-md border border-input bg-background px-3 py-1 text-sm shadow-sm focus-visible:outline-none focus-visible:ring-1 focus-visible:ring-ring"
                      value={docForm.doc_type}
                      onChange={(e) => setDocForm((f) => ({ ...f, doc_type: e.target.value }))}
                    >
                      <option value="receipt">Receipt</option>
                      <option value="statement">Statement</option>
                      <option value="tax_doc">Tax Document</option>
                      <option value="contract">Contract</option>
                      <option value="other">Other</option>
                    </select>
                  </div>
                  <Button type="submit" size="sm" className="gap-2">
                    <Upload className="w-4 h-4" /> Upload
                  </Button>
                </form>
              </CardContent>
            </Card>
          </div>
        </div>
      )}

      {activeTab === 'branding' && (
        <Card>
          <CardHeader><CardTitle className="text-base">Portal Branding</CardTitle></CardHeader>
          <CardContent>
            <form onSubmit={handleSaveBranding} className="space-y-4 max-w-md">
              <div>
                <label className="text-sm font-medium block mb-1">Logo URL</label>
                <Input value={brandingForm.logo_url} onChange={(e) => setBrandingForm((f) => ({ ...f, logo_url: e.target.value }))} />
              </div>
              <div>
                <label className="text-sm font-medium block mb-1">Primary Color</label>
                <Input value={brandingForm.primary_color} onChange={(e) => setBrandingForm((f) => ({ ...f, primary_color: e.target.value }))} placeholder="#3b82f6" />
              </div>
              <div>
                <label className="text-sm font-medium block mb-1">Domain</label>
                <Input value={brandingForm.domain} onChange={(e) => setBrandingForm((f) => ({ ...f, domain: e.target.value }))} placeholder="portal.yourfirm.com" />
              </div>
              <Button type="submit" size="sm">Save Branding</Button>
            </form>
          </CardContent>
        </Card>
      )}
    </div>
  )
}
