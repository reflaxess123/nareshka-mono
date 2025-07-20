package entities

import (
	"time"
	"nareshka-backend/app/shared/types"
	"gorm.io/gorm"
)

type User struct {
	ID                    uint             `json:"id" gorm:"primaryKey"`
	Username              string           `json:"username" gorm:"uniqueIndex;size:100;not null"`
	Email                 string           `json:"email" gorm:"uniqueIndex;size:255;not null"`
	PasswordHash          string           `json:"-" gorm:"size:255;not null"`
	Role                  types.UserRole   `json:"role" gorm:"type:varchar(20);default:'USER'"`
	IsActive              bool             `json:"is_active" gorm:"default:true"`
	FirstName             *string          `json:"first_name" gorm:"size:100"`
	LastName              *string          `json:"last_name" gorm:"size:100"`
	ProfilePicture        *string          `json:"profile_picture" gorm:"size:500"`
	Bio                   *string          `json:"bio" gorm:"type:text"`
	Location              *string          `json:"location" gorm:"size:200"`
	CompanyName           *string          `json:"company_name" gorm:"size:200"`
	Position              *string          `json:"position" gorm:"size:200"`
	ExperienceLevel       *string          `json:"experience_level" gorm:"size:50"`
	PreferredLanguages    []string         `json:"preferred_languages" gorm:"type:text[]"`
	
	// Progress tracking
	TotalTasksCompleted   int              `json:"total_tasks_completed" gorm:"default:0"`
	TotalPointsEarned     int              `json:"total_points_earned" gorm:"default:0"`
	CurrentStreak         int              `json:"current_streak" gorm:"default:0"`
	LongestStreak         int              `json:"longest_streak" gorm:"default:0"`
	LastActivityDate      *time.Time       `json:"last_activity_date"`
	
	// Timestamps
	CreatedAt             time.Time        `json:"created_at" gorm:"autoCreateTime"`
	UpdatedAt             time.Time        `json:"updated_at" gorm:"autoUpdateTime"`
	DeletedAt             gorm.DeletedAt   `json:"-" gorm:"index"`
}

type UserSession struct {
	ID        string    `json:"id" gorm:"primaryKey;size:255"`
	UserID    uint      `json:"user_id" gorm:"not null;index"`
	User      User      `json:"user" gorm:"foreignKey:UserID"`
	Data      string    `json:"data" gorm:"type:text"`
	ExpiresAt time.Time `json:"expires_at" gorm:"not null;index"`
	CreatedAt time.Time `json:"created_at" gorm:"autoCreateTime"`
	UpdatedAt time.Time `json:"updated_at" gorm:"autoUpdateTime"`
}

type UserPreferences struct {
	ID                    uint      `json:"id" gorm:"primaryKey"`
	UserID                uint      `json:"user_id" gorm:"uniqueIndex;not null"`
	User                  User      `json:"user" gorm:"foreignKey:UserID"`
	Theme                 string    `json:"theme" gorm:"size:20;default:'light'"`
	Language              string    `json:"language" gorm:"size:10;default:'en'"`
	EmailNotifications    bool      `json:"email_notifications" gorm:"default:true"`
	PushNotifications     bool      `json:"push_notifications" gorm:"default:true"`
	DefaultCodeLanguage   string    `json:"default_code_language" gorm:"size:20;default:'python'"`
	CreatedAt             time.Time `json:"created_at" gorm:"autoCreateTime"`
	UpdatedAt             time.Time `json:"updated_at" gorm:"autoUpdateTime"`
}