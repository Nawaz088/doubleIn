import * as React from 'react'
import { Link, Outlet, useLocation } from 'react-router-dom'
import {
  LayoutDashboard, Users, ListTodo, Landmark, FileSearch, BarChart3,
  Receipt, FileClock, UserSquare2, Inbox, FileText, Plug, Settings,
  TrendingUp, LogOut, Sun, Moon, IndianRupee, BookA, Search, Bell,
  ChevronLeft, ChevronRight, PanelRight,
} from 'lucide-react'
import { cn } from '@/lib/utils'
import { useAuth } from '@/context/AuthContext'
import { useTheme } from '@/context/ThemeContext'
import { Button } from '@/components/ui/button'

const navGroups = [
  {
    label: 'Practice',
    items: [
      { icon: LayoutDashboard, label: 'Dashboard', href: '/' },
      { icon: Users, label: 'Clients', href: '/clients' },
      { icon: ListTodo, label: 'Tasks', href: '/tasks' },
      { icon: TrendingUp, label: 'Scorecards', href: '/scorecards' },
    ],
  },
  {
    label: 'Close',
    items: [
      { icon: Landmark, label: 'Bank Feeds', href: '/bank-feeds' },
      { icon: FileSearch, label: 'File Review', href: '/file-review' },
      { icon: BarChart3, label: 'Reports', href: '/reports' },
      { icon: Receipt, label: 'Receipts', href: '/receipts' },
      { icon: FileClock, label: 'Accruals', href: '/accruals' },
      { icon: BookA, label: 'Chart of Accts', href: '/chart-of-accounts' },
    ],
  },
  {
    label: 'Client',
    items: [
      { icon: UserSquare2, label: 'Portal', href: '/portal' },
      { icon: Inbox, label: 'Inbox', href: '/inbox' },
    ],
  },
  {
    label: 'Compliance',
    items: [
      { icon: FileText, label: 'Tax', href: '/tax' },
      { icon: IndianRupee, label: 'GST', href: '/gst' },
      { icon: Landmark, label: 'TDS', href: '/tds' },
    ],
  },
  {
    label: 'System',
    items: [
      { icon: Plug, label: 'Integrations', href: '/integrations' },
      { icon: Settings, label: 'Settings', href: '/settings' },
    ],
  },
]

export function AppLayout() {
  const { user, logout } = useAuth()
  const { theme, toggleTheme } = useTheme()
  const location = useLocation()
  const [collapsed, setCollapsed] = React.useState(false)

  const isActive = (href: string) =>
    href === '/' ? location.pathname === '/' : location.pathname.startsWith(href)

  return (
    <div className="flex h-screen overflow-hidden">
      <aside
        className={cn(
          'flex flex-col shrink-0 transition-all duration-200 border-r bg-sidebar',
          collapsed ? 'w-16' : 'w-60',
        )}
      >
        <div className="flex items-center gap-3 px-4 h-14 border-b border-white/5">
          <div className="flex items-center justify-center w-8 h-8 rounded-lg bg-primary shrink-0">
            <span className="text-sm font-bold text-white">D</span>
          </div>
          {!collapsed && (
            <span className="text-sm font-semibold tracking-tight">DoubleIn</span>
          )}
        </div>

        <nav className="flex-1 overflow-y-auto scrollbar-thin px-2 py-3 space-y-5">
          {navGroups.map((group) => (
            <div key={group.label}>
              {!collapsed && (
                <p className="px-3 mb-1.5 text-[10px] font-semibold text-sidebar-foreground uppercase tracking-widest">
                  {group.label}
                </p>
              )}
              <div className="space-y-0.5">
                {group.items.map((item) => {
                  const active = isActive(item.href)
                  return (
                    <Link
                      key={item.href}
                      to={item.href}
                      className={cn(
                        'flex items-center gap-3 px-3 py-2 rounded-lg text-sm transition-all',
                        collapsed && 'justify-center px-2',
                        active
                          ? 'bg-sidebar-active-bg text-sidebar-active font-medium'
                          : 'text-sidebar-foreground hover:text-foreground hover:bg-white/5',
                      )}
                      title={collapsed ? item.label : undefined}
                    >
                      <item.icon className="w-4 h-4 shrink-0" />
                      {!collapsed && <span className="truncate">{item.label}</span>}
                    </Link>
                  )
                })}
              </div>
            </div>
          ))}
        </nav>

        <div className="border-t border-white/5 p-2 space-y-1">
          <button
            onClick={() => setCollapsed(!collapsed)}
            className="flex items-center gap-3 w-full px-3 py-2 rounded-lg text-sm text-sidebar-foreground hover:text-foreground hover:bg-white/5 transition-all"
          >
            {collapsed ? <ChevronRight className="w-4 h-4 mx-auto" /> : <><ChevronLeft className="w-4 h-4" /> Collapse</>}
          </button>
        </div>

        <div className="border-t border-white/5 p-3 space-y-2">
          <div className="flex items-center gap-3">
            <div className="w-8 h-8 rounded-full bg-primary/20 flex items-center justify-center text-xs font-bold text-primary shrink-0">
              {user?.name?.charAt(0)?.toUpperCase()}
            </div>
            {!collapsed && (
              <div className="flex-1 min-w-0">
                <p className="text-sm font-medium truncate text-foreground">{user?.name}</p>
                <p className="text-xs text-sidebar-foreground truncate">{user?.org_name}</p>
              </div>
            )}
          </div>
          <button
            onClick={logout}
            className="flex items-center gap-3 w-full px-3 py-2 rounded-lg text-sm text-sidebar-foreground hover:text-red-400 hover:bg-red-500/10 transition-all"
          >
            <LogOut className="w-4 h-4 shrink-0" />
            {!collapsed && <span>Sign out</span>}
          </button>
        </div>
      </aside>

      <div className="flex-1 flex flex-col min-w-0">
        <header className="flex items-center justify-between h-14 px-6 border-b bg-background/80 backdrop-blur-sm shrink-0">
          <div className="flex items-center gap-3">
            <div className="flex items-center gap-2 text-xs text-muted-foreground bg-muted rounded-lg px-3 py-1.5">
              <Search className="w-3.5 h-3.5" />
              <span>Search anything...</span>
              <kbd className="hidden sm:inline-flex items-center gap-0.5 rounded border bg-background px-1.5 py-0.5 text-[10px] font-medium text-muted-foreground">
                ⌘K
              </kbd>
            </div>
          </div>
          <div className="flex items-center gap-2">
            <button
              onClick={toggleTheme}
              className="p-2 rounded-lg text-muted-foreground hover:text-foreground hover:bg-accent transition-all"
            >
              {theme === 'dark' ? <Sun className="w-4 h-4" /> : <Moon className="w-4 h-4" />}
            </button>
            <button className="p-2 rounded-lg text-muted-foreground hover:text-foreground hover:bg-accent transition-all relative">
              <Bell className="w-4 h-4" />
              <span className="absolute top-1.5 right-1.5 w-2 h-2 rounded-full bg-primary ring-2 ring-background" />
            </button>
          </div>
        </header>

        <main className="flex-1 overflow-y-auto">
          <div className="p-6 lg:p-8 max-w-7xl mx-auto">
            <Outlet />
          </div>
        </main>
      </div>
    </div>
  )
}
