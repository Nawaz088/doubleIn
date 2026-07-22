import { cn } from '@/lib/utils'

const statusStyles: Record<string, string> = {
  active: 'bg-emerald-500/10 text-emerald-500 border-emerald-500/20',
  inactive: 'bg-gray-500/10 text-gray-400 border-gray-500/20',
  draft: 'bg-yellow-500/10 text-yellow-500 border-yellow-500/20',
  final: 'bg-blue-500/10 text-blue-500 border-blue-500/20',
  pending: 'bg-yellow-500/10 text-yellow-500 border-yellow-500/20',
  in_progress: 'bg-blue-500/10 text-blue-500 border-blue-500/20',
  done: 'bg-emerald-500/10 text-emerald-500 border-emerald-500/20',
  completed: 'bg-emerald-500/10 text-emerald-500 border-emerald-500/20',
  filed: 'bg-emerald-500/10 text-emerald-500 border-emerald-500/20',
  error: 'bg-red-500/10 text-red-500 border-red-500/20',
  posted: 'bg-violet-500/10 text-violet-500 border-violet-500/20',
  todo: 'bg-gray-500/10 text-gray-400 border-gray-500/20',
  review: 'bg-orange-500/10 text-orange-500 border-orange-500/20',
  ready_to_file: 'bg-emerald-500/10 text-emerald-500 border-emerald-500/20',
  paid: 'bg-emerald-500/10 text-emerald-500 border-emerald-500/20',
  cancelled: 'bg-red-500/10 text-red-500 border-red-500/20',
  deducted: 'bg-blue-500/10 text-blue-500 border-blue-500/20',
  deposited: 'bg-emerald-500/10 text-emerald-500 border-emerald-500/20',
}

const dotStyles: Record<string, string> = {
  active: 'bg-emerald-500',
  inactive: 'bg-gray-400',
  draft: 'bg-yellow-500',
  final: 'bg-blue-500',
  pending: 'bg-yellow-500',
  in_progress: 'bg-blue-500',
  done: 'bg-emerald-500',
  completed: 'bg-emerald-500',
  filed: 'bg-emerald-500',
  error: 'bg-red-500',
  posted: 'bg-violet-500',
  todo: 'bg-gray-400',
  review: 'bg-orange-500',
  ready_to_file: 'bg-emerald-500',
  paid: 'bg-emerald-500',
  cancelled: 'bg-red-500',
  deducted: 'bg-blue-500',
  deposited: 'bg-emerald-500',
}

interface StatusBadgeProps {
  status: string
  label?: string
  className?: string
}

export function StatusBadge({ status, label, className }: StatusBadgeProps) {
  return (
    <span
      className={cn(
        'inline-flex items-center gap-1.5 rounded-full border px-2.5 py-0.5 text-xs font-medium',
        statusStyles[status] || 'bg-gray-500/10 text-gray-400 border-gray-500/20',
        className,
      )}
    >
      <span className={cn('h-1.5 w-1.5 rounded-full', dotStyles[status] || 'bg-gray-400')} />
      {label || status.replace(/_/g, ' ')}
    </span>
  )
}
