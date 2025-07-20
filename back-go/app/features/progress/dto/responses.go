package dto

import (
	"time"
	"nareshka-backend/app/shared/entities"
)

type UserActivityResponse struct {
	ID           uint                   `json:"id"`
	UserID       uint                   `json:"user_id"`
	ActivityType string                 `json:"activity_type"`
	EntityType   string                 `json:"entity_type"`
	EntityID     *uint                  `json:"entity_id"`
	Description  string                 `json:"description"`
	PointsEarned int                    `json:"points_earned"`
	Metadata     map[string]interface{} `json:"metadata"`
	CreatedAt    time.Time              `json:"created_at"`
}

type UserCategoryProgressResponse struct {
	ID                uint      `json:"id"`
	UserID            uint      `json:"user_id"`
	Category          string    `json:"category"`
	TotalItems        int       `json:"total_items"`
	CompletedItems    int       `json:"completed_items"`
	ProgressPercentage float32  `json:"progress_percentage"`
	TotalTimeSpent    int       `json:"total_time_spent"`
	TotalPointsEarned int       `json:"total_points_earned"`
	LastAccessedAt    *time.Time `json:"last_accessed_at"`
	CreatedAt         time.Time `json:"created_at"`
	UpdatedAt         time.Time `json:"updated_at"`
}

type UserPathProgressResponse struct {
	ID                uint       `json:"id"`
	UserID            uint       `json:"user_id"`
	PathName          string     `json:"path_name"`
	TotalSteps        int        `json:"total_steps"`
	CompletedSteps    int        `json:"completed_steps"`
	CurrentStep       int        `json:"current_step"`
	ProgressPercentage float32   `json:"progress_percentage"`
	IsCompleted       bool       `json:"is_completed"`
	StartedAt         time.Time  `json:"started_at"`
	CompletedAt       *time.Time `json:"completed_at"`
	LastAccessedAt    *time.Time `json:"last_accessed_at"`
	CreatedAt         time.Time  `json:"created_at"`
	UpdatedAt         time.Time  `json:"updated_at"`
}

type UserStreakResponse struct {
	ID               uint       `json:"id"`
	UserID           uint       `json:"user_id"`
	CurrentStreak    int        `json:"current_streak"`
	LongestStreak    int        `json:"longest_streak"`
	LastActivityDate *time.Time `json:"last_activity_date"`
	StreakStartDate  *time.Time `json:"streak_start_date"`
	CreatedAt        time.Time  `json:"created_at"`
	UpdatedAt        time.Time  `json:"updated_at"`
}

type UserActivityListResponse struct {
	Activities []UserActivityResponse `json:"activities"`
	Total      int64                  `json:"total"`
	Page       int                    `json:"page"`
	Limit      int                    `json:"limit"`
	TotalPages int                    `json:"total_pages"`
}

type UserProgressSummaryResponse struct {
	TotalTasksCompleted int                             `json:"total_tasks_completed"`
	TotalPointsEarned   int                             `json:"total_points_earned"`
	CurrentStreak       int                             `json:"current_streak"`
	LongestStreak       int                             `json:"longest_streak"`
	LastActivityDate    *time.Time                      `json:"last_activity_date"`
	Categories          []UserCategoryProgressResponse `json:"categories"`
	Paths              []UserPathProgressResponse      `json:"paths"`
	RecentActivities   []UserActivityResponse          `json:"recent_activities"`
}

// Converter functions
func UserActivityToResponse(activity *entities.UserActivity) UserActivityResponse {
	return UserActivityResponse{
		ID:           activity.ID,
		UserID:       activity.UserID,
		ActivityType: activity.ActivityType,
		EntityType:   activity.EntityType,
		EntityID:     activity.EntityID,
		Description:  activity.Description,
		PointsEarned: activity.PointsEarned,
		Metadata:     activity.Metadata,
		CreatedAt:    activity.CreatedAt,
	}
}

func UserCategoryProgressToResponse(progress *entities.UserCategoryProgress) UserCategoryProgressResponse {
	return UserCategoryProgressResponse{
		ID:                progress.ID,
		UserID:            progress.UserID,
		Category:          progress.Category,
		TotalItems:        progress.TotalItems,
		CompletedItems:    progress.CompletedItems,
		ProgressPercentage: progress.ProgressPercentage,
		TotalTimeSpent:    progress.TotalTimeSpent,
		TotalPointsEarned: progress.TotalPointsEarned,
		LastAccessedAt:    progress.LastAccessedAt,
		CreatedAt:         progress.CreatedAt,
		UpdatedAt:         progress.UpdatedAt,
	}
}

func UserPathProgressToResponse(progress *entities.UserPathProgress) UserPathProgressResponse {
	return UserPathProgressResponse{
		ID:                progress.ID,
		UserID:            progress.UserID,
		PathName:          progress.PathName,
		TotalSteps:        progress.TotalSteps,
		CompletedSteps:    progress.CompletedSteps,
		CurrentStep:       progress.CurrentStep,
		ProgressPercentage: progress.ProgressPercentage,
		IsCompleted:       progress.IsCompleted,
		StartedAt:         progress.StartedAt,
		CompletedAt:       progress.CompletedAt,
		LastAccessedAt:    progress.LastAccessedAt,
		CreatedAt:         progress.CreatedAt,
		UpdatedAt:         progress.UpdatedAt,
	}
}

func UserStreakToResponse(streak *entities.UserStreak) UserStreakResponse {
	return UserStreakResponse{
		ID:               streak.ID,
		UserID:           streak.UserID,
		CurrentStreak:    streak.CurrentStreak,
		LongestStreak:    streak.LongestStreak,
		LastActivityDate: streak.LastActivityDate,
		StreakStartDate:  streak.StreakStartDate,
		CreatedAt:        streak.CreatedAt,
		UpdatedAt:        streak.UpdatedAt,
	}
}