package api

import (
	"net/http"
	"nareshka-backend/app/config"
	"nareshka-backend/app/features/code_editor/dto"
	"nareshka-backend/app/features/code_editor/services"

	"github.com/gin-gonic/gin"
	"github.com/redis/go-redis/v9"
	"gorm.io/gorm"
)

type CodeEditorHandler struct {
	service *services.CodeEditorService
}

func NewCodeEditorHandler(db *gorm.DB, redis *redis.Client, cfg *config.Config) *CodeEditorHandler {
	service := services.NewCodeEditorService(db)
	return &CodeEditorHandler{
		service: service,
	}
}

func (h *CodeEditorHandler) ExecuteCode(c *gin.Context) {
	var req dto.ExecuteCodeRequest
	if err := c.ShouldBindJSON(&req); err != nil {
		c.JSON(http.StatusBadRequest, gin.H{"error": err.Error()})
		return
	}

	result, err := h.service.ExecuteCode(&req)
	if err != nil {
		c.JSON(http.StatusInternalServerError, gin.H{"error": err.Error()})
		return
	}

	c.JSON(http.StatusOK, result)
}

func (h *CodeEditorHandler) ValidateTask(c *gin.Context) {
	userID, exists := c.Get("user_id")
	if !exists {
		c.JSON(http.StatusUnauthorized, gin.H{"error": "User not authenticated"})
		return
	}

	var req dto.ValidateTaskRequest
	if err := c.ShouldBindJSON(&req); err != nil {
		c.JSON(http.StatusBadRequest, gin.H{"error": err.Error()})
		return
	}

	result, err := h.service.ValidateTask(userID.(uint), &req)
	if err != nil {
		c.JSON(http.StatusBadRequest, gin.H{"error": err.Error()})
		return
	}

	c.JSON(http.StatusOK, result)
}

func (h *CodeEditorHandler) GetSupportedLanguages(c *gin.Context) {
	languages := h.service.GetSupportedLanguages()
	c.JSON(http.StatusOK, gin.H{"languages": languages})
}

func (h *CodeEditorHandler) GetTaskAttempts(c *gin.Context) {
	_, exists := c.Get("user_id")
	if !exists {
		c.JSON(http.StatusUnauthorized, gin.H{"error": "User not authenticated"})
		return
	}

	// TODO: Implement GetTaskAttempts in service
	c.JSON(http.StatusOK, gin.H{"message": "Task attempts - coming soon"})
}