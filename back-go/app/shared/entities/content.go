package entities

import (
	"time"
	"nareshka-backend/app/shared/types"
	"gorm.io/gorm"
	"database/sql/driver"
	"encoding/json"
	"fmt"
)

type StringArray []string

func (sa *StringArray) Scan(value interface{}) error {
	if value == nil {
		*sa = nil
		return nil
	}
	switch v := value.(type) {
	case []byte:
		return json.Unmarshal(v, sa)
	case string:
		return json.Unmarshal([]byte(v), sa)
	}
	return fmt.Errorf("cannot scan %T into StringArray", value)
}

func (sa StringArray) Value() (driver.Value, error) {
	if sa == nil {
		return nil, nil
	}
	return json.Marshal(sa)
}

type ContentFile struct {
	ID              string    `json:"id" gorm:"primaryKey;size:255"`
	WebDAVPath      string    `json:"webdav_path" gorm:"uniqueIndex;size:500;not null"`
	MainCategory    string    `json:"main_category" gorm:"size:100;not null"`
	SubCategory     string    `json:"sub_category" gorm:"size:100"`
	LastFileHash    string    `json:"last_file_hash" gorm:"size:64"`
	IsActive        bool      `json:"is_active" gorm:"default:true"`
	CreatedAt       time.Time `json:"created_at"`
	UpdatedAt       time.Time `json:"updated_at"`

	// Relations
	ContentBlocks []ContentBlock `json:"content_blocks,omitempty" gorm:"foreignKey:FileID"`
}

type ContentBlock struct {
	ID              string      `json:"id" gorm:"primaryKey;size:255"`
	FileID          string      `json:"file_id" gorm:"size:255;not null;index"`
	PathTitles      StringArray `json:"path_titles" gorm:"type:jsonb"`
	BlockTitle      string      `json:"block_title" gorm:"size:500;not null"`
	BlockLevel      int         `json:"block_level" gorm:"not null"`
	OrderInFile     int         `json:"order_in_file" gorm:"not null"`
	TextContent     string      `json:"text_content" gorm:"type:text"`
	CodeContent     string      `json:"code_content" gorm:"type:text"`
	CodeLanguage    string      `json:"code_language" gorm:"size:50"`
	IsCodeFoldable  bool        `json:"is_code_foldable" gorm:"default:false"`
	CodeFoldTitle   string      `json:"code_fold_title" gorm:"size:200"`
	ExtractedURLs   StringArray `json:"extracted_urls" gorm:"type:jsonb"`
	Companies       StringArray `json:"companies" gorm:"type:jsonb"`
	IsActive        bool        `json:"is_active" gorm:"default:true"`
	CreatedAt       time.Time   `json:"created_at"`
	UpdatedAt       time.Time   `json:"updated_at"`

	// Relations
	File         ContentFile              `json:"file,omitempty" gorm:"foreignKey:FileID"`
	UserProgress []UserContentProgress    `json:"user_progress,omitempty" gorm:"foreignKey:ContentBlockID"`
}

type UserContentProgress struct {
	ID              uint      `json:"id" gorm:"primaryKey"`
	UserID          uint      `json:"user_id" gorm:"not null;index"`
	ContentBlockID  string    `json:"content_block_id" gorm:"size:255;not null;index"`
	SolvedCount     int       `json:"solved_count" gorm:"default:0"`
	IsCompleted     bool      `json:"is_completed" gorm:"default:false"`
	LastAccessedAt  time.Time `json:"last_accessed_at"`
	CreatedAt       time.Time `json:"created_at"`
	UpdatedAt       time.Time `json:"updated_at"`

	// Relations
	User         User         `json:"user,omitempty" gorm:"foreignKey:UserID"`
	ContentBlock ContentBlock `json:"content_block,omitempty" gorm:"foreignKey:ContentBlockID"`
}

type TheoryCard struct {
	ID              uint                     `json:"id" gorm:"primaryKey"`
	Title           string                   `json:"title" gorm:"size:500;not null"`
	Question        string                   `json:"question" gorm:"type:text;not null"`
	Answer          string                   `json:"answer" gorm:"type:text;not null"`
	Category        string                   `json:"category" gorm:"size:100;not null"`
	SubCategory     string                   `json:"sub_category" gorm:"size:100"`
	DifficultyLevel types.DifficultyLevel    `json:"difficulty_level" gorm:"type:varchar(20);not null"`
	Tags            StringArray              `json:"tags" gorm:"type:jsonb"`
	IsActive        bool                     `json:"is_active" gorm:"default:true"`
	CreatedByID     uint                     `json:"created_by_id" gorm:"not null;index"`
	CreatedAt       time.Time                `json:"created_at"`
	UpdatedAt       time.Time                `json:"updated_at"`
	DeletedAt       gorm.DeletedAt           `json:"deleted_at,omitempty" gorm:"index"`

	// Relations
	CreatedBy    User                  `json:"created_by,omitempty" gorm:"foreignKey:CreatedByID"`
	UserProgress []UserTheoryProgress  `json:"user_progress,omitempty" gorm:"foreignKey:TheoryCardID"`
}

type UserTheoryProgress struct {
	ID           uint                 `json:"id" gorm:"primaryKey"`
	UserID       uint                 `json:"user_id" gorm:"not null;index"`
	TheoryCardID uint                 `json:"theory_card_id" gorm:"not null;index"`
	Interval     int                  `json:"interval" gorm:"default:1"`
	Repetitions  int                  `json:"repetitions" gorm:"default:0"`
	EaseFactor   float64              `json:"ease_factor" gorm:"default:2.5"`
	NextReviewAt time.Time            `json:"next_review_at"`
	LastAnswer   types.ReviewAnswer   `json:"last_answer" gorm:"type:varchar(20)"`
	IsActive     bool                 `json:"is_active" gorm:"default:true"`
	CreatedAt    time.Time            `json:"created_at"`
	UpdatedAt    time.Time            `json:"updated_at"`

	// Relations
	User       User       `json:"user,omitempty" gorm:"foreignKey:UserID"`
	TheoryCard TheoryCard `json:"theory_card,omitempty" gorm:"foreignKey:TheoryCardID"`
}