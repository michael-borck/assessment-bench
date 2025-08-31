import React from 'react'
import { Sidebar } from './Sidebar'
import { useAppStore } from '../stores/useAppStore'
import { cn } from '../lib/utils'

interface LayoutProps {
  children: React.ReactNode
}

export function Layout({ children }: LayoutProps) {
  const sidebarOpen = useAppStore((state) => state.sidebarOpen)

  return (
    <div className="flex h-screen overflow-hidden bg-white dark:bg-gray-900">
      {/* Sidebar */}
      <div
        className={cn(
          "border-r border-gray-200 dark:border-gray-700 bg-white dark:bg-gray-800 transition-all duration-300",
          sidebarOpen ? "w-64" : "w-16"
        )}
      >
        <Sidebar />
      </div>

      {/* Main Content */}
      <main className="flex-1 overflow-auto bg-background text-foreground">
        {children}
      </main>
    </div>
  )
}