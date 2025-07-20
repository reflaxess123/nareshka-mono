package app

import (
	"context"
	"fmt"
	"log"
	"net/http"
	"os"
	"os/signal"
	"syscall"
	"time"

	"nareshka-backend/app/config"
	"nareshka-backend/app/shared/database"
	"nareshka-backend/app/core"

	"github.com/gin-gonic/gin"
	"github.com/redis/go-redis/v9"
	"gorm.io/gorm"
)

type App struct {
	config   *config.Config
	db       *gorm.DB
	redis    *redis.Client
	router   *gin.Engine
	server   *http.Server
}

func NewApp() (*App, error) {
	// Load configuration
	cfg, err := config.Load()
	if err != nil {
		return nil, fmt.Errorf("failed to load config: %w", err)
	}

	// Initialize database
	db, err := database.NewDatabase(cfg)
	if err != nil {
		return nil, fmt.Errorf("failed to initialize database: %w", err)
	}

	// Initialize Redis
	redis, err := database.NewRedis(cfg)
	if err != nil {
		return nil, fmt.Errorf("failed to initialize Redis: %w", err)
	}

	// Set Gin mode
	if cfg.Server.Env == "production" {
		gin.SetMode(gin.ReleaseMode)
	}

	// Initialize router
	router := gin.Default()

	// Setup API routes
	core.SetupRoutes(router, db, redis, cfg)

	// Create HTTP server
	server := &http.Server{
		Addr:    fmt.Sprintf("%s:%s", cfg.Server.Host, cfg.Server.Port),
		Handler: router,
	}

	return &App{
		config: cfg,
		db:     db,
		redis:  redis,
		router: router,
		server: server,
	}, nil
}

func (a *App) Run() error {
	// Start server in a goroutine
	go func() {
		log.Printf("Server starting on %s:%s", a.config.Server.Host, a.config.Server.Port)
		if err := a.server.ListenAndServe(); err != nil && err != http.ErrServerClosed {
			log.Fatalf("Failed to start server: %v", err)
		}
	}()

	// Wait for interrupt signal to gracefully shutdown
	quit := make(chan os.Signal, 1)
	signal.Notify(quit, syscall.SIGINT, syscall.SIGTERM)
	<-quit

	log.Println("Shutting down server...")

	// Graceful shutdown with timeout
	ctx, cancel := context.WithTimeout(context.Background(), 10*time.Second)
	defer cancel()

	if err := a.server.Shutdown(ctx); err != nil {
		return fmt.Errorf("server forced to shutdown: %w", err)
	}

	// Close database connection
	if sqlDB, err := a.db.DB(); err == nil {
		sqlDB.Close()
	}

	// Close Redis connection
	a.redis.Close()

	log.Println("Server gracefully stopped")
	return nil
}