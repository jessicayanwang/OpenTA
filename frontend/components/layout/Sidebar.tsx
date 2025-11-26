'use client'

import { LucideIcon } from 'lucide-react'
import Logo from '@/components/Logo'
import { cn } from '@/lib/utils'

export interface SidebarNavItem {
  id: string
  label: string
  icon: LucideIcon
  badge?: string
}

export interface SidebarProps {
  brand: {
    name: string
    role?: string
  }
  items: SidebarNavItem[]
  footerItems?: SidebarNavItem[]
  activeItem?: string
  onNavigate?: (item: SidebarNavItem) => void
  primaryAction?: {
    label: string
    icon: LucideIcon
    onClick: () => void
  }
}

const navBaseStyles =
  'w-full flex items-center justify-between rounded-2xl px-4 py-3 text-sm font-medium transition-all duration-200 border'

export function Sidebar({
  brand,
  items,
  footerItems = [],
  activeItem,
  onNavigate,
  primaryAction,
}: SidebarProps) {
  return (
    <aside className="flex min-h-screen w-72 flex-col border-r border-slate-200/70 bg-white px-5 py-6 text-slate-700">
      <div className="flex flex-col gap-2 pb-6 border-b border-slate-100/80 mb-6">
        <Logo size="lg" showText label={brand.name} />
        {brand.role && <p className="text-xs text-slate-500">{brand.role}</p>}
      </div>

      {primaryAction && (
        <button
          onClick={primaryAction.onClick}
          className="flex items-center justify-center gap-2 rounded-2xl px-5 py-3 bg-[#FF6B35] text-white font-semibold text-sm shadow-[0_15px_30px_rgba(255,107,53,0.35)] mb-6"
        >
          <primaryAction.icon className="w-4 h-4" />
          {primaryAction.label}
        </button>
      )}

      <nav className="space-y-2 flex-1">
        {items.map((item) => {
          const isActive = item.id === activeItem
          return (
            <button
              key={item.id}
              onClick={() => onNavigate?.(item)}
              className={cn(
                navBaseStyles,
                isActive
                  ? 'bg-orange-50 text-[#FF6B35] border-orange-100 shadow-sm'
                  : 'text-slate-600 border-transparent hover:border-slate-200 hover:bg-slate-50/80'
              )}
            >
              <div className="flex items-center gap-3">
                <item.icon className={cn('w-4 h-4', isActive ? 'text-[#FF6B35]' : 'text-slate-400')} />
                <span>{item.label}</span>
              </div>
              {item.badge && (
                <span
                  className={cn(
                    'text-xs font-semibold px-2 py-0.5 rounded-full',
                    isActive ? 'bg-white text-[#FF6B35]' : 'bg-slate-100 text-slate-600'
                  )}
                >
                  {item.badge}
                </span>
              )}
            </button>
          )
        })}
      </nav>

      {footerItems.length > 0 && (
        <div className="pt-6 mt-6 border-t border-slate-100/80 space-y-2">
          {footerItems.map((item) => (
            <button
              key={item.id}
              onClick={() => onNavigate?.(item)}
              className="w-full flex items-center gap-3 rounded-2xl px-4 py-3 text-sm text-slate-500 hover:text-slate-900 hover:bg-slate-50 border border-transparent hover:border-slate-200 transition-all"
            >
              <item.icon className="w-4 h-4" />
              <span className="flex-1 text-left">{item.label}</span>
            </button>
          ))}
        </div>
      )}
    </aside>
  )
}
