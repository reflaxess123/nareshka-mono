import type { Plugin } from 'vite';

// Скрипт мониторинга Chrome MCP
const chromeMonitorScript = `
console.log('🔍 Chrome MCP Monitor активирован автоматически!');

window.chromeMonitor = {
  requests: [],
  logs: [],
  errors: [],
  startTime: Date.now(),
  sendTimeout: null,
  batchDelay: 2000, // 2 секунды для батчинга
  lastSentLogsCount: 0,
  lastSentErrorsCount: 0,
  
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
        if (self._addLog) {
          self._addLog('LOG', args.map(a => String(a)).join(' '));
        } else {
          self.logs.push({
            type: 'LOG',
            message: args.map(a => String(a)).join(' '),
            timestamp: new Date().toISOString(),
            time: new Date().toLocaleTimeString()
          });
        }
      }
      return originalLog.apply(console, args);
    };
    
    console.error = function(...args) {
      const errorMsg = args.map(a => String(a)).join(' ');
      
      if (self._addLog) {
        self._addLog('ERROR', errorMsg);
      } else {
        self.logs.push({
          type: 'ERROR',
          message: errorMsg,
          timestamp: new Date().toISOString(),
          time: new Date().toLocaleTimeString()
        });
      }
      
      if (self._addError) {
        self._addError({
          message: errorMsg,
          stack: new Error().stack
        });
      } else {
        self.errors.push({
          message: errorMsg,
          timestamp: new Date().toISOString(),
          time: new Date().toLocaleTimeString(),
          stack: new Error().stack
        });
      }
      
      return originalError.apply(console, args);
    };
    
    console.warn = function(...args) {
      const warnMsg = args.map(a => String(a)).join(' ');
      
      if (self._addLog) {
        self._addLog('WARN', warnMsg);
      } else {
        self.logs.push({
          type: 'WARN',
          message: warnMsg,
          timestamp: new Date().toISOString(),
          time: new Date().toLocaleTimeString()
        });
      }
      return originalWarn.apply(console, args);
    };
    
    console.info = function(...args) {
      const infoMsg = args.map(a => String(a)).join(' ');
      
      if (self._addLog) {
        self._addLog('INFO', infoMsg);
      } else {
        self.logs.push({
          type: 'INFO',
          message: infoMsg,
          timestamp: new Date().toISOString(),
          time: new Date().toLocaleTimeString()
        });
      }
      return originalInfo.apply(console, args);
    };
  },
  
  // Перехват JS ошибок
  interceptErrors() {
    const self = this;
    
    window.addEventListener('error', function(event) {
      const errorData = {
        message: event.message,
        filename: event.filename,
        lineno: event.lineno,
        colno: event.colno,
        error: event.error?.stack || event.error
      };
      
      if (self._addError) {
        self._addError(errorData);
      } else {
        self.errors.push({
          ...errorData,
          timestamp: new Date().toISOString(),
          time: new Date().toLocaleTimeString()
        });
      }
      
      console.error('🚨 JS ERROR:', event.message, event.filename + ':' + event.lineno);
    });
    
    window.addEventListener('unhandledrejection', function(event) {
      const errorData = {
        message: 'Unhandled Promise Rejection: ' + event.reason,
        stack: event.reason?.stack || String(event.reason)
      };
      
      if (self._addError) {
        self._addError(errorData);
      } else {
        self.errors.push({
          ...errorData,
          timestamp: new Date().toISOString(),
          time: new Date().toLocaleTimeString()
        });
      }
      
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
  
  // Полная очистка данных
  clear() {
    this.requests = [];
    this.logs = [];
    this.errors = [];
    console.log('🧹 Chrome Monitor данные полностью очищены');
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
  },
  
  // Отправка логов в backend
  async sendToBackend() {
    // Проверяем есть ли новые логи или ошибки с момента последней отправки
    const hasNewLogs = this.logs.length > this.lastSentLogsCount;
    const hasNewErrors = this.errors.length > this.lastSentErrorsCount;
    
    if (!hasNewLogs && !hasNewErrors) {
      // Нет новых данных для отправки
      return { status: 'skipped', reason: 'no_new_data' };
    }
    
    const logsToSend = [];
    
    // Конвертируем console логи
    this.logs.forEach(log => {
      logsToSend.push({
        level: log.type === 'LOG' ? 'INFO' : log.type,
        message: log.message,
        source: 'chrome_frontend',
        timestamp: log.timestamp,
        url: window.location.href,
        metadata: { originalType: log.type }
      });
    });
    
    // Конвертируем ошибки
    this.errors.forEach(error => {
      logsToSend.push({
        level: 'ERROR',
        message: error.message,
        source: 'chrome_frontend',
        timestamp: error.timestamp,
        url: window.location.href,
        metadata: {
          filename: error.filename,
          lineno: error.lineno,
          colno: error.colno,
          stack: error.stack
        }
      });
    });
    
    try {
      const response = await fetch('/api/logs/external', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          logs: logsToSend,
          source_info: {
            name: 'Chrome Monitor',
            version: '1.0',
            url: window.location.href,
            userAgent: navigator.userAgent.slice(0, 200)
          }
        })
      });
      
      if (response.ok) {
        const result = await response.json();
        console.log('✅ Логи отправлены в backend:', result);
        
        // Очищаем отправленные логи
        this.clearMonitor();
        
        // Сбрасываем счетчики после очистки
        this.lastSentLogsCount = 0;
        this.lastSentErrorsCount = 0;
        
        return { status: 'success', result };
      } else {
        console.error('❌ Ошибка отправки логов:', response.status, response.statusText);
        return { status: 'error', error: response.statusText };
      }
    } catch (error) {
      console.error('❌ Сетевая ошибка при отправке логов:', error);
      return { status: 'error', error: error.message };
    }
  },
  
  // Очистка только логов (для автоотправки)
  clearMonitor() {
    this.logs = [];
    this.errors = [];
    // Не логируем очистку, чтобы избежать бесконечного цикла
    // console.log('🧹 Chrome Monitor логи очищены после отправки');
  },
  
  // Планирование отправки логов (с батчингом)
  scheduleSend() {
    if (this.sendTimeout) {
      clearTimeout(this.sendTimeout);
    }
    
    this.sendTimeout = setTimeout(async () => {
      try {
        const result = await this.sendToBackend();
        // Не логируем успешную отправку, чтобы избежать бесконечного цикла
        // console.log('📤 Логи отправлены автоматически');
      } catch (error) {
        console.error('❌ Ошибка автоотправки логов:', error);
      }
    }, this.batchDelay);
  },
  
  // Мгновенная отправка + автоматическое планирование
  startAutoSend() {
    console.log('⚡ Мгновенная отправка логов активирована (батчинг 2 сек)');
    
    // Переопределяем методы добавления логов для автоотправки
    const originalAddLog = (type, message, extra = {}) => {
      this.logs.push({
        type: type,
        message: message,
        timestamp: new Date().toISOString(),
        time: new Date().toLocaleTimeString(),
        ...extra
      });
      
      // Планируем отправку при каждом новом логе
      this.scheduleSend();
    };
    
    // Хелпер для добавления ошибок
    const originalAddError = (errorData) => {
      this.errors.push({
        ...errorData,
        timestamp: new Date().toISOString(),
        time: new Date().toLocaleTimeString()
      });
      
      // Планируем отправку при каждой новой ошибке
      this.scheduleSend();
    };
    
    // Сохраняем ссылки для использования в перехватчиках
    this._addLog = originalAddLog;
    this._addError = originalAddError;
  }
};

// Автоматический запуск при загрузке страницы
if (document.readyState === 'loading') {
  document.addEventListener('DOMContentLoaded', () => {
    window.chromeMonitor.init();
    window.chromeMonitor.startAutoSend();
  });
} else {
  window.chromeMonitor.init();
  window.chromeMonitor.startAutoSend();
}

// Глобальные команды для удобства
window.getMonitorStats = () => window.chromeMonitor.getStats();
window.clearMonitor = () => window.chromeMonitor.clear();
window.exportMonitor = () => window.chromeMonitor.export();
window.sendToBackend = () => window.chromeMonitor.sendToBackend();

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