import { useState } from 'react'
import { invoke } from '@tauri-apps/api/core'
import './styles/App.css'

function App() {
  const [greetMsg, setGreetMsg] = useState('')
  const [name, setName] = useState('')

  async function greet() {
    setGreetMsg(await invoke('greet', { name }))
  }

  return (
    <div className="container">
      <h1>AI Assessor</h1>
      <p>Welcome to AI Assessor - Your intelligent grading assistant</p>
      
      <div className="row">
        <div>
          <input
            id="greet-input"
            onChange={(e) => setName(e.currentTarget.value)}
            placeholder="Enter a name..."
          />
          <button type="button" onClick={() => greet()}>
            Greet
          </button>
        </div>
      </div>

      <p>{greetMsg}</p>
      
      <div className="info">
        <p>This is a placeholder for the AI Assessor application.</p>
        <p>Features to implement:</p>
        <ul>
          <li>Multi-provider LLM support</li>
          <li>Document processing</li>
          <li>Batch grading</li>
          <li>Modern UI with split panels</li>
        </ul>
      </div>
    </div>
  )
}

export default App