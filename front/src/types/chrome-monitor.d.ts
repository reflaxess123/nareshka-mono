interface ChromeMonitorRequest {
  type: 'FETCH' | 'XHR';
  url: string;
  method: string;
  status: number | string;
  statusText?: string;
  error?: string;
  duration: number;
  timestamp: string;
  time: string;
}

interface ChromeMonitorLog {
  type: 'LOG' | 'ERROR' | 'WARN' | 'INFO';
  message: string;
  timestamp: string;
  time: string;
}

interface ChromeMonitorError {
  message: string;
  filename?: string;
  lineno?: number;
  colno?: number;
  error?: string;
  stack?: string;
  timestamp: string;
  time: string;
}

interface ChromeMonitorStats {
  totalRequests: number;
  totalLogs: number;
  totalErrors: number;
  uptime: number;
  url: string;
  userAgent: string;
  timestamp: string;
}

interface ChromeMonitorData {
  requests: ChromeMonitorRequest[];
  logs: ChromeMonitorLog[];
  errors: ChromeMonitorError[];
  stats: ChromeMonitorStats;
}

interface ChromeMonitor {
  requests: ChromeMonitorRequest[];
  logs: ChromeMonitorLog[];
  errors: ChromeMonitorError[];
  startTime: number;
  sendTimeout: NodeJS.Timeout | null;
  batchDelay: number;
  lastSentLogsCount: number;
  lastSentErrorsCount: number;
  _addLog?: (type: string, message: string, extra?: Record<string, unknown>) => void;
  _addError?: (errorData: Record<string, unknown>) => void;
  init(): void;
  getStats(): ChromeMonitorData;
  clear(): void;
  export(): void;
  sendToBackend(): Promise<{status: string, result?: Record<string, unknown>, error?: string, reason?: string}>;
  clearMonitor(): void;
  startAutoSend(): void;
  scheduleSend(): void;
}

// Глобальные переменные
declare global {
  interface Window {
    chromeMonitor: ChromeMonitor;
    getMonitorStats: () => ChromeMonitorData;
    clearMonitor: () => void;
    exportMonitor: () => void;
    sendToBackend: () => Promise<{status: string, result?: Record<string, unknown>, error?: string, reason?: string}>;
  }
}
