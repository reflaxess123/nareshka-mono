#!/usr/bin/env node

/**
 * Скрипт для исправления генерируемого Orval кода для совместимости с React Query v5
 * 
 * Использование: node fix-orval-v5.js
 * 
 * Исправления:
 * 1. Убирает второй параметр queryClient из useQuery() - это v4 синтаксис
 * 2. Убирает параметр queryClient из сигнатур функций где он не нужен
 */

import fs from 'fs';
import path from 'path';
import { fileURLToPath } from 'url';

const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);

const API_FILE_PATH = path.join(__dirname, 'src/shared/api/generated/api.ts');

function fixOrvalV5Compatibility() {
  console.log('🔧 Исправляем совместимость Orval с React Query v5...');
  
  if (!fs.existsSync(API_FILE_PATH)) {
    console.error('❌ API файл не найден:', API_FILE_PATH);
    return;
  }

  let content = fs.readFileSync(API_FILE_PATH, 'utf8');
  let changed = false;

  // Исправление 1: убираем второй параметр queryClient из useQuery вызовов
  const oldUseQueryPattern = /const query = useQuery\(queryOptions\s*,\s*queryClient\)/g;
  if (content.match(oldUseQueryPattern)) {
    content = content.replace(oldUseQueryPattern, 'const query = useQuery(queryOptions)');
    console.log('✅ Исправлены useQuery вызовы');
    changed = true;
  }

  // Исправление 2: убираем опциональный параметр queryClient из сигнатур функций
  const queryClientParamPattern = /\s*,\s*queryClient\?\:\s*QueryClient/g;
  if (content.match(queryClientParamPattern)) {
    content = content.replace(queryClientParamPattern, '');
    console.log('✅ Убраны параметры queryClient из функций');
    changed = true;
  }

  if (changed) {
    fs.writeFileSync(API_FILE_PATH, content, 'utf8');
    console.log('✅ API файл исправлен для React Query v5');
  } else {
    console.log('ℹ️ Исправления не требуются');
  }
}

// Запускаем исправления
fixOrvalV5Compatibility();