package entities

import (
	"time"
	"nareshka-backend/app/shared/types"
	"gorm.io/gorm"
)

type Task struct {
	ID                    uint                    `json:"id" gorm:"primaryKey"`
	Title                 string                  `json:"title" gorm:"size:200;not null"`
	Description           string                  `json:"description" gorm:"type:text"`
	Content               string                  `json:"content" gorm:"type:text"`
	DifficultyLevel       types.DifficultyLevel   `json:"difficulty_level" gorm:"type:varchar(20);not null"`
	Category              string                  `json:"category" gorm:"size:100"`
	Tags                  []string                `json:"tags" gorm:"type:text[]"`
	Points                int                     `json:"points" gorm:"default:0"`
	TimeLimit             *int                    `json:"time_limit"`
	MemoryLimit           *int                    `json:"memory_limit"`
	SupportedLanguages    []string                `json:"supported_languages" gorm:"type:text[]"`
	InitialCode           map[string]string       `json:"initial_code" gorm:"type:jsonb"`
	SolutionTemplate      map[string]string       `json:"solution_template" gorm:"type:jsonb"`
	IsPublic              bool                    `json:"is_public" gorm:"default:true"`
	IsActive              bool                    `json:"is_active" gorm:"default:true"`
	Order                 int                     `json:"order" gorm:"default:0"`
	
	// Relationships
	CreatedByID           uint                    `json:"created_by_id"`
	CreatedBy             User                    `json:"created_by" gorm:"foreignKey:CreatedByID"`
	TestCases             []TestCase              `json:"test_cases" gorm:"foreignKey:TaskID"`
	TaskAttempts          []TaskAttempt           `json:"task_attempts" gorm:"foreignKey:TaskID"`
	
	CreatedAt             time.Time               `json:"created_at" gorm:"autoCreateTime"`
	UpdatedAt             time.Time               `json:"updated_at" gorm:"autoUpdateTime"`
	DeletedAt             gorm.DeletedAt          `json:"-" gorm:"index"`
}

type TestCase struct {
	ID                    uint               `json:"id" gorm:"primaryKey"`
	TaskID                uint               `json:"task_id" gorm:"not null;index"`
	Task                  Task               `json:"task" gorm:"foreignKey:TaskID"`
	Input                 string             `json:"input" gorm:"type:text"`
	ExpectedOutput        string             `json:"expected_output" gorm:"type:text"`
	IsPublic              bool               `json:"is_public" gorm:"default:false"`
	IsActive              bool               `json:"is_active" gorm:"default:true"`
	Order                 int                `json:"order" gorm:"default:0"`
	TimeLimit             *int               `json:"time_limit"`
	MemoryLimit           *int               `json:"memory_limit"`
	
	CreatedAt             time.Time          `json:"created_at" gorm:"autoCreateTime"`
	UpdatedAt             time.Time          `json:"updated_at" gorm:"autoUpdateTime"`
}

type TaskAttempt struct {
	ID                    uint               `json:"id" gorm:"primaryKey"`
	TaskID                uint               `json:"task_id" gorm:"not null;index"`
	Task                  Task               `json:"task" gorm:"foreignKey:TaskID"`
	UserID                uint               `json:"user_id" gorm:"not null;index"`
	User                  User               `json:"user" gorm:"foreignKey:UserID"`
	Language              types.LanguageType `json:"language" gorm:"type:varchar(20);not null"`
	Code                  string             `json:"code" gorm:"type:text;not null"`
	Status                types.TaskStatus   `json:"status" gorm:"type:varchar(20);not null"`
	Score                 *int               `json:"score"`
	ExecutionTime         *int               `json:"execution_time"`
	MemoryUsed            *int               `json:"memory_used"`
	TestsPassed           int                `json:"tests_passed" gorm:"default:0"`
	TestsFailed           int                `json:"tests_failed" gorm:"default:0"`
	ErrorMessage          *string            `json:"error_message" gorm:"type:text"`
	Output                *string            `json:"output" gorm:"type:text"`
	
	CreatedAt             time.Time          `json:"created_at" gorm:"autoCreateTime"`
	UpdatedAt             time.Time          `json:"updated_at" gorm:"autoUpdateTime"`
}

type TaskSolution struct {
	ID                    uint               `json:"id" gorm:"primaryKey"`
	TaskID                uint               `json:"task_id" gorm:"not null;index"`
	Task                  Task               `json:"task" gorm:"foreignKey:TaskID"`
	Language              types.LanguageType `json:"language" gorm:"type:varchar(20);not null"`
	Code                  string             `json:"code" gorm:"type:text;not null"`
	Description           *string            `json:"description" gorm:"type:text"`
	IsOfficial            bool               `json:"is_official" gorm:"default:false"`
	
	CreatedByID           uint               `json:"created_by_id"`
	CreatedBy             User               `json:"created_by" gorm:"foreignKey:CreatedByID"`
	
	CreatedAt             time.Time          `json:"created_at" gorm:"autoCreateTime"`
	UpdatedAt             time.Time          `json:"updated_at" gorm:"autoUpdateTime"`
}