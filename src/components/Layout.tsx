import React from 'react'
import { Sidebar } from './Sidebar'
import { Header } from './Header'
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
      <div className="flex flex-1 flex-col overflow-hidden">
        <Header />
        <main className="flex-1 overflow-auto p-4 lg:p-6 text-gray-900 dark:text-gray-50">
          {children}
        </main>
      </div>
    </div>
  )
}