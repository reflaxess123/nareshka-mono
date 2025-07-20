package services

import (
	"fmt"
	"math"
	"time"
	"nareshka-backend/app/shared/entities"
	"nareshka-backend/app/features/content/dto"
	"nareshka-backend/app/shared/types"

	"gorm.io/gorm"
)

type TheoryService struct {
	db *gorm.DB
}

func NewTheoryService(db *gorm.DB) *TheoryService {
	return &TheoryService{
		db: db,
	}
}

func (s *TheoryService) CreateTheoryCard(userID uint, req *dto.CreateTheoryCardRequest) (*dto.TheoryCardResponse, error) {
	card := &entities.TheoryCard{
		Title:           req.Title,
		Question:        req.Question,
		Answer:          req.Answer,
		Category:        req.Category,
		SubCategory:     req.SubCategory,
		DifficultyLevel: req.DifficultyLevel,
		Tags:            entities.StringArray(req.Tags),
		IsActive:        true,
		CreatedByID:     userID,
	}

	if err := s.db.Create(card).Error; err != nil {
		return nil, fmt.Errorf("failed to create theory card: %w", err)
	}

	// Load created card with relations
	if err := s.db.Preload("CreatedBy").First(card, card.ID).Error; err != nil {
		return nil, fmt.Errorf("failed to load created theory card: %w", err)
	}

	response := dto.TheoryCardToResponse(card)
	return &response, nil
}

func (s *TheoryService) GetTheoryCard(id uint, userID *uint) (*dto.TheoryCardResponse, error) {
	var card entities.TheoryCard
	query := s.db.Preload("CreatedBy")
	
	if userID != nil {
		query = query.Preload("UserProgress", "user_id = ?", *userID)
	}

	if err := query.First(&card, "id = ? AND is_active = ?", id, true).Error; err != nil {
		if err == gorm.ErrRecordNotFound {
			return nil, fmt.Errorf("theory card not found")
		}
		return nil, fmt.Errorf("failed to get theory card: %w", err)
	}

	response := dto.TheoryCardToResponse(&card)
	return &response, nil
}

func (s *TheoryService) GetTheoryCards(req *dto.TheoryCardFilterRequest, userID *uint) (*dto.TheoryCardListResponse, error) {
	var cards []entities.TheoryCard
	var total int64

	query := s.db.Model(&entities.TheoryCard{}).Where("is_active = ?", true)

	// Apply filters
	if req.Category != "" {
		query = query.Where("category = ?", req.Category)
	}
	if req.SubCategory != "" {
		query = query.Where("sub_category = ?", req.SubCategory)
	}
	if req.DifficultyLevel != nil {
		query = query.Where("difficulty_level = ?", *req.DifficultyLevel)
	}
	if len(req.Tags) > 0 {
		query = query.Where("tags && ?", req.Tags)
	}
	if req.CreatedBy != nil {
		query = query.Where("created_by_id = ?", *req.CreatedBy)
	}

	// Get total count
	if err := query.Count(&total).Error; err != nil {
		return nil, fmt.Errorf("failed to count theory cards: %w", err)
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

	// Load cards with relations
	preloadQuery := query.Preload("CreatedBy")
	if userID != nil {
		preloadQuery = preloadQuery.Preload("UserProgress", "user_id = ?", *userID)
	}

	if err := preloadQuery.Find(&cards).Error; err != nil {
		return nil, fmt.Errorf("failed to get theory cards: %w", err)
	}

	// Convert to response
	cardResponses := make([]dto.TheoryCardResponse, len(cards))
	for i, card := range cards {
		cardResponses[i] = dto.TheoryCardToResponse(&card)
	}

	totalPages := int(math.Ceil(float64(total) / float64(req.Limit)))

	return &dto.TheoryCardListResponse{
		Cards:      cardResponses,
		Total:      total,
		Page:       req.Page,
		Limit:      req.Limit,
		TotalPages: totalPages,
	}, nil
}

func (s *TheoryService) UpdateTheoryCard(id uint, userID uint, req *dto.UpdateTheoryCardRequest) (*dto.TheoryCardResponse, error) {
	var card entities.TheoryCard
	if err := s.db.First(&card, id).Error; err != nil {
		if err == gorm.ErrRecordNotFound {
			return nil, fmt.Errorf("theory card not found")
		}
		return nil, fmt.Errorf("failed to get theory card: %w", err)
	}

	// Check if user is creator
	if card.CreatedByID != userID {
		return nil, fmt.Errorf("permission denied")
	}

	// Update fields
	updates := make(map[string]interface{})
	if req.Title != nil {
		updates["title"] = *req.Title
	}
	if req.Question != nil {
		updates["question"] = *req.Question
	}
	if req.Answer != nil {
		updates["answer"] = *req.Answer
	}
	if req.Category != nil {
		updates["category"] = *req.Category
	}
	if req.SubCategory != nil {
		updates["sub_category"] = *req.SubCategory
	}
	if req.DifficultyLevel != nil {
		updates["difficulty_level"] = *req.DifficultyLevel
	}
	if req.Tags != nil {
		updates["tags"] = entities.StringArray(req.Tags)
	}
	if req.IsActive != nil {
		updates["is_active"] = *req.IsActive
	}

	if err := s.db.Model(&card).Updates(updates).Error; err != nil {
		return nil, fmt.Errorf("failed to update theory card: %w", err)
	}

	// Load updated card
	if err := s.db.Preload("CreatedBy").First(&card, id).Error; err != nil {
		return nil, fmt.Errorf("failed to load updated theory card: %w", err)
	}

	response := dto.TheoryCardToResponse(&card)
	return &response, nil
}

func (s *TheoryService) DeleteTheoryCard(id uint, userID uint) error {
	var card entities.TheoryCard
	if err := s.db.First(&card, id).Error; err != nil {
		if err == gorm.ErrRecordNotFound {
			return fmt.Errorf("theory card not found")
		}
		return fmt.Errorf("failed to get theory card: %w", err)
	}

	// Check if user is creator
	if card.CreatedByID != userID {
		return fmt.Errorf("permission denied")
	}

	// Soft delete
	if err := s.db.Delete(&card).Error; err != nil {
		return fmt.Errorf("failed to delete theory card: %w", err)
	}

	return nil
}

func (s *TheoryService) ReviewTheoryCard(cardID uint, userID uint, req *dto.ReviewTheoryCardRequest) (*dto.UserTheoryProgressResponse, error) {
	// Check if card exists
	var card entities.TheoryCard
	if err := s.db.First(&card, "id = ? AND is_active = ?", cardID, true).Error; err != nil {
		if err == gorm.ErrRecordNotFound {
			return nil, fmt.Errorf("theory card not found")
		}
		return nil, fmt.Errorf("failed to find theory card: %w", err)
	}

	// Find or create progress record
	var progress entities.UserTheoryProgress
	err := s.db.Where("user_id = ? AND theory_card_id = ?", userID, cardID).First(&progress).Error
	if err != nil {
		if err == gorm.ErrRecordNotFound {
			// Create new progress record
			progress = entities.UserTheoryProgress{
				UserID:       userID,
				TheoryCardID: cardID,
				Interval:     1,
				Repetitions:  0,
				EaseFactor:   2.5,
				NextReviewAt: time.Now().AddDate(0, 0, 1),
				LastAnswer:   req.Answer,
				IsActive:     true,
			}
		} else {
			return nil, fmt.Errorf("failed to find progress record: %w", err)
		}
	}

	// Apply spaced repetition algorithm (simplified SM-2)
	progress.LastAnswer = req.Answer
	
	if req.Answer == types.ReviewAnswerAgain {
		// Reset progress for failed review
		progress.Repetitions = 0
		progress.Interval = 1
	} else {
		progress.Repetitions++
		
		// Calculate ease factor adjustment
		var quality int
		switch req.Answer {
		case types.ReviewAnswerHard:
			quality = 3
		case types.ReviewAnswerGood:
			quality = 4
		case types.ReviewAnswerEasy:
			quality = 5
		}
		
		// Update ease factor (SM-2 algorithm)
		progress.EaseFactor = progress.EaseFactor + (0.1 - (5-float64(quality))*(0.08+(5-float64(quality))*0.02))
		if progress.EaseFactor < 1.3 {
			progress.EaseFactor = 1.3
		}
		
		// Calculate next interval
		if progress.Repetitions <= 1 {
			progress.Interval = 1
		} else if progress.Repetitions == 2 {
			progress.Interval = 6
		} else {
			progress.Interval = int(float64(progress.Interval) * progress.EaseFactor)
		}
	}
	
	progress.NextReviewAt = time.Now().AddDate(0, 0, progress.Interval)

	// Save progress
	if err := s.db.Save(&progress).Error; err != nil {
		return nil, fmt.Errorf("failed to save progress: %w", err)
	}

	return &dto.UserTheoryProgressResponse{
		ID:           progress.ID,
		UserID:       progress.UserID,
		TheoryCardID: progress.TheoryCardID,
		Interval:     progress.Interval,
		Repetitions:  progress.Repetitions,
		EaseFactor:   progress.EaseFactor,
		NextReviewAt: progress.NextReviewAt,
		LastAnswer:   progress.LastAnswer,
		IsActive:     progress.IsActive,
		CreatedAt:    progress.CreatedAt,
		UpdatedAt:    progress.UpdatedAt,
	}, nil
}

func (s *TheoryService) GetCardsForReview(userID uint, limit int) (*dto.TheoryCardListResponse, error) {
	var progressRecords []entities.UserTheoryProgress
	
	// Find cards that are due for review
	err := s.db.Where("user_id = ? AND is_active = ? AND next_review_at <= ?", userID, true, time.Now()).
		Preload("TheoryCard", "is_active = ?", true).
		Preload("TheoryCard.CreatedBy").
		Limit(limit).
		Find(&progressRecords).Error
	
	if err != nil {
		return nil, fmt.Errorf("failed to get cards for review: %w", err)
	}

	// Convert to response
	cardResponses := make([]dto.TheoryCardResponse, len(progressRecords))
	for i, progress := range progressRecords {
		card := progress.TheoryCard
		response := dto.TheoryCardToResponse(&card)
		
		// Add progress information
		response.Progress = &dto.UserTheoryProgressResponse{
			ID:           progress.ID,
			UserID:       progress.UserID,
			TheoryCardID: progress.TheoryCardID,
			Interval:     progress.Interval,
			Repetitions:  progress.Repetitions,
			EaseFactor:   progress.EaseFactor,
			NextReviewAt: progress.NextReviewAt,
			LastAnswer:   progress.LastAnswer,
			IsActive:     progress.IsActive,
			CreatedAt:    progress.CreatedAt,
			UpdatedAt:    progress.UpdatedAt,
		}
		
		cardResponses[i] = response
	}

	return &dto.TheoryCardListResponse{
		Cards:      cardResponses,
		Total:      int64(len(cardResponses)),
		Page:       1,
		Limit:      limit,
		TotalPages: 1,
	}, nil
}