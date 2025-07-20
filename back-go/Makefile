.PHONY: run build test clean deps

# Run the application
run:
	go run main.go

# Build the application
build:
	go build -o bin/nareshka-backend main.go

# Test the application
test:
	go test ./...

# Clean build artifacts
clean:
	rm -rf bin/

# Download dependencies
deps:
	go mod tidy
	go mod download

# Development database setup (requires Docker)
db-up:
	docker run --name nareshka-postgres -e POSTGRES_PASSWORD=postgres -e POSTGRES_DB=nareshka -p 5432:5432 -d postgres:15

# Redis setup (requires Docker)
redis-up:
	docker run --name nareshka-redis -p 6379:6379 -d redis:7-alpine

# Stop development databases
db-down:
	docker stop nareshka-postgres nareshka-redis
	docker rm nareshka-postgres nareshka-redis

# Test API endpoints
test-api:
	./test_server.sh