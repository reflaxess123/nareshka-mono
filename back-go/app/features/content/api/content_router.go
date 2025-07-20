package api

import (
	"net/http"
	"strconv"
	"nareshka-backend/app/config"
	"nareshka-backend/app/features/content/dto"
	"nareshka-backend/app/features/content/services"

	"github.com/gin-gonic/gin"
	"github.com/redis/go-redis/v9"
	"gorm.io/gorm"
)

type ContentHandler struct {
	contentService *services.ContentService
	theoryService  *services.TheoryService
}

func NewContentHandler(db *gorm.DB, redis *redis.Client, cfg *config.Config) *ContentHandler {
	return &ContentHandler{
		contentService: services.NewContentService(db),
		theoryService:  services.NewTheoryService(db),
	}
}

// Content Blocks
func (h *ContentHandler) GetContentBlocks(c *gin.Context) {
	var req dto.ContentBlockFilterRequest
	if err := c.ShouldBindQuery(&req); err != nil {
		c.JSON(http.StatusBadRequest, gin.H{"error": err.Error()})
		return
	}

	// Set defaults
	if req.Page <= 0 {
		req.Page = 1
	}
	if req.Limit <= 0 || req.Limit > 100 {
		req.Limit = 20
	}

	var userID *uint
	if uid, exists := c.Get("user_id"); exists {
		userId := uid.(uint)
		userID = &userId
	}

	response, err := h.contentService.GetContentBlocks(&req, userID)
	if err != nil {
		c.JSON(http.StatusInternalServerError, gin.H{"error": err.Error()})
		return
	}

	c.JSON(http.StatusOK, response)
}

func (h *ContentHandler) GetContentBlock(c *gin.Context) {
	id := c.Param("id")
	if id == "" {
		c.JSON(http.StatusBadRequest, gin.H{"error": "Block ID is required"})
		return
	}

	var userID *uint
	if uid, exists := c.Get("user_id"); exists {
		userId := uid.(uint)
		userID = &userId
	}

	response, err := h.contentService.GetContentBlock(id, userID)
	if err != nil {
		if err.Error() == "content block not found" {
			c.JSON(http.StatusNotFound, gin.H{"error": err.Error()})
		} else {
			c.JSON(http.StatusInternalServerError, gin.H{"error": err.Error()})
		}
		return
	}

	c.JSON(http.StatusOK, response)
}

func (h *ContentHandler) UpdateProgress(c *gin.Context) {
	userID, exists := c.Get("user_id")
	if !exists {
		c.JSON(http.StatusUnauthorized, gin.H{"error": "User not authenticated"})
		return
	}

	blockID := c.Param("id")
	if blockID == "" {
		c.JSON(http.StatusBadRequest, gin.H{"error": "Block ID is required"})
		return
	}

	var req dto.UpdateProgressRequest
	if err := c.ShouldBindJSON(&req); err != nil {
		c.JSON(http.StatusBadRequest, gin.H{"error": err.Error()})
		return
	}

	response, err := h.contentService.UpdateProgress(blockID, userID.(uint), req.Increment)
	if err != nil {
		if err.Error() == "content block not found" {
			c.JSON(http.StatusNotFound, gin.H{"error": err.Error()})
		} else {
			c.JSON(http.StatusInternalServerError, gin.H{"error": err.Error()})
		}
		return
	}

	c.JSON(http.StatusOK, response)
}

// Content Files
func (h *ContentHandler) GetContentFiles(c *gin.Context) {
	var req dto.ContentFileFilterRequest
	if err := c.ShouldBindQuery(&req); err != nil {
		c.JSON(http.StatusBadRequest, gin.H{"error": err.Error()})
		return
	}

	// Set defaults
	if req.Page <= 0 {
		req.Page = 1
	}
	if req.Limit <= 0 || req.Limit > 100 {
		req.Limit = 20
	}

	response, err := h.contentService.GetContentFiles(&req)
	if err != nil {
		c.JSON(http.StatusInternalServerError, gin.H{"error": err.Error()})
		return
	}

	c.JSON(http.StatusOK, response)
}

// Categories
func (h *ContentHandler) GetCategories(c *gin.Context) {
	response, err := h.contentService.GetCategories()
	if err != nil {
		c.JSON(http.StatusInternalServerError, gin.H{"error": err.Error()})
		return
	}

	c.JSON(http.StatusOK, response)
}

// Theory Cards
func (h *ContentHandler) CreateTheoryCard(c *gin.Context) {
	userID, exists := c.Get("user_id")
	if !exists {
		c.JSON(http.StatusUnauthorized, gin.H{"error": "User not authenticated"})
		return
	}

	var req dto.CreateTheoryCardRequest
	if err := c.ShouldBindJSON(&req); err != nil {
		c.JSON(http.StatusBadRequest, gin.H{"error": err.Error()})
		return
	}

	response, err := h.theoryService.CreateTheoryCard(userID.(uint), &req)
	if err != nil {
		c.JSON(http.StatusInternalServerError, gin.H{"error": err.Error()})
		return
	}

	c.JSON(http.StatusCreated, response)
}

func (h *ContentHandler) GetTheoryCard(c *gin.Context) {
	idStr := c.Param("id")
	id, err := strconv.ParseUint(idStr, 10, 32)
	if err != nil {
		c.JSON(http.StatusBadRequest, gin.H{"error": "Invalid theory card ID"})
		return
	}

	var userID *uint
	if uid, exists := c.Get("user_id"); exists {
		userId := uid.(uint)
		userID = &userId
	}

	response, err := h.theoryService.GetTheoryCard(uint(id), userID)
	if err != nil {
		if err.Error() == "theory card not found" {
			c.JSON(http.StatusNotFound, gin.H{"error": err.Error()})
		} else {
			c.JSON(http.StatusInternalServerError, gin.H{"error": err.Error()})
		}
		return
	}

	c.JSON(http.StatusOK, response)
}

func (h *ContentHandler) GetTheoryCards(c *gin.Context) {
	var req dto.TheoryCardFilterRequest
	if err := c.ShouldBindQuery(&req); err != nil {
		c.JSON(http.StatusBadRequest, gin.H{"error": err.Error()})
		return
	}

	// Set defaults
	if req.Page <= 0 {
		req.Page = 1
	}
	if req.Limit <= 0 || req.Limit > 100 {
		req.Limit = 20
	}

	var userID *uint
	if uid, exists := c.Get("user_id"); exists {
		userId := uid.(uint)
		userID = &userId
	}

	response, err := h.theoryService.GetTheoryCards(&req, userID)
	if err != nil {
		c.JSON(http.StatusInternalServerError, gin.H{"error": err.Error()})
		return
	}

	c.JSON(http.StatusOK, response)
}

func (h *ContentHandler) UpdateTheoryCard(c *gin.Context) {
	userID, exists := c.Get("user_id")
	if !exists {
		c.JSON(http.StatusUnauthorized, gin.H{"error": "User not authenticated"})
		return
	}

	idStr := c.Param("id")
	id, err := strconv.ParseUint(idStr, 10, 32)
	if err != nil {
		c.JSON(http.StatusBadRequest, gin.H{"error": "Invalid theory card ID"})
		return
	}

	var req dto.UpdateTheoryCardRequest
	if err := c.ShouldBindJSON(&req); err != nil {
		c.JSON(http.StatusBadRequest, gin.H{"error": err.Error()})
		return
	}

	response, err := h.theoryService.UpdateTheoryCard(uint(id), userID.(uint), &req)
	if err != nil {
		if err.Error() == "permission denied" {
			c.JSON(http.StatusForbidden, gin.H{"error": err.Error()})
		} else if err.Error() == "theory card not found" {
			c.JSON(http.StatusNotFound, gin.H{"error": err.Error()})
		} else {
			c.JSON(http.StatusInternalServerError, gin.H{"error": err.Error()})
		}
		return
	}

	c.JSON(http.StatusOK, response)
}

func (h *ContentHandler) DeleteTheoryCard(c *gin.Context) {
	userID, exists := c.Get("user_id")
	if !exists {
		c.JSON(http.StatusUnauthorized, gin.H{"error": "User not authenticated"})
		return
	}

	idStr := c.Param("id")
	id, err := strconv.ParseUint(idStr, 10, 32)
	if err != nil {
		c.JSON(http.StatusBadRequest, gin.H{"error": "Invalid theory card ID"})
		return
	}

	err = h.theoryService.DeleteTheoryCard(uint(id), userID.(uint))
	if err != nil {
		if err.Error() == "permission denied" {
			c.JSON(http.StatusForbidden, gin.H{"error": err.Error()})
		} else if err.Error() == "theory card not found" {
			c.JSON(http.StatusNotFound, gin.H{"error": err.Error()})
		} else {
			c.JSON(http.StatusInternalServerError, gin.H{"error": err.Error()})
		}
		return
	}

	c.JSON(http.StatusOK, gin.H{"message": "Theory card deleted successfully"})
}

func (h *ContentHandler) ReviewTheoryCard(c *gin.Context) {
	userID, exists := c.Get("user_id")
	if !exists {
		c.JSON(http.StatusUnauthorized, gin.H{"error": "User not authenticated"})
		return
	}

	idStr := c.Param("id")
	id, err := strconv.ParseUint(idStr, 10, 32)
	if err != nil {
		c.JSON(http.StatusBadRequest, gin.H{"error": "Invalid theory card ID"})
		return
	}

	var req dto.ReviewTheoryCardRequest
	if err := c.ShouldBindJSON(&req); err != nil {
		c.JSON(http.StatusBadRequest, gin.H{"error": err.Error()})
		return
	}

	response, err := h.theoryService.ReviewTheoryCard(uint(id), userID.(uint), &req)
	if err != nil {
		if err.Error() == "theory card not found" {
			c.JSON(http.StatusNotFound, gin.H{"error": err.Error()})
		} else {
			c.JSON(http.StatusInternalServerError, gin.H{"error": err.Error()})
		}
		return
	}

	c.JSON(http.StatusOK, response)
}

func (h *ContentHandler) GetCardsForReview(c *gin.Context) {
	userID, exists := c.Get("user_id")
	if !exists {
		c.JSON(http.StatusUnauthorized, gin.H{"error": "User not authenticated"})
		return
	}

	limitStr := c.DefaultQuery("limit", "10")
	limit, err := strconv.Atoi(limitStr)
	if err != nil || limit <= 0 || limit > 50 {
		limit = 10
	}

	response, err := h.theoryService.GetCardsForReview(userID.(uint), limit)
	if err != nil {
		c.JSON(http.StatusInternalServerError, gin.H{"error": err.Error()})
		return
	}

	c.JSON(http.StatusOK, response)
}