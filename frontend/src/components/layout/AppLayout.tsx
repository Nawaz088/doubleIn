import * as React from 'react'
import { Link, Outlet, useLocation } from 'react-router-dom'
import {
  LayoutDashboard,
  Users,
  ListTodo,
  Landmark,
  FileSearch,
  BarChart3,
  Receipt,
  FileClock,
  UserSquare2,
  Inbox,
  FileText,
  Plug,
  Settings,
  TrendingUp,
  LogOut,
  Sun,
  Moon,
  IndianRupee,
  BookA,
} from 'lucide-react'
import { cn } from '@/lib/utils'
import { useAuth } from '@/context/AuthContext'
import { useTheme } from '@/context/ThemeContext'
import { Button } from '@/components/ui/button'

const navItems = [
  { icon: LayoutDashboard, label: 'Dashboard', href: '/' },
  { icon: Users, label: 'Clients', href: '/clients' },
  { icon: ListTodo, label: 'Tasks', href: '/tasks' },
  { icon: Landmark, label: 'Bank Feeds', href: '/bank-feeds' },
  { icon: TrendingUp, label: 'Scorecards', href: '/scorecards' },
  { icon: FileSearch, label: 'File Review', href: '/file-review' },
  { icon: BarChart3, label: 'Reports', href: '/reports' },
  { icon: Receipt, label: 'Receipts', href: '/receipts' },
  { icon: FileClock, label: 'Accruals', href: '/accruals' },
  { icon: BookA, label: 'Chart of Accts', href: '/chart-of-accounts' },
  { icon: UserSquare2, label: 'Portal', href: '/portal' },
  { icon: Inbox, label: 'Inbox', href: '/inbox' },
  { icon: FileText, label: 'Tax', href: '/tax' },
  { icon: IndianRupee, label: 'GST', href: '/gst' },
  { icon: Landmark, label: 'TDS', href: '/tds' },
  { icon: Plug, label: 'Integrations', href: '/integrations' },
  { icon: Settings, label: 'Settings', href: '/settings' },
]

export function AppLayout() {
  const { user, logout } = useAuth()
  const { theme, toggleTheme } = useTheme()
  const location = useLocation()

  return (
    <div className="flex h-screen overflow-hidden">
      <aside className="w-56 border-r bg-card flex flex-col shrink-0">
        <div className="p-4 border-b">
          <h1 className="text-lg font-bold tracking-tight">DoubleHQ</h1>
        </div>

        <nav className="flex-1 overflow-y-auto p-2 space-y-1">
          {navItems.map((item) => {
            const isActive = item.href === '/'
              ? location.pathname === '/'
              : location.pathname.startsWith(item.href)
            return (
              <Link
                key={item.href}
                to={item.href}
                className={cn(
                  'flex items-center gap-3 px-3 py-2 rounded-lg text-sm transition-colors',
                  isActive
                    ? 'bg-primary/10 text-primary font-medium'
                    : 'text-muted-foreground hover:bg-accent hover:text-foreground',
                )}
              >
                <item.icon className="w-4 h-4" />
                {item.label}
              </Link>
            )
          })}
        </nav>

        <div className="p-3 border-t space-y-2">
          <Button variant="ghost" size="sm" className="w-full justify-start gap-2" onClick={toggleTheme}>
            {theme === 'dark' ? <Sun className="w-4 h-4" /> : <Moon className="w-4 h-4" />}
            {theme === 'dark' ? 'Light Mode' : 'Dark Mode'}
          </Button>
          <div className="flex items-center gap-2">
            <div className="w-7 h-7 rounded-full bg-primary flex items-center justify-center text-xs font-bold shrink-0">
              {user?.name?.charAt(0)?.toUpperCase()}
            </div>
            <div className="flex-1 min-w-0">
              <p className="text-sm font-medium truncate">{user?.name}</p>
              <p className="text-xs text-muted-foreground truncate">{user?.org_name}</p>
            </div>
          </div>
          <Button variant="ghost" size="sm" className="w-full justify-start gap-2" onClick={logout}>
            <LogOut className="w-3 h-3" />
            Sign out
          </Button>
        </div>
      </aside>

      <main className="flex-1 overflow-y-auto">
        <div className="p-6">
          <Outlet />
        </div>
      </main>
    </div>
  )
}
