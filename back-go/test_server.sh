#!/bin/bash

echo "Testing Nareshka Go Backend..."

# Test health endpoint
echo "Testing health endpoint..."
curl -X GET http://localhost:8000/health

echo -e "\n\nTesting registration..."
curl -X POST http://localhost:8000/api/v1/auth/register \
  -H "Content-Type: application/json" \
  -d '{
    "username": "testuser",
    "email": "test@example.com", 
    "password": "testpass123"
  }'

echo -e "\n\nTesting login..."
curl -X POST http://localhost:8000/api/v1/auth/login \
  -H "Content-Type: application/json" \
  -d '{
    "login": "testuser",
    "password": "testpass123"
  }'

echo -e "\n\nTesting tasks endpoint..."
curl -X GET http://localhost:8000/api/v1/tasks/

echo -e "\n\nTesting content endpoint..."
curl -X GET http://localhost:8000/api/v1/content/

echo -e "\n\nDone!"