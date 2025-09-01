import { invoke } from '@tauri-apps/api/core'
import { open } from '@tauri-apps/plugin-dialog'

export interface FileInfo {
  name: string
  path: string
  size: number
  modified?: string
  is_docx: boolean
}

export const tauriApi = {
  greet: (name: string): Promise<string> => invoke('greet', { name }),
  
  browseFolder: async (): Promise<FileInfo[]> => {
    // Open folder selection dialog
    const selected = await open({
      directory: true,
      multiple: false,
      title: 'Select Folder with Submissions'
    })
    
    if (!selected) {
      throw new Error('No folder selected')
    }
    
    // Pass the selected folder path to the backend
    return invoke('browse_folder', { folderPath: selected })
  },
  
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
  
  browseSupportFiles: async (): Promise<FileInfo[]> => {
    // Open multiple file selection dialog
    const selected = await open({
      directory: false,
      multiple: true,
      title: 'Select Support Files (Rubric, Marking Guide, Guidelines)',
      filters: [{
        name: 'Documents',
        extensions: ['docx', 'doc', 'pdf', 'txt']
      }]
    })
    
    if (!selected || (Array.isArray(selected) && selected.length === 0)) {
      throw new Error('No files selected')
    }
    
    // Convert selected files to FileInfo format
    const files: FileInfo[] = []
    const selectedArray = Array.isArray(selected) ? selected : [selected]
    
    for (const filePath of selectedArray) {
      // Get file info (we'll need to implement this in Rust)
      const content = await invoke('read_file_content', { filePath }) as string
      const fileName = filePath.split(/[\\/]/).pop() || ''
      
      files.push({
        name: fileName,
        path: filePath,
        size: content.length, // Approximation
        is_docx: fileName.toLowerCase().endsWith('.docx')
      })
    }
    
    return files
  },
}