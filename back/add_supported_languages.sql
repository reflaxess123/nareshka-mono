-- Добавляем поддерживаемые языки программирования в базу данных
-- Запустить: psql -d nareshka_dev -f add_supported_languages.sql

INSERT INTO "SupportedLanguage" (
    id, name, language, version, "dockerImage", "fileExtension", 
    "compileCommand", "runCommand", "timeoutSeconds", "memoryLimitMB", 
    "isEnabled", "createdAt", "updatedAt"
) VALUES 
(
    'python3', 'Python 3', 'PYTHON', '3.8.1', 'python:3.8-slim', '.py',
    NULL, 'python {file}', 30, 128, true, NOW(), NOW()
),
(
    'javascript', 'JavaScript (Node.js)', 'JAVASCRIPT', '12.14.0', 'node:12-slim', '.js',
    NULL, 'node {file}', 30, 128, true, NOW(), NOW()
),
(
    'typescript', 'TypeScript', 'TYPESCRIPT', '3.7.4', 'node:12-slim', '.ts',
    'tsc {file} --outDir /tmp', 'node /tmp/{file}.js', 30, 128, true, NOW(), NOW()
),
(
    'java', 'Java', 'JAVA', '13.0.1', 'openjdk:13-slim', '.java',
    'javac {file}', 'java Main', 30, 256, true, NOW(), NOW()
),
(
    'cpp', 'C++', 'CPP', '9.2.0', 'gcc:9', '.cpp',
    'g++ -o main {file}', './main', 30, 128, true, NOW(), NOW()
),
(
    'c', 'C', 'C', '9.2.0', 'gcc:9', '.c',
    'gcc -o main {file}', './main', 30, 128, true, NOW(), NOW()
),
(
    'go', 'Go', 'GO', '1.13.5', 'golang:1.13-alpine', '.go',
    NULL, 'go run {file}', 30, 128, true, NOW(), NOW()
),
(
    'rust', 'Rust', 'RUST', '1.40.0', 'rust:1.40', '.rs',
    'rustc {file} -o main', './main', 30, 128, true, NOW(), NOW()
),
(
    'php', 'PHP', 'PHP', '7.4.1', 'php:7.4-cli', '.php',
    NULL, 'php {file}', 30, 128, true, NOW(), NOW()
),
(
    'ruby', 'Ruby', 'RUBY', '2.7.0', 'ruby:2.7', '.rb',
    NULL, 'ruby {file}', 30, 128, true, NOW(), NOW()
)
ON CONFLICT (id) DO NOTHING;