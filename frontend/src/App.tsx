import { Routes, Route, Navigate } from 'react-router-dom'
import { useAuth } from './context/AuthContext'
import { AppLayout } from './components/layout/AppLayout'
import { LoginPage } from './pages/LoginPage'
import { RegisterPage } from './pages/RegisterPage'
import { DashboardPage } from './pages/DashboardPage'
import { ScorecardsPage } from './pages/ScorecardsPage'
import { ScorecardDetailPage } from './pages/ScorecardDetailPage'
import { ScorecardBuilderPage } from './pages/ScorecardBuilderPage'
import { KpiDefinitionsPage } from './pages/KpiDefinitionsPage'
import { ClientsPage } from './pages/ClientsPage'
import { ClientDetailPage } from './pages/ClientDetailPage'
import { TasksPage } from './pages/TasksPage'
import { TaskDetailPage } from './pages/TaskDetailPage'
import { ClosePage } from './pages/ClosePage'
import { BankFeedsPage } from './pages/BankFeedsPage'
import { JournalEntriesPage } from './pages/JournalEntriesPage'
import { ReportsPage } from './pages/ReportsPage'
import { ReportDetailPage } from './pages/ReportDetailPage'
import { FileReviewPage } from './pages/FileReviewPage'
import { FileReviewDetailPage } from './pages/FileReviewDetailPage'
import { PortalPage } from './pages/PortalPage'
import { ReceiptsPage } from './pages/ReceiptsPage'
import { AccrualsPage } from './pages/AccrualsPage'
import { TaxPage } from './pages/TaxPage'
import { InboxPage } from './pages/InboxPage'
import { IntegrationsPage } from './pages/IntegrationsPage'
import { GstPage } from './pages/GstPage'
import { ChartOfAccountsPage } from './pages/ChartOfAccountsPage'
import { SettingsPage } from './pages/SettingsPage'

export default function App() {
  const { isAuthenticated, isLoading } = useAuth()

  if (isLoading) {
    return (
      <div className="flex items-center justify-center h-screen">
        <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-primary" />
      </div>
    )
  }

  if (!isAuthenticated) {
    return (
      <Routes>
        <Route path="/login" element={<LoginPage />} />
        <Route path="/register" element={<RegisterPage />} />
        <Route path="*" element={<Navigate to="/login" replace />} />
      </Routes>
    )
  }

  return (
    <Routes>
      <Route element={<AppLayout />}>
        <Route path="/" element={<DashboardPage />} />
        <Route path="/scorecards" element={<ScorecardsPage />} />
        <Route path="/scorecards/:id" element={<ScorecardDetailPage />} />
        <Route path="/scorecards/new" element={<ScorecardBuilderPage />} />
        <Route path="/scorecards/:id/edit" element={<ScorecardBuilderPage />} />
        <Route path="/scorecards/definitions" element={<KpiDefinitionsPage />} />
        <Route path="/clients" element={<ClientsPage />} />
        <Route path="/clients/:id" element={<ClientDetailPage />} />
        <Route path="/clients/:id/close" element={<ClosePage />} />
        <Route path="/tasks" element={<TasksPage />} />
        <Route path="/tasks/:id" element={<TaskDetailPage />} />
        <Route path="/bank-feeds" element={<BankFeedsPage />} />
        <Route path="/journal-entries" element={<JournalEntriesPage />} />
        <Route path="/reports" element={<ReportsPage />} />
        <Route path="/reports/:id" element={<ReportDetailPage />} />
        <Route path="/file-review" element={<FileReviewPage />} />
        <Route path="/file-review/:id" element={<FileReviewDetailPage />} />
        <Route path="/portal" element={<PortalPage />} />
        <Route path="/receipts" element={<ReceiptsPage />} />
        <Route path="/accruals" element={<AccrualsPage />} />
        <Route path="/tax" element={<TaxPage />} />
        <Route path="/inbox" element={<InboxPage />} />
        <Route path="/integrations" element={<IntegrationsPage />} />
        <Route path="/gst" element={<GstPage />} />
        <Route path="/chart-of-accounts" element={<ChartOfAccountsPage />} />
        <Route path="/settings" element={<SettingsPage />} />
        <Route path="*" element={<Navigate to="/" replace />} />
      </Route>
    </Routes>
  )
}
