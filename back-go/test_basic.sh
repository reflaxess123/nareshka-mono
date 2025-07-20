#!/bin/bash

echo "Testing basic server functionality without Go..."

# Test health endpoint with mock response
echo "Health endpoint should return: {'status': 'ok'}"

# Test endpoints that should exist
echo "Available endpoints:"
echo "- GET /health"
echo "- POST /api/v1/auth/register"
echo "- POST /api/v1/auth/login"
echo "- GET /api/v1/auth/me"
echo "- GET /api/v1/users/profile"
echo "- GET /api/v1/tasks/"
echo "- GET /api/v1/content/"

echo "To test manually, install Go and run: go run main.go"