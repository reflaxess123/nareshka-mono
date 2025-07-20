package dto

import (
	"time"
	"nareshka-backend/app/shared/entities"
	"nareshka-backend/app/shared/types"
)

type ContentFileResponse struct {
	ID           string    `json:"id"`
	WebDAVPath   string    `json:"webdav_path"`
	MainCategory string    `json:"main_category"`
	SubCategory  string    `json:"sub_category"`
	LastFileHash string    `json:"last_file_hash"`
	IsActive     bool      `json:"is_active"`
	CreatedAt    time.Time `json:"created_at"`
	UpdatedAt    time.Time `json:"updated_at"`
}

type ContentBlockResponse struct {
	ID             string                      `json:"id"`
	FileID         string                      `json:"file_id"`
	PathTitles     []string                    `json:"path_titles"`
	BlockTitle     string                      `json:"block_title"`
	BlockLevel     int                         `json:"block_level"`
	OrderInFile    int                         `json:"order_in_file"`
	TextContent    string                      `json:"text_content"`
	CodeContent    string                      `json:"code_content"`
	CodeLanguage   string                      `json:"code_language"`
	IsCodeFoldable bool                        `json:"is_code_foldable"`
	CodeFoldTitle  string                      `json:"code_fold_title"`
	ExtractedURLs  []string                    `json:"extracted_urls"`
	Companies      []string                    `json:"companies"`
	IsActive       bool                        `json:"is_active"`
	CreatedAt      time.Time                   `json:"created_at"`
	UpdatedAt      time.Time                   `json:"updated_at"`
	File           *ContentFileResponse        `json:"file,omitempty"`
	Progress       *UserContentProgressResponse `json:"progress,omitempty"`
}

type ContentBlockListResponse struct {
	Blocks     []ContentBlockResponse `json:"blocks"`
	Total      int64                  `json:"total"`
	Page       int                    `json:"page"`
	Limit      int                    `json:"limit"`
	TotalPages int                    `json:"total_pages"`
}

type ContentFileListResponse struct {
	Files      []ContentFileResponse `json:"files"`
	Total      int64                 `json:"total"`
	Page       int                   `json:"page"`
	Limit      int                   `json:"limit"`
	TotalPages int                   `json:"total_pages"`
}

type UserContentProgressResponse struct {
	ID             uint      `json:"id"`
	UserID         uint      `json:"user_id"`
	ContentBlockID string    `json:"content_block_id"`
	SolvedCount    int       `json:"solved_count"`
	IsCompleted    bool      `json:"is_completed"`
	LastAccessedAt time.Time `json:"last_accessed_at"`
	CreatedAt      time.Time `json:"created_at"`
	UpdatedAt      time.Time `json:"updated_at"`
}

type CategoryResponse struct {
	Name           string   `json:"name"`
	SubCategories  []string `json:"sub_categories,omitempty"`
	BlockCount     int64    `json:"block_count"`
}

type CategoriesResponse struct {
	Categories []CategoryResponse `json:"categories"`
}

type TheoryCardResponse struct {
	ID              uint                     `json:"id"`
	Title           string                   `json:"title"`
	Question        string                   `json:"question"`
	Answer          string                   `json:"answer"`
	Category        string                   `json:"category"`
	SubCategory     string                   `json:"sub_category"`
	DifficultyLevel types.DifficultyLevel    `json:"difficulty_level"`
	Tags            []string                 `json:"tags"`
	IsActive        bool                     `json:"is_active"`
	CreatedByID     uint                     `json:"created_by_id"`
	CreatedBy       *UserResponse            `json:"created_by,omitempty"`
	Progress        *UserTheoryProgressResponse `json:"progress,omitempty"`
	CreatedAt       time.Time                `json:"created_at"`
	UpdatedAt       time.Time                `json:"updated_at"`
}

type TheoryCardListResponse struct {
	Cards      []TheoryCardResponse `json:"cards"`
	Total      int64                `json:"total"`
	Page       int                  `json:"page"`
	Limit      int                  `json:"limit"`
	TotalPages int                  `json:"total_pages"`
}

type UserTheoryProgressResponse struct {
	ID           uint                `json:"id"`
	UserID       uint                `json:"user_id"`
	TheoryCardID uint                `json:"theory_card_id"`
	Interval     int                 `json:"interval"`
	Repetitions  int                 `json:"repetitions"`
	EaseFactor   float64             `json:"ease_factor"`
	NextReviewAt time.Time           `json:"next_review_at"`
	LastAnswer   types.ReviewAnswer  `json:"last_answer"`
	IsActive     bool                `json:"is_active"`
	CreatedAt    time.Time           `json:"created_at"`
	UpdatedAt    time.Time           `json:"updated_at"`
}

type UserResponse struct {
	ID                  uint           `json:"id"`
	Username            string         `json:"username"`
	Email               string         `json:"email"`
	Role                types.UserRole `json:"role"`
	FirstName           *string        `json:"first_name"`
	LastName            *string        `json:"last_name"`
	ProfilePicture      *string        `json:"profile_picture"`
	TotalTasksCompleted int            `json:"total_tasks_completed"`
	TotalPointsEarned   int            `json:"total_points_earned"`
	CurrentStreak       int            `json:"current_streak"`
}

// Converter functions
func ContentFileToResponse(file *entities.ContentFile) ContentFileResponse {
	return ContentFileResponse{
		ID:           file.ID,
		WebDAVPath:   file.WebDAVPath,
		MainCategory: file.MainCategory,
		SubCategory:  file.SubCategory,
		LastFileHash: file.LastFileHash,
		IsActive:     file.IsActive,
		CreatedAt:    file.CreatedAt,
		UpdatedAt:    file.UpdatedAt,
	}
}

func ContentBlockToResponse(block *entities.ContentBlock) ContentBlockResponse {
	response := ContentBlockResponse{
		ID:             block.ID,
		FileID:         block.FileID,
		PathTitles:     []string(block.PathTitles),
		BlockTitle:     block.BlockTitle,
		BlockLevel:     block.BlockLevel,
		OrderInFile:    block.OrderInFile,
		TextContent:    block.TextContent,
		CodeContent:    block.CodeContent,
		CodeLanguage:   block.CodeLanguage,
		IsCodeFoldable: block.IsCodeFoldable,
		CodeFoldTitle:  block.CodeFoldTitle,
		ExtractedURLs:  []string(block.ExtractedURLs),
		Companies:      []string(block.Companies),
		IsActive:       block.IsActive,
		CreatedAt:      block.CreatedAt,
		UpdatedAt:      block.UpdatedAt,
	}

	if block.File.ID != "" {
		fileResponse := ContentFileToResponse(&block.File)
		response.File = &fileResponse
	}

	if len(block.UserProgress) > 0 {
		progress := &block.UserProgress[0]
		response.Progress = &UserContentProgressResponse{
			ID:             progress.ID,
			UserID:         progress.UserID,
			ContentBlockID: progress.ContentBlockID,
			SolvedCount:    progress.SolvedCount,
			IsCompleted:    progress.IsCompleted,
			LastAccessedAt: progress.LastAccessedAt,
			CreatedAt:      progress.CreatedAt,
			UpdatedAt:      progress.UpdatedAt,
		}
	}

	return response
}

func TheoryCardToResponse(card *entities.TheoryCard) TheoryCardResponse {
	response := TheoryCardResponse{
		ID:              card.ID,
		Title:           card.Title,
		Question:        card.Question,
		Answer:          card.Answer,
		Category:        card.Category,
		SubCategory:     card.SubCategory,
		DifficultyLevel: card.DifficultyLevel,
		Tags:            []string(card.Tags),
		IsActive:        card.IsActive,
		CreatedByID:     card.CreatedByID,
		CreatedAt:       card.CreatedAt,
		UpdatedAt:       card.UpdatedAt,
	}

	if card.CreatedBy.ID != 0 {
		response.CreatedBy = &UserResponse{
			ID:                  card.CreatedBy.ID,
			Username:            card.CreatedBy.Username,
			Email:               card.CreatedBy.Email,
			Role:                card.CreatedBy.Role,
			FirstName:           card.CreatedBy.FirstName,
			LastName:            card.CreatedBy.LastName,
			ProfilePicture:      card.CreatedBy.ProfilePicture,
			TotalTasksCompleted: card.CreatedBy.TotalTasksCompleted,
			TotalPointsEarned:   card.CreatedBy.TotalPointsEarned,
			CurrentStreak:       card.CreatedBy.CurrentStreak,
		}
	}

	if len(card.UserProgress) > 0 {
		progress := &card.UserProgress[0]
		response.Progress = &UserTheoryProgressResponse{
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
	}

	return response
}