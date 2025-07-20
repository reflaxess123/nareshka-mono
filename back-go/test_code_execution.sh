#!/bin/bash

echo "Testing Code Execution System..."

# Test supported languages
echo "Testing supported languages..."
curl -X GET http://localhost:8000/api/v1/code/languages

echo -e "\n\nTesting Python code execution..."
curl -X POST http://localhost:8000/api/v1/code/execute \
  -H "Content-Type: application/json" \
  -d '{
    "code": "print(\"Hello, World!\")",
    "language": "python",
    "input": ""
  }'

echo -e "\n\nTesting Python code with input..."
curl -X POST http://localhost:8000/api/v1/code/execute \
  -H "Content-Type: application/json" \
  -d '{
    "code": "name = input(\"Enter name: \")\nprint(f\"Hello, {name}!\")",
    "language": "python",
    "input": "Alice"
  }'

echo -e "\n\nTesting JavaScript code execution..."
curl -X POST http://localhost:8000/api/v1/code/execute \
  -H "Content-Type: application/json" \
  -d '{
    "code": "console.log(\"Hello from JavaScript!\");",
    "language": "javascript",
    "input": ""
  }'

echo -e "\n\nTesting Go code execution..."
curl -X POST http://localhost:8000/api/v1/code/execute \
  -H "Content-Type: application/json" \
  -d '{
    "code": "package main\nimport \"fmt\"\nfunc main() {\n\tfmt.Println(\"Hello from Go!\")\n}",
    "language": "go",
    "input": ""
  }'

echo -e "\n\nTesting error handling..."
curl -X POST http://localhost:8000/api/v1/code/execute \
  -H "Content-Type: application/json" \
  -d '{
    "code": "print(undefined_variable)",
    "language": "python",
    "input": ""
  }'

echo -e "\n\nDone!"