import { Clock, FileText, ExternalLink, Trash2 } from 'lucide-react'

export function HistoryView() {
  // TODO: Add actual history state management
  const mockHistory = [
    {
      id: '1',
      filename: 'student_assignment_01.docx',
      provider: 'openai',
      model: 'gpt-4-turbo',
      timestamp: '2024-08-30 14:30:00',
      status: 'completed',
    },
    {
      id: '2',
      filename: 'student_assignment_02.docx',
      provider: 'anthropic',
      model: 'claude-3-opus',
      timestamp: '2024-08-30 14:25:00',
      status: 'completed',
    }
  ]

  return (
    <div className="max-w-4xl">
      <div className="mb-6">
        <h1 className="text-2xl font-bold">Grading History</h1>
        <p className="text-muted-foreground">View and manage your previous grading sessions</p>
      </div>

      {mockHistory.length === 0 ? (
        <div className="flex flex-col items-center justify-center rounded-lg border border-dashed p-12 text-center">
          <Clock className="h-12 w-12 text-muted-foreground mb-4" />
          <h3 className="text-lg font-semibold mb-2">No grading history</h3>
          <p className="text-muted-foreground">Your graded submissions will appear here</p>
        </div>
      ) : (
        <div className="space-y-4">
          {mockHistory.map((item) => (
            <div
              key={item.id}
              className="rounded-lg border bg-card p-4 transition-colors hover:bg-accent/50"
            >
              <div className="flex items-center justify-between">
                <div className="flex items-center gap-4">
                  <FileText className="h-8 w-8 text-muted-foreground" />
                  <div>
                    <h3 className="font-medium">{item.filename}</h3>
                    <div className="flex items-center gap-4 text-sm text-muted-foreground">
                      <span className="capitalize">{item.provider}</span>
                      <span>•</span>
                      <span>{item.model}</span>
                      <span>•</span>
                      <span>{item.timestamp}</span>
                    </div>
                  </div>
                </div>
                
                <div className="flex items-center gap-2">
                  <span className="rounded-full bg-green-100 px-2 py-1 text-xs font-medium text-green-700 dark:bg-green-900 dark:text-green-300">
                    {item.status}
                  </span>
                  <button className="rounded-md p-2 hover:bg-accent">
                    <ExternalLink className="h-4 w-4" />
                  </button>
                  <button className="rounded-md p-2 hover:bg-accent text-red-600">
                    <Trash2 className="h-4 w-4" />
                  </button>
                </div>
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  )
}