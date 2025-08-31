import { Layout } from './components/Layout'
import { GradingView } from './components/GradingView'
import { SettingsView } from './components/SettingsView'
import { HistoryView } from './components/HistoryView'
import { useAppStore } from './stores/useAppStore'

function App() {
  const currentView = useAppStore((state) => state.currentView)

  const renderCurrentView = () => {
    switch (currentView) {
      case 'grading':
        return <GradingView />
      case 'settings':
        return <SettingsView />
      case 'history':
        return <HistoryView />
      default:
        return <GradingView />
    }
  }

  return (
    <Layout>
      {renderCurrentView()}
    </Layout>
  )
}

export default App