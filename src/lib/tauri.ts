import { invoke } from '@tauri-apps/api/core'

export interface FileInfo {
  name: string
  path: string
  size: number
  modified?: string
  is_docx: boolean
}

export const tauriApi = {
  greet: (name: string): Promise<string> => invoke('greet', { name }),
  
  browseFolder: (): Promise<FileInfo[]> => invoke('browse_folder'),
  
  readFileContent: (filePath: string): Promise<string> => 
    invoke('read_file_content', { filePath }),
  
  gradeSubmission: (request: {
    submission_content: string
    system_prompt: string
    user_prompt: string
    provider: string
    model: string
    api_key: string
    temperature: number
  }): Promise<{ success: boolean; feedback?: string; error?: string }> => 
    invoke('grade_submission', { request }),
    
  testLLMConnection: (provider: string, apiKey: string): Promise<boolean> => 
    invoke('test_llm_connection', { provider, apiKey }),
}