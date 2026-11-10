export type UsageLimit = { kind: string; percentUsed: number; resetsAt?: string }

export type Usage = {
  tokens?: number
  window: number
  percent?: number
  limits: UsageLimit[]
  costUsd?: number
  isCached?: boolean
}

export type Progress = {
  status: 'idle' | 'loading' | 'done' | 'error'
  text: string
}

declare module 'claude-code' {
  interface PluginState {
    'usage-progress': {
      usage: Usage | null
      isPinned: boolean
      progress: Progress
    }
  }
}
