package dto

import "nareshka-backend/app/shared/types"

type CreateTaskRequest struct {
	Title              string                  `json:"title" binding:"required,max=200"`
	Description        string                  `json:"description"`
	Content            string                  `json:"content"`
	DifficultyLevel    types.DifficultyLevel   `json:"difficulty_level" binding:"required"`
	Category           string                  `json:"category"`
	Tags               []string                `json:"tags"`
	Points             int                     `json:"points"`
	TimeLimit          *int                    `json:"time_limit"`
	MemoryLimit        *int                    `json:"memory_limit"`
	SupportedLanguages []string                `json:"supported_languages"`
	InitialCode        map[string]string       `json:"initial_code"`
	SolutionTemplate   map[string]string       `json:"solution_template"`
	IsPublic           bool                    `json:"is_public"`
}

type UpdateTaskRequest struct {
	Title              *string                 `json:"title,omitempty"`
	Description        *string                 `json:"description,omitempty"`
	Content            *string                 `json:"content,omitempty"`
	DifficultyLevel    *types.DifficultyLevel  `json:"difficulty_level,omitempty"`
	Category           *string                 `json:"category,omitempty"`
	Tags               []string                `json:"tags,omitempty"`
	Points             *int                    `json:"points,omitempty"`
	TimeLimit          *int                    `json:"time_limit,omitempty"`
	MemoryLimit        *int                    `json:"memory_limit,omitempty"`
	SupportedLanguages []string                `json:"supported_languages,omitempty"`
	InitialCode        map[string]string       `json:"initial_code,omitempty"`
	SolutionTemplate   map[string]string       `json:"solution_template,omitempty"`
	IsPublic           *bool                   `json:"is_public,omitempty"`
	IsActive           *bool                   `json:"is_active,omitempty"`
}

type TaskFilterRequest struct {
	DifficultyLevel *types.DifficultyLevel `form:"difficulty_level"`
	Category        string                 `form:"category"`
	Tags            []string               `form:"tags"`
	IsPublic        *bool                  `form:"is_public"`
	CreatedBy       *uint                  `form:"created_by"`
	Page            int                    `form:"page,default=1"`
	Limit           int                    `form:"limit,default=20"`
}

type CreateTestCaseRequest struct {
	TaskID         uint   `json:"task_id" binding:"required"`
	Input          string `json:"input"`
	ExpectedOutput string `json:"expected_output" binding:"required"`
	IsPublic       bool   `json:"is_public"`
	Order          int    `json:"order"`
	TimeLimit      *int   `json:"time_limit"`
	MemoryLimit    *int   `json:"memory_limit"`
}

type UpdateTestCaseRequest struct {
	Input          *string `json:"input,omitempty"`
	ExpectedOutput *string `json:"expected_output,omitempty"`
	IsPublic       *bool   `json:"is_public,omitempty"`
	IsActive       *bool   `json:"is_active,omitempty"`
	Order          *int    `json:"order,omitempty"`
	TimeLimit      *int    `json:"time_limit,omitempty"`
	MemoryLimit    *int    `json:"memory_limit,omitempty"`
}