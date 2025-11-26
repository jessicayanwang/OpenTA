'use client'

import { ReactNode } from 'react'
import { Search, Bell, CircleHelp } from 'lucide-react'
import { Sidebar, SidebarProps } from './Sidebar'

interface DashboardLayoutProps {
  sidebar: SidebarProps
  children: ReactNode
  topBarContent?: ReactNode
}

export function DashboardLayout({ sidebar, children, topBarContent }: DashboardLayoutProps) {
  return (
    <div className="min-h-screen flex bg-slate-50 text-slate-900">
      <Sidebar {...sidebar} />
      <div className="flex-1 flex flex-col">
        <header className="sticky top-0 z-30 border-b border-slate-200/80 bg-slate-50/80 backdrop-blur-xl">
          <div className="flex flex-col gap-4 px-5 py-4 sm:flex-row sm:items-center sm:justify-between lg:px-10">
            <div className="w-full sm:max-w-md">
              <label htmlFor="global-search" className="sr-only">
                Search
              </label>
              <div className="relative">
                <Search className="absolute left-4 top-1/2 -translate-y-1/2 text-slate-400 w-4 h-4" />
                <input
                  id="global-search"
                  type="search"
                  placeholder="Search course knowledge, students, or resources"
                  className="w-full rounded-full border border-slate-200 bg-white/80 px-12 py-3 text-sm text-slate-700 placeholder:text-slate-400 focus:outline-none focus:ring-2 focus:ring-orange-100 focus:border-orange-200"
                />
              </div>
            </div>
            <div className="flex items-center justify-end gap-3">
              {topBarContent}
              <button
                aria-label="Notifications"
                className="relative rounded-full border border-slate-200 bg-white p-2 text-slate-500 hover:text-slate-900 hover:border-slate-300 transition-colors"
              >
                <Bell className="w-5 h-5" />
                <span className="absolute -top-0.5 -right-0.5 h-2 w-2 rounded-full bg-[#FF6B35]"></span>
              </button>
              <button
                aria-label="Get help"
                className="rounded-full border border-slate-200 bg-white p-2 text-slate-500 hover:text-slate-900 hover:border-slate-300 transition-colors"
              >
                <CircleHelp className="w-5 h-5" />
              </button>
              <div className="flex items-center gap-3 rounded-full border border-slate-200 bg-white px-3 py-2">
                <div className="text-right">
                  <p className="text-sm font-semibold text-slate-900">Dr. Riley</p>
                  <p className="text-xs text-slate-500">Instructor</p>
                </div>
                <div className="h-10 w-10 rounded-full bg-gradient-to-br from-orange-400 to-orange-600 text-white font-semibold flex items-center justify-center">
                  DR
                </div>
              </div>
            </div>
          </div>
        </header>
        <main className="flex-1 px-5 py-6 lg:px-10 lg:py-10">{children}</main>
      </div>
    </div>
  )
}
