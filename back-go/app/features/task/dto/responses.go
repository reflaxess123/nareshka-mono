package dto

import (
	"time"
	"nareshka-backend/app/shared/entities"
	"nareshka-backend/app/shared/types"
)

type TaskResponse struct {
	ID                    uint                    `json:"id"`
	Title                 string                  `json:"title"`
	Description           string                  `json:"description"`
	Content               string                  `json:"content"`
	DifficultyLevel       types.DifficultyLevel   `json:"difficulty_level"`
	Category              string                  `json:"category"`
	Tags                  []string                `json:"tags"`
	Points                int                     `json:"points"`
	TimeLimit             *int                    `json:"time_limit"`
	MemoryLimit           *int                    `json:"memory_limit"`
	SupportedLanguages    []string                `json:"supported_languages"`
	InitialCode           map[string]string       `json:"initial_code"`
	SolutionTemplate      map[string]string       `json:"solution_template"`
	IsPublic              bool                    `json:"is_public"`
	IsActive              bool                    `json:"is_active"`
	Order                 int                     `json:"order"`
	CreatedByID           uint                    `json:"created_by_id"`
	CreatedBy             *UserResponse           `json:"created_by,omitempty"`
	TestCases             []TestCaseResponse      `json:"test_cases,omitempty"`
	CreatedAt             time.Time               `json:"created_at"`
	UpdatedAt             time.Time               `json:"updated_at"`
}

type TaskListResponse struct {
	Tasks      []TaskResponse `json:"tasks"`
	Total      int64          `json:"total"`
	Page       int            `json:"page"`
	Limit      int            `json:"limit"`
	TotalPages int            `json:"total_pages"`
}

type TestCaseResponse struct {
	ID             uint      `json:"id"`
	TaskID         uint      `json:"task_id"`
	Input          string    `json:"input"`
	ExpectedOutput string    `json:"expected_output"`
	IsPublic       bool      `json:"is_public"`
	IsActive       bool      `json:"is_active"`
	Order          int       `json:"order"`
	TimeLimit      *int      `json:"time_limit"`
	MemoryLimit    *int      `json:"memory_limit"`
	CreatedAt      time.Time `json:"created_at"`
	UpdatedAt      time.Time `json:"updated_at"`
}

type TaskAttemptResponse struct {
	ID            uint                `json:"id"`
	TaskID        uint                `json:"task_id"`
	Task          *TaskResponse       `json:"task,omitempty"`
	UserID        uint                `json:"user_id"`
	User          *UserResponse       `json:"user,omitempty"`
	Language      types.LanguageType  `json:"language"`
	Code          string              `json:"code"`
	Status        types.TaskStatus    `json:"status"`
	Score         *int                `json:"score"`
	ExecutionTime *int                `json:"execution_time"`
	MemoryUsed    *int                `json:"memory_used"`
	TestsPassed   int                 `json:"tests_passed"`
	TestsFailed   int                 `json:"tests_failed"`
	ErrorMessage  *string             `json:"error_message"`
	Output        *string             `json:"output"`
	CreatedAt     time.Time           `json:"created_at"`
	UpdatedAt     time.Time           `json:"updated_at"`
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

func TaskToResponse(task *entities.Task) TaskResponse {
	response := TaskResponse{
		ID:                 task.ID,
		Title:              task.Title,
		Description:        task.Description,
		Content:            task.Content,
		DifficultyLevel:    task.DifficultyLevel,
		Category:           task.Category,
		Tags:               task.Tags,
		Points:             task.Points,
		TimeLimit:          task.TimeLimit,
		MemoryLimit:        task.MemoryLimit,
		SupportedLanguages: task.SupportedLanguages,
		InitialCode:        task.InitialCode,
		SolutionTemplate:   task.SolutionTemplate,
		IsPublic:           task.IsPublic,
		IsActive:           task.IsActive,
		Order:              task.Order,
		CreatedByID:        task.CreatedByID,
		CreatedAt:          task.CreatedAt,
		UpdatedAt:          task.UpdatedAt,
	}

	if task.CreatedBy.ID != 0 {
		response.CreatedBy = &UserResponse{
			ID:                  task.CreatedBy.ID,
			Username:            task.CreatedBy.Username,
			Email:               task.CreatedBy.Email,
			Role:                task.CreatedBy.Role,
			FirstName:           task.CreatedBy.FirstName,
			LastName:            task.CreatedBy.LastName,
			ProfilePicture:      task.CreatedBy.ProfilePicture,
			TotalTasksCompleted: task.CreatedBy.TotalTasksCompleted,
			TotalPointsEarned:   task.CreatedBy.TotalPointsEarned,
			CurrentStreak:       task.CreatedBy.CurrentStreak,
		}
	}

	for _, testCase := range task.TestCases {
		response.TestCases = append(response.TestCases, TestCaseResponse{
			ID:             testCase.ID,
			TaskID:         testCase.TaskID,
			Input:          testCase.Input,
			ExpectedOutput: testCase.ExpectedOutput,
			IsPublic:       testCase.IsPublic,
			IsActive:       testCase.IsActive,
			Order:          testCase.Order,
			TimeLimit:      testCase.TimeLimit,
			MemoryLimit:    testCase.MemoryLimit,
			CreatedAt:      testCase.CreatedAt,
			UpdatedAt:      testCase.UpdatedAt,
		})
	}

	return response
}