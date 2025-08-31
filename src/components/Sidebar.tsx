import { FileText, Settings, History, Folder, Zap } from 'lucide-react'
import { useAppStore } from '../stores/useAppStore'
import { cn } from '../lib/utils'

export function Sidebar() {
  const { 
    sidebarOpen, 
    currentView, 
    setCurrentView,
    selectedFiles,
    currentProvider 
  } = useAppStore()

  const menuItems = [
    {
      key: 'grading' as const,
      label: 'Grade Submissions',
      icon: FileText,
      badge: selectedFiles.length > 0 ? selectedFiles.length : null
    },
    {
      key: 'settings' as const,
      label: 'Provider Settings',
      icon: Settings,
      badge: null
    },
    {
      key: 'history' as const,
      label: 'Grading History',
      icon: History,
      badge: null
    },
  ]

  return (
    <div className="flex h-full flex-col">
      {/* Logo/Brand */}
      <div className="border-b p-4">
        <div className="flex items-center gap-3">
          <div className="flex h-8 w-8 items-center justify-center rounded-lg bg-primary text-primary-foreground">
            <Zap className="h-4 w-4" />
          </div>
          {sidebarOpen && (
            <div className="flex flex-col">
              <span className="text-sm font-semibold">AI Assessor</span>
              <span className="text-xs text-muted-foreground capitalize">
                {currentProvider}
              </span>
            </div>
          )}
        </div>
      </div>

      {/* Navigation */}
      <nav className="flex-1 space-y-1 p-2">
        {menuItems.map((item) => {
          const Icon = item.icon
          const isActive = currentView === item.key
          
          return (
            <button
              key={item.key}
              onClick={() => setCurrentView(item.key)}
              className={cn(
                "flex w-full items-center gap-3 rounded-lg px-3 py-2 text-left text-sm transition-colors",
                isActive
                  ? "bg-primary text-primary-foreground"
                  : "text-muted-foreground hover:bg-accent hover:text-accent-foreground"
              )}
            >
              <Icon className={cn("h-4 w-4", sidebarOpen ? "flex-shrink-0" : "")} />
              {sidebarOpen && (
                <>
                  <span className="flex-1">{item.label}</span>
                  {item.badge && (
                    <span className="flex h-5 w-5 items-center justify-center rounded-full bg-muted text-xs">
                      {item.badge}
                    </span>
                  )}
                </>
              )}
            </button>
          )
        })}
      </nav>

      {/* Quick Actions */}
      {sidebarOpen && (
        <div className="border-t p-4">
          <div className="space-y-2">
            <button className="flex w-full items-center gap-3 rounded-lg px-3 py-2 text-left text-sm text-muted-foreground hover:bg-accent hover:text-accent-foreground">
              <Folder className="h-4 w-4" />
              Browse Files
            </button>
          </div>
        </div>
      )}
    </div>
  )
}