import React from 'react'
import { Check, Eye, EyeOff, ExternalLink } from 'lucide-react'
import { useAppStore, type LLMProvider } from '../stores/useAppStore'
import { cn } from '../lib/utils'

export function SettingsView() {
  const { 
    currentProvider, 
    setCurrentProvider, 
    providers, 
    updateProviderConfig 
  } = useAppStore()

  const [showApiKey, setShowApiKey] = React.useState<Record<LLMProvider, boolean>>({
    openai: false,
    anthropic: false,
    groq: false,
    gemini: false,
    ollama: false,
    openrouter: false,
  })

  const providerInfo = {
    openai: {
      name: 'OpenAI',
      description: 'GPT-3.5, GPT-4, and GPT-4 Turbo models',
      website: 'https://platform.openai.com',
      models: ['gpt-3.5-turbo', 'gpt-4', 'gpt-4-turbo', 'gpt-4o'],
      requiresApiKey: true,
    },
    anthropic: {
      name: 'Anthropic',
      description: 'Claude 3 models (Haiku, Sonnet, Opus)',
      website: 'https://console.anthropic.com',
      models: ['claude-3-haiku-20240307', 'claude-3-sonnet-20240229', 'claude-3-opus-20240229'],
      requiresApiKey: true,
    },
    groq: {
      name: 'Groq',
      description: 'Fast inference for Llama, Mixtral, and Gemma',
      website: 'https://console.groq.com',
      models: ['llama-3.1-70b-versatile', 'mixtral-8x7b-32768', 'gemma-7b-it'],
      requiresApiKey: true,
    },
    gemini: {
      name: 'Google Gemini',
      description: 'Gemini Pro and Ultra models',
      website: 'https://makersuite.google.com/app/apikey',
      models: ['gemini-1.5-pro', 'gemini-1.5-flash', 'gemini-1.0-pro'],
      requiresApiKey: true,
    },
    ollama: {
      name: 'Ollama',
      description: 'Local LLM inference',
      website: 'https://ollama.ai',
      models: ['llama3', 'mistral', 'codellama', 'phi3'],
      requiresApiKey: false,
    },
    openrouter: {
      name: 'OpenRouter',
      description: 'Access to multiple models through one API',
      website: 'https://openrouter.ai',
      models: ['openai/gpt-4-turbo', 'anthropic/claude-3-opus', 'meta-llama/llama-3-70b'],
      requiresApiKey: true,
    },
  } as const

  const toggleApiKeyVisibility = (provider: LLMProvider) => {
    setShowApiKey(prev => ({ ...prev, [provider]: !prev[provider] }))
  }

  return (
    <div className="max-w-4xl">
      <div className="mb-6">
        <h1 className="text-2xl font-bold">Provider Settings</h1>
        <p className="text-muted-foreground">Configure your LLM providers and models</p>
      </div>

      <div className="grid gap-6 md:grid-cols-2">
        {(Object.keys(providerInfo) as LLMProvider[]).map((provider) => {
          const info = providerInfo[provider]
          const config = providers[provider]
          const isActive = currentProvider === provider
          const isConfigured = info.requiresApiKey ? !!config.apiKey : true

          return (
            <div
              key={provider}
              className={cn(
                "rounded-lg border p-6 transition-colors",
                isActive ? "border-primary bg-primary/5" : "border-border bg-card"
              )}
            >
              <div className="flex items-start justify-between mb-4">
                <div className="flex items-center gap-3">
                  <div className={cn(
                    "h-3 w-3 rounded-full",
                    isConfigured ? "bg-green-500" : "bg-red-500"
                  )} />
                  <div>
                    <h3 className="font-semibold">{info.name}</h3>
                    <p className="text-sm text-muted-foreground">{info.description}</p>
                  </div>
                </div>
                <button
                  onClick={() => window.open(info.website, '_blank')}
                  className="rounded-md p-2 hover:bg-accent"
                >
                  <ExternalLink className="h-4 w-4" />
                </button>
              </div>

              {/* API Key Input */}
              {info.requiresApiKey && (
                <div className="space-y-2 mb-4">
                  <label className="text-sm font-medium">API Key</label>
                  <div className="relative">
                    <input
                      type={showApiKey[provider] ? "text" : "password"}
                      value={config.apiKey || ''}
                      onChange={(e) => updateProviderConfig(provider, { apiKey: e.target.value })}
                      placeholder="Enter your API key"
                      className="w-full rounded-md border border-input bg-background px-3 py-2 pr-10 text-sm ring-offset-background placeholder:text-muted-foreground focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring"
                    />
                    <button
                      type="button"
                      onClick={() => toggleApiKeyVisibility(provider)}
                      className="absolute right-3 top-2.5 rounded-md p-0.5 hover:bg-accent"
                    >
                      {showApiKey[provider] ? (
                        <EyeOff className="h-4 w-4" />
                      ) : (
                        <Eye className="h-4 w-4" />
                      )}
                    </button>
                  </div>
                </div>
              )}

              {/* Base URL for Ollama */}
              {provider === 'ollama' && (
                <div className="space-y-2 mb-4">
                  <label className="text-sm font-medium">Base URL</label>
                  <input
                    type="text"
                    value={config.baseUrl || ''}
                    onChange={(e) => updateProviderConfig(provider, { baseUrl: e.target.value })}
                    placeholder="http://localhost:11434"
                    className="w-full rounded-md border border-input bg-background px-3 py-2 text-sm ring-offset-background placeholder:text-muted-foreground focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring"
                  />
                </div>
              )}

              {/* Model Selection */}
              <div className="space-y-2 mb-4">
                <label className="text-sm font-medium">Model</label>
                <select
                  value={config.model || ''}
                  onChange={(e) => updateProviderConfig(provider, { model: e.target.value })}
                  className="w-full rounded-md border border-input bg-background px-3 py-2 text-sm ring-offset-background focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring"
                >
                  <option value="">Select a model</option>
                  {info.models.map((model) => (
                    <option key={model} value={model}>
                      {model}
                    </option>
                  ))}
                </select>
              </div>

              {/* Temperature */}
              <div className="space-y-2 mb-4">
                <label className="text-sm font-medium">
                  Temperature: {config.temperature?.toFixed(1) || '0.7'}
                </label>
                <input
                  type="range"
                  min="0"
                  max="1"
                  step="0.1"
                  value={config.temperature || 0.7}
                  onChange={(e) => updateProviderConfig(provider, { temperature: parseFloat(e.target.value) })}
                  className="w-full"
                />
              </div>

              {/* Set as Active Button */}
              <button
                onClick={() => setCurrentProvider(provider)}
                disabled={!isConfigured}
                className={cn(
                  "flex w-full items-center justify-center gap-2 rounded-md px-4 py-2 text-sm font-medium transition-colors",
                  isActive
                    ? "bg-primary text-primary-foreground"
                    : isConfigured
                    ? "border border-input hover:bg-accent"
                    : "bg-muted text-muted-foreground cursor-not-allowed"
                )}
              >
                {isActive && <Check className="h-4 w-4" />}
                {isActive ? 'Active Provider' : 'Use This Provider'}
              </button>
            </div>
          )
        })}
      </div>
    </div>
  )
}