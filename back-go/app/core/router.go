package core

import (
	"nareshka-backend/app/config"
	authApi "nareshka-backend/app/features/auth/api"
	codeEditorApi "nareshka-backend/app/features/code_editor/api"
	contentApi "nareshka-backend/app/features/content/api"
	progressApi "nareshka-backend/app/features/progress/api"
	taskApi "nareshka-backend/app/features/task/api"
	"nareshka-backend/app/shared/middleware"

	"github.com/gin-gonic/gin"
	"github.com/redis/go-redis/v9"
	"gorm.io/gorm"
)

func SetupRoutes(r *gin.Engine, db *gorm.DB, redis *redis.Client, cfg *config.Config) {
	// Health check
	r.GET("/health", func(c *gin.Context) {
		c.JSON(200, gin.H{
			"status": "ok",
			"timestamp": "2025-01-01T00:00:00Z",
		})
	})

	// API v1 routes
	api := r.Group("/api/v1")
	{
		// Initialize middleware
		authMiddleware := middleware.NewAuthMiddleware(db, cfg)

		// Initialize handlers
		authHandler := authApi.NewAuthHandler(db, redis, cfg)
		codeEditorHandler := codeEditorApi.NewCodeEditorHandler(db, redis, cfg)
		contentHandler := contentApi.NewContentHandler(db, redis, cfg)
		progressHandler := progressApi.NewProgressHandler(db, redis, cfg)
		taskHandler := taskApi.NewTaskHandler(db, redis, cfg)

		// Auth routes
		auth := api.Group("/auth")
		{
			auth.POST("/register", authHandler.Register)
			auth.POST("/login", authHandler.Login)
			auth.POST("/logout", authHandler.Logout)
			auth.GET("/me", authHandler.GetCurrentUser)
		}

		// Code execution routes
		code := api.Group("/code")
		{
			code.POST("/execute", codeEditorHandler.ExecuteCode)
			code.POST("/validate", authMiddleware.RequireAuth(), codeEditorHandler.ValidateTask)
			code.GET("/languages", codeEditorHandler.GetSupportedLanguages)
			code.GET("/attempts", authMiddleware.RequireAuth(), codeEditorHandler.GetTaskAttempts)
		}

		// Task routes
		tasks := api.Group("/tasks")
		{
			// Public routes
			tasks.GET("/", authMiddleware.OptionalAuth(), taskHandler.GetTasks)
			tasks.GET("/:id", authMiddleware.OptionalAuth(), taskHandler.GetTask)

			// Protected routes
			tasks.POST("/", authMiddleware.RequireAuth(), taskHandler.CreateTask)
			tasks.PUT("/:id", authMiddleware.RequireAuth(), taskHandler.UpdateTask)
			tasks.DELETE("/:id", authMiddleware.RequireAuth(), taskHandler.DeleteTask)
			tasks.POST("/test-cases", authMiddleware.RequireAuth(), taskHandler.CreateTestCase)
		}

		// Content routes
		content := api.Group("/content")
		{
			// Content blocks
			content.GET("/blocks", authMiddleware.OptionalAuth(), contentHandler.GetContentBlocks)
			content.GET("/blocks/:id", authMiddleware.OptionalAuth(), contentHandler.GetContentBlock)
			content.PATCH("/blocks/:id/progress", authMiddleware.RequireAuth(), contentHandler.UpdateProgress)

			// Content files
			content.GET("/files", contentHandler.GetContentFiles)
			
			// Categories
			content.GET("/categories", contentHandler.GetCategories)

			// Theory cards
			content.POST("/theory", authMiddleware.RequireAuth(), contentHandler.CreateTheoryCard)
			content.GET("/theory", authMiddleware.OptionalAuth(), contentHandler.GetTheoryCards)
			content.GET("/theory/:id", authMiddleware.OptionalAuth(), contentHandler.GetTheoryCard)
			content.PUT("/theory/:id", authMiddleware.RequireAuth(), contentHandler.UpdateTheoryCard)
			content.DELETE("/theory/:id", authMiddleware.RequireAuth(), contentHandler.DeleteTheoryCard)
			content.POST("/theory/:id/review", authMiddleware.RequireAuth(), contentHandler.ReviewTheoryCard)
			content.GET("/theory/review", authMiddleware.RequireAuth(), contentHandler.GetCardsForReview)
		}

		// Progress routes
		progress := api.Group("/progress")
		{
			progress.POST("/activity", authMiddleware.RequireAuth(), progressHandler.RecordActivity)
			progress.GET("/activities", authMiddleware.RequireAuth(), progressHandler.GetUserActivities)
			progress.GET("/summary", authMiddleware.RequireAuth(), progressHandler.GetProgressSummary)
			progress.POST("/category", authMiddleware.RequireAuth(), progressHandler.UpdateCategoryProgress)
			progress.POST("/path", authMiddleware.RequireAuth(), progressHandler.UpdatePathProgress)
		}

		// Placeholder routes
		api.GET("/users/profile", func(c *gin.Context) {
			c.JSON(200, gin.H{"message": "User profile - coming soon"})
		})
	}
}