package services

import (
	"fmt"
	"math"
	"nareshka-backend/app/shared/entities"
	"nareshka-backend/app/features/task/dto"

	"gorm.io/gorm"
)

type TaskService struct {
	db *gorm.DB
}

func NewTaskService(db *gorm.DB) *TaskService {
	return &TaskService{
		db: db,
	}
}

func (s *TaskService) CreateTask(userID uint, req *dto.CreateTaskRequest) (*dto.TaskResponse, error) {
	task := &entities.Task{
		Title:              req.Title,
		Description:        req.Description,
		Content:            req.Content,
		DifficultyLevel:    req.DifficultyLevel,
		Category:           req.Category,
		Tags:               req.Tags,
		Points:             req.Points,
		TimeLimit:          req.TimeLimit,
		MemoryLimit:        req.MemoryLimit,
		SupportedLanguages: req.SupportedLanguages,
		InitialCode:        req.InitialCode,
		SolutionTemplate:   req.SolutionTemplate,
		IsPublic:           req.IsPublic,
		IsActive:           true,
		CreatedByID:        userID,
	}

	if err := s.db.Create(task).Error; err != nil {
		return nil, fmt.Errorf("failed to create task: %w", err)
	}

	// Load created task with relations
	if err := s.db.Preload("CreatedBy").First(task, task.ID).Error; err != nil {
		return nil, fmt.Errorf("failed to load created task: %w", err)
	}

	response := dto.TaskToResponse(task)
	return &response, nil
}

func (s *TaskService) GetTask(id uint, userID *uint) (*dto.TaskResponse, error) {
	var task entities.Task
	query := s.db.Preload("CreatedBy").Preload("TestCases", func(db *gorm.DB) *gorm.DB {
		if userID == nil {
			// Public test cases only for non-authenticated users
			return db.Where("is_public = ? AND is_active = ?", true, true)
		}
		// All active test cases for authenticated users
		return db.Where("is_active = ?", true)
	})

	if err := query.First(&task, id).Error; err != nil {
		if err == gorm.ErrRecordNotFound {
			return nil, fmt.Errorf("task not found")
		}
		return nil, fmt.Errorf("failed to get task: %w", err)
	}

	// Check if task is public or user is creator
	if !task.IsPublic && (userID == nil || *userID != task.CreatedByID) {
		return nil, fmt.Errorf("task not found")
	}

	response := dto.TaskToResponse(&task)
	return &response, nil
}

func (s *TaskService) GetTasks(req *dto.TaskFilterRequest, userID *uint) (*dto.TaskListResponse, error) {
	var tasks []entities.Task
	var total int64

	query := s.db.Model(&entities.Task{}).Where("is_active = ?", true)

	// Apply filters
	if req.DifficultyLevel != nil {
		query = query.Where("difficulty_level = ?", *req.DifficultyLevel)
	}
	if req.Category != "" {
		query = query.Where("category = ?", req.Category)
	}
	if len(req.Tags) > 0 {
		query = query.Where("tags && ?", req.Tags)
	}
	if req.CreatedBy != nil {
		query = query.Where("created_by_id = ?", *req.CreatedBy)
	}

	// Public tasks filter
	if userID == nil {
		query = query.Where("is_public = ?", true)
	} else if req.IsPublic != nil {
		query = query.Where("is_public = ?", *req.IsPublic)
	}

	// Get total count
	if err := query.Count(&total).Error; err != nil {
		return nil, fmt.Errorf("failed to count tasks: %w", err)
	}

	// Apply pagination
	offset := (req.Page - 1) * req.Limit
	query = query.Offset(offset).Limit(req.Limit).Order("created_at DESC")

	// Load tasks with relations
	if err := query.Preload("CreatedBy").Find(&tasks).Error; err != nil {
		return nil, fmt.Errorf("failed to get tasks: %w", err)
	}

	// Convert to response
	taskResponses := make([]dto.TaskResponse, len(tasks))
	for i, task := range tasks {
		taskResponses[i] = dto.TaskToResponse(&task)
	}

	totalPages := int(math.Ceil(float64(total) / float64(req.Limit)))

	return &dto.TaskListResponse{
		Tasks:      taskResponses,
		Total:      total,
		Page:       req.Page,
		Limit:      req.Limit,
		TotalPages: totalPages,
	}, nil
}

func (s *TaskService) UpdateTask(id uint, userID uint, req *dto.UpdateTaskRequest) (*dto.TaskResponse, error) {
	var task entities.Task
	if err := s.db.First(&task, id).Error; err != nil {
		if err == gorm.ErrRecordNotFound {
			return nil, fmt.Errorf("task not found")
		}
		return nil, fmt.Errorf("failed to get task: %w", err)
	}

	// Check if user is creator (or admin in future)
	if task.CreatedByID != userID {
		return nil, fmt.Errorf("permission denied")
	}

	// Update fields
	updates := make(map[string]interface{})
	if req.Title != nil {
		updates["title"] = *req.Title
	}
	if req.Description != nil {
		updates["description"] = *req.Description
	}
	if req.Content != nil {
		updates["content"] = *req.Content
	}
	if req.DifficultyLevel != nil {
		updates["difficulty_level"] = *req.DifficultyLevel
	}
	if req.Category != nil {
		updates["category"] = *req.Category
	}
	if req.Tags != nil {
		updates["tags"] = req.Tags
	}
	if req.Points != nil {
		updates["points"] = *req.Points
	}
	if req.TimeLimit != nil {
		updates["time_limit"] = req.TimeLimit
	}
	if req.MemoryLimit != nil {
		updates["memory_limit"] = req.MemoryLimit
	}
	if req.SupportedLanguages != nil {
		updates["supported_languages"] = req.SupportedLanguages
	}
	if req.InitialCode != nil {
		updates["initial_code"] = req.InitialCode
	}
	if req.SolutionTemplate != nil {
		updates["solution_template"] = req.SolutionTemplate
	}
	if req.IsPublic != nil {
		updates["is_public"] = *req.IsPublic
	}
	if req.IsActive != nil {
		updates["is_active"] = *req.IsActive
	}

	if err := s.db.Model(&task).Updates(updates).Error; err != nil {
		return nil, fmt.Errorf("failed to update task: %w", err)
	}

	// Load updated task
	if err := s.db.Preload("CreatedBy").First(&task, id).Error; err != nil {
		return nil, fmt.Errorf("failed to load updated task: %w", err)
	}

	response := dto.TaskToResponse(&task)
	return &response, nil
}

func (s *TaskService) DeleteTask(id uint, userID uint) error {
	var task entities.Task
	if err := s.db.First(&task, id).Error; err != nil {
		if err == gorm.ErrRecordNotFound {
			return fmt.Errorf("task not found")
		}
		return fmt.Errorf("failed to get task: %w", err)
	}

	// Check if user is creator (or admin in future)
	if task.CreatedByID != userID {
		return fmt.Errorf("permission denied")
	}

	// Soft delete
	if err := s.db.Delete(&task).Error; err != nil {
		return fmt.Errorf("failed to delete task: %w", err)
	}

	return nil
}

func (s *TaskService) CreateTestCase(userID uint, req *dto.CreateTestCaseRequest) (*dto.TestCaseResponse, error) {
	// Check if user owns the task
	var task entities.Task
	if err := s.db.First(&task, req.TaskID).Error; err != nil {
		if err == gorm.ErrRecordNotFound {
			return nil, fmt.Errorf("task not found")
		}
		return nil, fmt.Errorf("failed to get task: %w", err)
	}

	if task.CreatedByID != userID {
		return nil, fmt.Errorf("permission denied")
	}

	testCase := &entities.TestCase{
		TaskID:         req.TaskID,
		Input:          req.Input,
		ExpectedOutput: req.ExpectedOutput,
		IsPublic:       req.IsPublic,
		IsActive:       true,
		Order:          req.Order,
		TimeLimit:      req.TimeLimit,
		MemoryLimit:    req.MemoryLimit,
	}

	if err := s.db.Create(testCase).Error; err != nil {
		return nil, fmt.Errorf("failed to create test case: %w", err)
	}

	return &dto.TestCaseResponse{
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
	}, nil
}