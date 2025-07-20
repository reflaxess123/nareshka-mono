package entities

import (
	"time"
)


type UserCategoryProgress struct {
	ID                    uint                 `json:"id" gorm:"primaryKey"`
	UserID                uint                 `json:"user_id" gorm:"not null;index"`
	User                  User                 `json:"user" gorm:"foreignKey:UserID"`
	Category              string               `json:"category" gorm:"size:100;not null"`
	TotalItems            int                  `json:"total_items" gorm:"default:0"`
	CompletedItems        int                  `json:"completed_items" gorm:"default:0"`
	ProgressPercentage    float32              `json:"progress_percentage" gorm:"default:0"`
	TotalTimeSpent        int                  `json:"total_time_spent" gorm:"default:0"`
	TotalPointsEarned     int                  `json:"total_points_earned" gorm:"default:0"`
	LastAccessedAt        *time.Time           `json:"last_accessed_at"`
	
	CreatedAt             time.Time            `json:"created_at" gorm:"autoCreateTime"`
	UpdatedAt             time.Time            `json:"updated_at" gorm:"autoUpdateTime"`
}

type UserPathProgress struct {
	ID                    uint                 `json:"id" gorm:"primaryKey"`
	UserID                uint                 `json:"user_id" gorm:"not null;index"`
	User                  User                 `json:"user" gorm:"foreignKey:UserID"`
	PathName              string               `json:"path_name" gorm:"size:200;not null"`
	TotalSteps            int                  `json:"total_steps" gorm:"default:0"`
	CompletedSteps        int                  `json:"completed_steps" gorm:"default:0"`
	CurrentStep           int                  `json:"current_step" gorm:"default:1"`
	ProgressPercentage    float32              `json:"progress_percentage" gorm:"default:0"`
	IsCompleted           bool                 `json:"is_completed" gorm:"default:false"`
	StartedAt             time.Time            `json:"started_at" gorm:"autoCreateTime"`
	CompletedAt           *time.Time           `json:"completed_at"`
	LastAccessedAt        *time.Time           `json:"last_accessed_at"`
	
	CreatedAt             time.Time            `json:"created_at" gorm:"autoCreateTime"`
	UpdatedAt             time.Time            `json:"updated_at" gorm:"autoUpdateTime"`
}

type UserActivity struct {
	ID                    uint                 `json:"id" gorm:"primaryKey"`
	UserID                uint                 `json:"user_id" gorm:"not null;index"`
	User                  User                 `json:"user" gorm:"foreignKey:UserID"`
	ActivityType          string               `json:"activity_type" gorm:"size:50;not null"`
	EntityType            string               `json:"entity_type" gorm:"size:50"`
	EntityID              *uint                `json:"entity_id"`
	Description           string               `json:"description" gorm:"type:text"`
	PointsEarned          int                  `json:"points_earned" gorm:"default:0"`
	Metadata              map[string]interface{} `json:"metadata" gorm:"type:jsonb"`
	
	CreatedAt             time.Time            `json:"created_at" gorm:"autoCreateTime"`
}

type UserStreak struct {
	ID                    uint                 `json:"id" gorm:"primaryKey"`
	UserID                uint                 `json:"user_id" gorm:"uniqueIndex;not null"`
	User                  User                 `json:"user" gorm:"foreignKey:UserID"`
	CurrentStreak         int                  `json:"current_streak" gorm:"default:0"`
	LongestStreak         int                  `json:"longest_streak" gorm:"default:0"`
	LastActivityDate      *time.Time           `json:"last_activity_date"`
	StreakStartDate       *time.Time           `json:"streak_start_date"`
	
	CreatedAt             time.Time            `json:"created_at" gorm:"autoCreateTime"`
	UpdatedAt             time.Time            `json:"updated_at" gorm:"autoUpdateTime"`
}