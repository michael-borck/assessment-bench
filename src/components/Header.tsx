import { Menu, Settings, History, FileText } from 'lucide-react'
import { useAppStore } from '../stores/useAppStore'
import { cn } from '../lib/utils'

export function Header() {
  const { 
    sidebarOpen, 
    setSidebarOpen, 
    currentView, 
    setCurrentView,
    currentProvider,
    providers 
  } = useAppStore()

  const currentProviderConfig = providers[currentProvider]

  return (
    <header className="border-b bg-card px-4 py-3">
      <div className="flex items-center justify-between">
        <div className="flex items-center gap-4">
          <button
            onClick={() => setSidebarOpen(!sidebarOpen)}
            className="rounded-md p-2 hover:bg-accent"
          >
            <Menu className="h-5 w-5" />
          </button>
          
          <h1 className="text-xl font-semibold">AI Assessor</h1>
          
          <div className="hidden md:flex items-center gap-2">
            <button
              onClick={() => setCurrentView('grading')}
              className={cn(
                "flex items-center gap-2 rounded-md px-3 py-2 text-sm transition-colors",
                currentView === 'grading' 
                  ? "bg-primary text-primary-foreground" 
                  : "hover:bg-accent"
              )}
            >
              <FileText className="h-4 w-4" />
              Grade
            </button>
            <button
              onClick={() => setCurrentView('settings')}
              className={cn(
                "flex items-center gap-2 rounded-md px-3 py-2 text-sm transition-colors",
                currentView === 'settings' 
                  ? "bg-primary text-primary-foreground" 
                  : "hover:bg-accent"
              )}
            >
              <Settings className="h-4 w-4" />
              Settings
            </button>
            <button
              onClick={() => setCurrentView('history')}
              className={cn(
                "flex items-center gap-2 rounded-md px-3 py-2 text-sm transition-colors",
                currentView === 'history' 
                  ? "bg-primary text-primary-foreground" 
                  : "hover:bg-accent"
              )}
            >
              <History className="h-4 w-4" />
              History
            </button>
          </div>
        </div>

        <div className="flex items-center gap-3">
          <div className="hidden sm:flex items-center gap-2 text-sm text-muted-foreground">
            <div className="flex items-center gap-1">
              <div className={cn(
                "h-2 w-2 rounded-full",
                currentProviderConfig.apiKey ? "bg-green-500" : "bg-red-500"
              )} />
              <span className="capitalize">{currentProvider}</span>
            </div>
            {currentProviderConfig.model && (
              <span className="text-xs">• {currentProviderConfig.model}</span>
            )}
          </div>
        </div>
      </div>
    </header>
  )
}