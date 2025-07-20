package dto

import (
	"nareshka-backend/app/shared/types"
)

type ExecuteCodeRequest struct {
	Code        string             `json:"code" binding:"required"`
	Language    types.LanguageType `json:"language" binding:"required"`
	Input       string             `json:"input"`
	TimeLimit   int                `json:"time_limit,omitempty"`
	MemoryLimit int                `json:"memory_limit,omitempty"`
}

type ValidateTaskRequest struct {
	TaskID   uint               `json:"task_id" binding:"required"`
	Code     string             `json:"code" binding:"required"`
	Language types.LanguageType `json:"language" binding:"required"`
}