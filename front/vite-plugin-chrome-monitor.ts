import type { Plugin } from 'vite';

// Скрипт мониторинга Chrome MCP
const chromeMonitorScript = `
console.log('🔍 Chrome MCP Monitor активирован автоматически!');

window.chromeMonitor = {
  requests: [],
  logs: [],
  errors: [],
  startTime: Date.now(),
  
  init() {
    this.interceptFetch();
    this.interceptXHR();
    this.interceptConsole();
    this.interceptErrors();
    console.log('✅ Chrome Monitor запущен автоматически при загрузке страницы');
  },
  
  // Перехват fetch запросов
  interceptFetch() {
    const originalFetch = window.fetch;
    const self = this;
    
    window.fetch = async function(...args) {
      const start = Date.now();
      const url = typeof args[0] === 'string' ? args[0] : args[0]?.url || 'unknown';
      const method = args[1]?.method || 'GET';
      
      console.log('📡 FETCH:', method, url);
      
      try {
        const response = await originalFetch(...args);
        const duration = Date.now() - start;
        
        const requestData = {
          type: 'FETCH',
          url: url,
          method: method,
          status: response.status,
          statusText: response.statusText,
          duration: duration,
          timestamp: new Date().toISOString(),
          time: new Date().toLocaleTimeString()
        };
        
        self.requests.push(requestData);
        console.log('✅ FETCH SUCCESS:', response.status, url, duration + 'ms');
        
        return response;
      } catch (error) {
        const requestData = {
          type: 'FETCH',
          url: url,
          method: method,
          status: 'ERROR',
          error: error.message,
          duration: Date.now() - start,
          timestamp: new Date().toISOString(),
          time: new Date().toLocaleTimeString()
        };
        
        self.requests.push(requestData);
        console.error('❌ FETCH ERROR:', error, url);
        throw error;
      }
    };
  },
  
  // Перехват XHR запросов
  interceptXHR() {
    const originalXHR = window.XMLHttpRequest;
    const self = this;
    
    window.XMLHttpRequest = function() {
      const xhr = new originalXHR();
      const start = Date.now();
      let method = 'GET';
      let url = '';
      
      const originalOpen = xhr.open;
      xhr.open = function(m, u, ...args) {
        method = m;
        url = u;
        console.log('📡 XHR OPEN:', method, url);
        return originalOpen.call(this, m, u, ...args);
      };
      
      xhr.addEventListener('readystatechange', function() {
        if (this.readyState === 4) {
          const duration = Date.now() - start;
          const requestData = {
            type: 'XHR',
            url: url,
            method: method,
            status: this.status,
            statusText: this.statusText,
            duration: duration,
            timestamp: new Date().toISOString(),
            time: new Date().toLocaleTimeString()
          };
          
          self.requests.push(requestData);
          
          if (this.status >= 200 && this.status < 300) {
            console.log('✅ XHR SUCCESS:', this.status, url, duration + 'ms');
          } else {
            console.warn('⚠️ XHR WARNING:', this.status, url, duration + 'ms');
          }
        }
      });
      
      return xhr;
    };
  },
  
  // Перехват консольных логов
  interceptConsole() {
    const originalLog = console.log;
    const originalError = console.error;
    const originalWarn = console.warn;
    const originalInfo = console.info;
    const self = this;
    
    console.log = function(...args) {
      if (!args[0]?.toString().includes('Chrome Monitor')) {
        self.logs.push({
          type: 'LOG',
          message: args.map(a => String(a)).join(' '),
          timestamp: new Date().toISOString(),
          time: new Date().toLocaleTimeString()
        });
      }
      return originalLog.apply(console, args);
    };
    
    console.error = function(...args) {
      self.logs.push({
        type: 'ERROR',
        message: args.map(a => String(a)).join(' '),
        timestamp: new Date().toISOString(),
        time: new Date().toLocaleTimeString()
      });
      self.errors.push({
        message: args.map(a => String(a)).join(' '),
        timestamp: new Date().toISOString(),
        time: new Date().toLocaleTimeString(),
        stack: new Error().stack
      });
      return originalError.apply(console, args);
    };
    
    console.warn = function(...args) {
      self.logs.push({
        type: 'WARN',
        message: args.map(a => String(a)).join(' '),
        timestamp: new Date().toISOString(),
        time: new Date().toLocaleTimeString()
      });
      return originalWarn.apply(console, args);
    };
    
    console.info = function(...args) {
      self.logs.push({
        type: 'INFO',
        message: args.map(a => String(a)).join(' '),
        timestamp: new Date().toISOString(),
        time: new Date().toLocaleTimeString()
      });
      return originalInfo.apply(console, args);
    };
  },
  
  // Перехват JS ошибок
  interceptErrors() {
    const self = this;
    
    window.addEventListener('error', function(event) {
      self.errors.push({
        message: event.message,
        filename: event.filename,
        lineno: event.lineno,
        colno: event.colno,
        error: event.error?.stack || event.error,
        timestamp: new Date().toISOString(),
        time: new Date().toLocaleTimeString()
      });
      console.error('🚨 JS ERROR:', event.message, event.filename + ':' + event.lineno);
    });
    
    window.addEventListener('unhandledrejection', function(event) {
      self.errors.push({
        message: 'Unhandled Promise Rejection: ' + event.reason,
        timestamp: new Date().toISOString(),
        time: new Date().toLocaleTimeString(),
        stack: event.reason?.stack || String(event.reason)
      });
      console.error('🚨 UNHANDLED PROMISE REJECTION:', event.reason);
    });
  },
  
  // Получение статистики
  getStats() {
    return {
      requests: this.requests,
      logs: this.logs,
      errors: this.errors,
      stats: {
        totalRequests: this.requests.length,
        totalLogs: this.logs.length,
        totalErrors: this.errors.length,
        uptime: Date.now() - this.startTime,
        url: window.location.href,
        userAgent: navigator.userAgent,
        timestamp: new Date().toISOString()
      }
    };
  },
  
  // Очистка данных
  clear() {
    this.requests = [];
    this.logs = [];
    this.errors = [];
    console.log('🧹 Chrome Monitor данные очищены');
  },
  
  // Экспорт данных
  export() {
    const data = this.getStats();
    const blob = new Blob([JSON.stringify(data, null, 2)], { type: 'application/json' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = 'chrome-monitor-' + Date.now() + '.json';
    a.click();
    URL.revokeObjectURL(url);
    console.log('💾 Chrome Monitor данные экспортированы');
  }
};

// Автоматический запуск при загрузке страницы
if (document.readyState === 'loading') {
  document.addEventListener('DOMContentLoaded', () => window.chromeMonitor.init());
} else {
  window.chromeMonitor.init();
}

// Глобальные команды для удобства
window.getMonitorStats = () => window.chromeMonitor.getStats();
window.clearMonitor = () => window.chromeMonitor.clear();
window.exportMonitor = () => window.chromeMonitor.export();

console.log('🎯 Chrome MCP Monitor готов! Команды: getMonitorStats(), clearMonitor(), exportMonitor()');
`;

export function chromeMonitorPlugin(): Plugin {
  return {
    name: 'chrome-monitor',
    transformIndexHtml(html) {
      // Инжектируем скрипт в head страницы
      return html.replace(
        '<head>',
        `<head>
  <script>
    ${chromeMonitorScript}
  </script>`
      );
    },
    configureServer(server) {
      console.log('🔍 Chrome MCP Monitor Plugin активирован в dev режиме');
      
      // Логируем когда сервер готов
      server.middlewares.use((req, res, next) => {
        if (req.url === '/' || req.url?.startsWith('/?')) {
          console.log('📄 Страница загружена, Chrome Monitor автоматически инжектирован');
        }
        next();
      });
    }
  };
}