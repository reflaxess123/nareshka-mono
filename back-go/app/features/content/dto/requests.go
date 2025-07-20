package dto

import "nareshka-backend/app/shared/types"

type ContentBlockFilterRequest struct {
	Category        string                  `form:"category"`
	SubCategory     string                  `form:"sub_category"`
	FileID          string                  `form:"file_id"`
	DifficultyLevel *types.DifficultyLevel  `form:"difficulty_level"`
	Search          string                  `form:"search"`
	Level           *int                    `form:"level"`
	MinOrder        *int                    `form:"min_order"`
	MaxOrder        *int                    `form:"max_order"`
	Page            int                     `form:"page,default=1"`
	Limit           int                     `form:"limit,default=20"`
	SortBy          string                  `form:"sort_by,default=order_in_file"`
	SortDir         string                  `form:"sort_dir,default=asc"`
}

type ContentFileFilterRequest struct {
	MainCategory string `form:"main_category"`
	SubCategory  string `form:"sub_category"`
	Search       string `form:"search"`
	Page         int    `form:"page,default=1"`
	Limit        int    `form:"limit,default=20"`
	SortBy       string `form:"sort_by,default=created_at"`
	SortDir      string `form:"sort_dir,default=desc"`
}

type UpdateProgressRequest struct {
	Increment bool `json:"increment" binding:"required"`
}

type CreateTheoryCardRequest struct {
	Title           string                  `json:"title" binding:"required,max=500"`
	Question        string                  `json:"question" binding:"required"`
	Answer          string                  `json:"answer" binding:"required"`
	Category        string                  `json:"category" binding:"required,max=100"`
	SubCategory     string                  `json:"sub_category" binding:"max=100"`
	DifficultyLevel types.DifficultyLevel   `json:"difficulty_level" binding:"required"`
	Tags            []string                `json:"tags"`
}

type UpdateTheoryCardRequest struct {
	Title           *string                 `json:"title,omitempty"`
	Question        *string                 `json:"question,omitempty"`
	Answer          *string                 `json:"answer,omitempty"`
	Category        *string                 `json:"category,omitempty"`
	SubCategory     *string                 `json:"sub_category,omitempty"`
	DifficultyLevel *types.DifficultyLevel  `json:"difficulty_level,omitempty"`
	Tags            []string                `json:"tags,omitempty"`
	IsActive        *bool                   `json:"is_active,omitempty"`
}

type TheoryCardFilterRequest struct {
	Category        string                  `form:"category"`
	SubCategory     string                  `form:"sub_category"`
	DifficultyLevel *types.DifficultyLevel  `form:"difficulty_level"`
	Tags            []string                `form:"tags"`
	CreatedBy       *uint                   `form:"created_by"`
	Page            int                     `form:"page,default=1"`
	Limit           int                     `form:"limit,default=20"`
	SortBy          string                  `form:"sort_by,default=created_at"`
	SortDir         string                  `form:"sort_dir,default=desc"`
}

type ReviewTheoryCardRequest struct {
	Answer types.ReviewAnswer `json:"answer" binding:"required"`
}