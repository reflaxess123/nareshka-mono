package services

import (
	"fmt"
	"math"
	"strings"
	"time"
	"nareshka-backend/app/shared/entities"
	"nareshka-backend/app/features/content/dto"

	"gorm.io/gorm"
)

type ContentService struct {
	db *gorm.DB
}

func NewContentService(db *gorm.DB) *ContentService {
	return &ContentService{
		db: db,
	}
}

func (s *ContentService) GetContentBlocks(req *dto.ContentBlockFilterRequest, userID *uint) (*dto.ContentBlockListResponse, error) {
	var blocks []entities.ContentBlock
	var total int64

	query := s.db.Model(&entities.ContentBlock{}).Where("is_active = ?", true)

	// Apply filters
	if req.Category != "" {
		query = query.Joins("JOIN content_files ON content_blocks.file_id = content_files.id").
			Where("content_files.main_category = ?", req.Category)
	}
	if req.SubCategory != "" {
		query = query.Joins("JOIN content_files ON content_blocks.file_id = content_files.id").
			Where("content_files.sub_category = ?", req.SubCategory)
	}
	if req.FileID != "" {
		query = query.Where("file_id = ?", req.FileID)
	}
	if req.Level != nil {
		query = query.Where("block_level = ?", *req.Level)
	}
	if req.MinOrder != nil {
		query = query.Where("order_in_file >= ?", *req.MinOrder)
	}
	if req.MaxOrder != nil {
		query = query.Where("order_in_file <= ?", *req.MaxOrder)
	}
	if req.Search != "" {
		searchTerm := "%" + strings.ToLower(req.Search) + "%"
		query = query.Where(
			"LOWER(block_title) LIKE ? OR LOWER(text_content) LIKE ? OR LOWER(code_content) LIKE ?",
			searchTerm, searchTerm, searchTerm,
		)
	}

	// Get total count
	if err := query.Count(&total).Error; err != nil {
		return nil, fmt.Errorf("failed to count content blocks: %w", err)
	}

	// Apply sorting
	sortBy := req.SortBy
	if sortBy == "" {
		sortBy = "order_in_file"
	}
	sortDir := req.SortDir
	if sortDir != "desc" {
		sortDir = "asc"
	}
	query = query.Order(fmt.Sprintf("%s %s", sortBy, sortDir))

	// Apply pagination
	offset := (req.Page - 1) * req.Limit
	query = query.Offset(offset).Limit(req.Limit)

	// Load blocks with relations
	preloadQuery := query.Preload("File")
	if userID != nil {
		preloadQuery = preloadQuery.Preload("UserProgress", "user_id = ?", *userID)
	}

	if err := preloadQuery.Find(&blocks).Error; err != nil {
		return nil, fmt.Errorf("failed to get content blocks: %w", err)
	}

	// Convert to response
	blockResponses := make([]dto.ContentBlockResponse, len(blocks))
	for i, block := range blocks {
		blockResponses[i] = dto.ContentBlockToResponse(&block)
	}

	totalPages := int(math.Ceil(float64(total) / float64(req.Limit)))

	return &dto.ContentBlockListResponse{
		Blocks:     blockResponses,
		Total:      total,
		Page:       req.Page,
		Limit:      req.Limit,
		TotalPages: totalPages,
	}, nil
}

func (s *ContentService) GetContentBlock(id string, userID *uint) (*dto.ContentBlockResponse, error) {
	var block entities.ContentBlock
	query := s.db.Preload("File")
	
	if userID != nil {
		query = query.Preload("UserProgress", "user_id = ?", *userID)
	}

	if err := query.First(&block, "id = ? AND is_active = ?", id, true).Error; err != nil {
		if err == gorm.ErrRecordNotFound {
			return nil, fmt.Errorf("content block not found")
		}
		return nil, fmt.Errorf("failed to get content block: %w", err)
	}

	response := dto.ContentBlockToResponse(&block)
	return &response, nil
}

func (s *ContentService) GetContentFiles(req *dto.ContentFileFilterRequest) (*dto.ContentFileListResponse, error) {
	var files []entities.ContentFile
	var total int64

	query := s.db.Model(&entities.ContentFile{}).Where("is_active = ?", true)

	// Apply filters
	if req.MainCategory != "" {
		query = query.Where("main_category = ?", req.MainCategory)
	}
	if req.SubCategory != "" {
		query = query.Where("sub_category = ?", req.SubCategory)
	}
	if req.Search != "" {
		searchTerm := "%" + strings.ToLower(req.Search) + "%"
		query = query.Where("LOWER(webdav_path) LIKE ?", searchTerm)
	}

	// Get total count
	if err := query.Count(&total).Error; err != nil {
		return nil, fmt.Errorf("failed to count content files: %w", err)
	}

	// Apply sorting
	sortBy := req.SortBy
	if sortBy == "" {
		sortBy = "created_at"
	}
	sortDir := req.SortDir
	if sortDir != "asc" {
		sortDir = "desc"
	}
	query = query.Order(fmt.Sprintf("%s %s", sortBy, sortDir))

	// Apply pagination
	offset := (req.Page - 1) * req.Limit
	query = query.Offset(offset).Limit(req.Limit)

	if err := query.Find(&files).Error; err != nil {
		return nil, fmt.Errorf("failed to get content files: %w", err)
	}

	// Convert to response
	fileResponses := make([]dto.ContentFileResponse, len(files))
	for i, file := range files {
		fileResponses[i] = dto.ContentFileToResponse(&file)
	}

	totalPages := int(math.Ceil(float64(total) / float64(req.Limit)))

	return &dto.ContentFileListResponse{
		Files:      fileResponses,
		Total:      total,
		Page:       req.Page,
		Limit:      req.Limit,
		TotalPages: totalPages,
	}, nil
}

func (s *ContentService) UpdateProgress(blockID string, userID uint, increment bool) (*dto.UserContentProgressResponse, error) {
	var progress entities.UserContentProgress

	// Check if block exists
	var block entities.ContentBlock
	if err := s.db.First(&block, "id = ? AND is_active = ?", blockID, true).Error; err != nil {
		if err == gorm.ErrRecordNotFound {
			return nil, fmt.Errorf("content block not found")
		}
		return nil, fmt.Errorf("failed to find content block: %w", err)
	}

	// Find or create progress record
	err := s.db.Where("user_id = ? AND content_block_id = ?", userID, blockID).First(&progress).Error
	if err != nil {
		if err == gorm.ErrRecordNotFound {
			// Create new progress record
			progress = entities.UserContentProgress{
				UserID:         userID,
				ContentBlockID: blockID,
				SolvedCount:    0,
				IsCompleted:    false,
				LastAccessedAt: time.Now(),
			}
			if err := s.db.Create(&progress).Error; err != nil {
				return nil, fmt.Errorf("failed to create progress record: %w", err)
			}
		} else {
			return nil, fmt.Errorf("failed to find progress record: %w", err)
		}
	}

	// Update progress
	if increment {
		progress.SolvedCount++
	} else if progress.SolvedCount > 0 {
		progress.SolvedCount--
	}

	progress.LastAccessedAt = time.Now()
	progress.IsCompleted = progress.SolvedCount > 0

	if err := s.db.Save(&progress).Error; err != nil {
		return nil, fmt.Errorf("failed to update progress: %w", err)
	}

	return &dto.UserContentProgressResponse{
		ID:             progress.ID,
		UserID:         progress.UserID,
		ContentBlockID: progress.ContentBlockID,
		SolvedCount:    progress.SolvedCount,
		IsCompleted:    progress.IsCompleted,
		LastAccessedAt: progress.LastAccessedAt,
		CreatedAt:      progress.CreatedAt,
		UpdatedAt:      progress.UpdatedAt,
	}, nil
}

func (s *ContentService) GetCategories() (*dto.CategoriesResponse, error) {
	var results []struct {
		MainCategory string
		SubCategory  string
		BlockCount   int64
	}

	err := s.db.Table("content_files").
		Select("content_files.main_category, content_files.sub_category, COUNT(content_blocks.id) as block_count").
		Joins("LEFT JOIN content_blocks ON content_files.id = content_blocks.file_id AND content_blocks.is_active = true").
		Where("content_files.is_active = true").
		Group("content_files.main_category, content_files.sub_category").
		Find(&results).Error

	if err != nil {
		return nil, fmt.Errorf("failed to get categories: %w", err)
	}

	// Group by main category
	categoryMap := make(map[string]*dto.CategoryResponse)
	for _, result := range results {
		if _, exists := categoryMap[result.MainCategory]; !exists {
			categoryMap[result.MainCategory] = &dto.CategoryResponse{
				Name:          result.MainCategory,
				SubCategories: []string{},
				BlockCount:    0,
			}
		}

		category := categoryMap[result.MainCategory]
		if result.SubCategory != "" {
			// Check if subcategory already exists
			exists := false
			for _, subCat := range category.SubCategories {
				if subCat == result.SubCategory {
					exists = true
					break
				}
			}
			if !exists {
				category.SubCategories = append(category.SubCategories, result.SubCategory)
			}
		}
		category.BlockCount += result.BlockCount
	}

	// Convert map to slice
	categories := make([]dto.CategoryResponse, 0, len(categoryMap))
	for _, category := range categoryMap {
		categories = append(categories, *category)
	}

	return &dto.CategoriesResponse{
		Categories: categories,
	}, nil
}