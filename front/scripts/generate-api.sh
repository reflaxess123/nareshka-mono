#!/bin/bash

# Скрипт для генерации API типов и хуков из OpenAPI спецификации
# Использование: ./scripts/generate-api.sh [--force]

set -e

# Цвета для вывода
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Функция для логирования
log() {
    echo -e "${GREEN}[API Generator]${NC} $1"
}

warn() {
    echo -e "${YELLOW}[API Generator]${NC} $1"
}

error() {
    echo -e "${RED}[API Generator]${NC} $1"
}

# Проверка доступности бекенда
check_backend() {
    log "Проверка доступности бекенда..."
    
    local max_attempts=30
    local attempt=1
    
    while [ $attempt -le $max_attempts ]; do
        if curl -s http://localhost:4000/openapi.json > /dev/null 2>&1; then
            log "Бекенд доступен ✅"
            return 0
        fi
        
        warn "Попытка $attempt/$max_attempts: бекенд недоступен, ожидание..."
        sleep 2
        ((attempt++))
    done
    
    error "Бекенд недоступен после $max_attempts попыток"
    error "Убедитесь что бекенд запущен на http://localhost:4000"
    exit 1
}

# Функция генерации API
generate_api() {
    log "Генерация API типов и хуков..."
    
    # Запускаем orval
    if npx orval --config orval.config.ts; then
        log "API успешно сгенерирован ✅"
        
        # Показываем статистику
        local generated_file="src/shared/api/generated/api.ts"
        if [ -f "$generated_file" ]; then
            local lines=$(wc -l < "$generated_file")
            local hooks=$(grep -c "export.*use.*" "$generated_file" || echo "0")
            local types=$(grep -c "export.*Type" "$generated_file" || echo "0")
            
            echo -e "${BLUE}📊 Статистика генерации:${NC}"
            echo -e "   • Строк кода: $lines"
            echo -e "   • React Query хуков: $hooks"
            echo -e "   • TypeScript типов: $types"
        fi
    else
        error "Ошибка генерации API"
        exit 1
    fi
}

# Основная функция
main() {
    log "Запуск генерации API..."
    
    # Проверяем наличие orval
    if ! command -v npx &> /dev/null; then
        error "npx не найден. Установите Node.js"
        exit 1
    fi
    
    # Проверяем что мы в правильной директории
    if [ ! -f "orval.config.ts" ]; then
        error "Файл orval.config.ts не найден"
        error "Запустите скрипт из корневой директории фронтенда"
        exit 1
    fi
    
    # Проверяем доступность бекенда
    check_backend
    
    # Генерируем API
    generate_api
    
    log "Генерация завершена успешно! 🎉"
}

# Запуск
main "$@" 