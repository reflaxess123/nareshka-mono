package services

import (
	"fmt"
	"math"
	"time"
	"nareshka-backend/app/shared/entities"
	"nareshka-backend/app/features/progress/dto"

	"gorm.io/gorm"
)

type ProgressService struct {
	db *gorm.DB
}

func NewProgressService(db *gorm.DB) *ProgressService {
	return &ProgressService{
		db: db,
	}
}

func (s *ProgressService) RecordActivity(userID uint, req *dto.UpdateActivityRequest) (*dto.UserActivityResponse, error) {
	activity := &entities.UserActivity{
		UserID:       userID,
		ActivityType: req.ActivityType,
		EntityType:   req.EntityType,
		EntityID:     req.EntityID,
		Description:  req.Description,
		PointsEarned: req.PointsEarned,
		Metadata:     req.Metadata,
	}

	if err := s.db.Create(activity).Error; err != nil {
		return nil, fmt.Errorf("failed to record activity: %w", err)
	}

	// Update user stats
	if err := s.updateUserStats(userID, req.PointsEarned); err != nil {
		return nil, fmt.Errorf("failed to update user stats: %w", err)
	}

	// Update streak
	if err := s.updateUserStreak(userID); err != nil {
		return nil, fmt.Errorf("failed to update user streak: %w", err)
	}

	response := dto.UserActivityToResponse(activity)
	return &response, nil
}

func (s *ProgressService) GetUserActivities(userID uint, req *dto.ProgressFilterRequest) (*dto.UserActivityListResponse, error) {
	var activities []entities.UserActivity
	var total int64

	query := s.db.Model(&entities.UserActivity{}).Where("user_id = ?", userID)

	// Apply filters
	if req.ActivityType != "" {
		query = query.Where("activity_type = ?", req.ActivityType)
	}
	if req.StartDate != "" {
		if startTime, err := time.Parse("2006-01-02", req.StartDate); err == nil {
			query = query.Where("created_at >= ?", startTime)
		}
	}
	if req.EndDate != "" {
		if endTime, err := time.Parse("2006-01-02", req.EndDate); err == nil {
			query = query.Where("created_at <= ?", endTime.Add(24*time.Hour))
		}
	}

	// Get total count
	if err := query.Count(&total).Error; err != nil {
		return nil, fmt.Errorf("failed to count activities: %w", err)
	}

	// Apply pagination and ordering
	offset := (req.Page - 1) * req.Limit
	query = query.Order("created_at DESC").Offset(offset).Limit(req.Limit)

	if err := query.Find(&activities).Error; err != nil {
		return nil, fmt.Errorf("failed to get activities: %w", err)
	}

	// Convert to response
	activityResponses := make([]dto.UserActivityResponse, len(activities))
	for i, activity := range activities {
		activityResponses[i] = dto.UserActivityToResponse(&activity)
	}

	totalPages := int(math.Ceil(float64(total) / float64(req.Limit)))

	return &dto.UserActivityListResponse{
		Activities: activityResponses,
		Total:      total,
		Page:       req.Page,
		Limit:      req.Limit,
		TotalPages: totalPages,
	}, nil
}

func (s *ProgressService) GetUserProgressSummary(userID uint) (*dto.UserProgressSummaryResponse, error) {
	// Get user basic stats
	var user entities.User
	if err := s.db.First(&user, userID).Error; err != nil {
		return nil, fmt.Errorf("failed to get user: %w", err)
	}

	// Get streak information
	var streak entities.UserStreak
	err := s.db.Where("user_id = ?", userID).First(&streak).Error
	if err != nil && err != gorm.ErrRecordNotFound {
		return nil, fmt.Errorf("failed to get user streak: %w", err)
	}

	// Get category progress
	var categoryProgress []entities.UserCategoryProgress
	if err := s.db.Where("user_id = ?", userID).Find(&categoryProgress).Error; err != nil {
		return nil, fmt.Errorf("failed to get category progress: %w", err)
	}

	// Get path progress
	var pathProgress []entities.UserPathProgress
	if err := s.db.Where("user_id = ?", userID).Find(&pathProgress).Error; err != nil {
		return nil, fmt.Errorf("failed to get path progress: %w", err)
	}

	// Get recent activities
	var recentActivities []entities.UserActivity
	if err := s.db.Where("user_id = ?", userID).Order("created_at DESC").Limit(10).Find(&recentActivities).Error; err != nil {
		return nil, fmt.Errorf("failed to get recent activities: %w", err)
	}

	// Convert to responses
	categoryResponses := make([]dto.UserCategoryProgressResponse, len(categoryProgress))
	for i, cp := range categoryProgress {
		categoryResponses[i] = dto.UserCategoryProgressToResponse(&cp)
	}

	pathResponses := make([]dto.UserPathProgressResponse, len(pathProgress))
	for i, pp := range pathProgress {
		pathResponses[i] = dto.UserPathProgressToResponse(&pp)
	}

	activityResponses := make([]dto.UserActivityResponse, len(recentActivities))
	for i, activity := range recentActivities {
		activityResponses[i] = dto.UserActivityToResponse(&activity)
	}

	return &dto.UserProgressSummaryResponse{
		TotalTasksCompleted: user.TotalTasksCompleted,
		TotalPointsEarned:   user.TotalPointsEarned,
		CurrentStreak:       streak.CurrentStreak,
		LongestStreak:       streak.LongestStreak,
		LastActivityDate:    streak.LastActivityDate,
		Categories:          categoryResponses,
		Paths:              pathResponses,
		RecentActivities:   activityResponses,
	}, nil
}

func (s *ProgressService) UpdateCategoryProgress(userID uint, req *dto.CategoryProgressRequest) (*dto.UserCategoryProgressResponse, error) {
	var progress entities.UserCategoryProgress

	// Find or create category progress
	err := s.db.Where("user_id = ? AND category = ?", userID, req.Category).First(&progress).Error
	if err != nil {
		if err == gorm.ErrRecordNotFound {
			progress = entities.UserCategoryProgress{
				UserID:   userID,
				Category: req.Category,
			}
		} else {
			return nil, fmt.Errorf("failed to find category progress: %w", err)
		}
	}

	// Update completed items and calculate percentage
	progress.CompletedItems++
	if progress.TotalItems > 0 {
		progress.ProgressPercentage = float32(progress.CompletedItems) / float32(progress.TotalItems) * 100
	}
	
	now := time.Now()
	progress.LastAccessedAt = &now

	if err := s.db.Save(&progress).Error; err != nil {
		return nil, fmt.Errorf("failed to update category progress: %w", err)
	}

	response := dto.UserCategoryProgressToResponse(&progress)
	return &response, nil
}

func (s *ProgressService) UpdatePathProgress(userID uint, req *dto.PathProgressRequest) (*dto.UserPathProgressResponse, error) {
	var progress entities.UserPathProgress

	// Find or create path progress
	err := s.db.Where("user_id = ? AND path_name = ?", userID, req.PathName).First(&progress).Error
	if err != nil {
		if err == gorm.ErrRecordNotFound {
			progress = entities.UserPathProgress{
				UserID:      userID,
				PathName:    req.PathName,
				CurrentStep: 1,
			}
		} else {
			return nil, fmt.Errorf("failed to find path progress: %w", err)
		}
	}

	// Update progress
	if progress.CurrentStep < progress.TotalSteps {
		progress.CurrentStep++
		progress.CompletedSteps++
	}

	if progress.TotalSteps > 0 {
		progress.ProgressPercentage = float32(progress.CompletedSteps) / float32(progress.TotalSteps) * 100
	}

	if progress.CompletedSteps >= progress.TotalSteps && !progress.IsCompleted {
		progress.IsCompleted = true
		now := time.Now()
		progress.CompletedAt = &now
	}

	now := time.Now()
	progress.LastAccessedAt = &now

	if err := s.db.Save(&progress).Error; err != nil {
		return nil, fmt.Errorf("failed to update path progress: %w", err)
	}

	response := dto.UserPathProgressToResponse(&progress)
	return &response, nil
}

func (s *ProgressService) updateUserStats(userID uint, pointsEarned int) error {
	return s.db.Model(&entities.User{}).Where("id = ?", userID).Updates(map[string]interface{}{
		"total_points_earned": gorm.Expr("total_points_earned + ?", pointsEarned),
		"last_activity_date":  time.Now(),
	}).Error
}

func (s *ProgressService) updateUserStreak(userID uint) error {
	var streak entities.UserStreak
	now := time.Now()
	today := time.Date(now.Year(), now.Month(), now.Day(), 0, 0, 0, 0, time.UTC)

	// Find or create streak record
	err := s.db.Where("user_id = ?", userID).First(&streak).Error
	if err != nil {
		if err == gorm.ErrRecordNotFound {
			// Create new streak
			streak = entities.UserStreak{
				UserID:           userID,
				CurrentStreak:    1,
				LongestStreak:    1,
				LastActivityDate: &now,
				StreakStartDate:  &today,
			}
			return s.db.Create(&streak).Error
		}
		return err
	}

	// Check if activity is on a new day
	if streak.LastActivityDate != nil {
		lastActivityDay := time.Date(
			streak.LastActivityDate.Year(),
			streak.LastActivityDate.Month(),
			streak.LastActivityDate.Day(),
			0, 0, 0, 0, time.UTC,
		)

		daysDiff := int(today.Sub(lastActivityDay).Hours() / 24)

		if daysDiff == 1 {
			// Consecutive day - increment streak
			streak.CurrentStreak++
			if streak.CurrentStreak > streak.LongestStreak {
				streak.LongestStreak = streak.CurrentStreak
			}
		} else if daysDiff > 1 {
			// Streak broken - reset
			streak.CurrentStreak = 1
			streak.StreakStartDate = &today
		}
		// If daysDiff == 0, it's the same day, no change needed
	}

	streak.LastActivityDate = &now
	return s.db.Save(&streak).Error
}