package services

import (
	"fmt"
	"strings"
	"nareshka-backend/app/shared/entities"
	"nareshka-backend/app/shared/types"
	"nareshka-backend/app/features/code_editor/dto"
	"gorm.io/gorm"
)

type CodeEditorService struct {
	db       *gorm.DB
	executor *CodeExecutorService
}

func NewCodeEditorService(db *gorm.DB) *CodeEditorService {
	return &CodeEditorService{
		db:       db,
		executor: NewCodeExecutorService(),
	}
}

func (s *CodeEditorService) ExecuteCode(req *dto.ExecuteCodeRequest) (*dto.ExecuteCodeResponse, error) {
	return s.executor.Execute(req)
}

func (s *CodeEditorService) ValidateTask(userID uint, req *dto.ValidateTaskRequest) (*dto.ValidateTaskResponse, error) {
	// Get task and test cases
	var task entities.Task
	if err := s.db.Preload("TestCases").First(&task, req.TaskID).Error; err != nil {
		return nil, fmt.Errorf("task not found: %w", err)
	}

	// Check if language is supported for this task
	if !s.isLanguageSupported(task, req.Language) {
		return nil, fmt.Errorf("language %s is not supported for this task", req.Language)
	}

	response := &dto.ValidateTaskResponse{
		TestResults: []dto.TestCaseResult{},
	}

	var totalExecutionTime int
	var totalMemoryUsed int
	testsPassed := 0
	testsFailed := 0

	// Run each test case
	for _, testCase := range task.TestCases {
		if !testCase.IsActive {
			continue
		}

		result := s.runTestCase(req, &testCase)
		response.TestResults = append(response.TestResults, result)

		totalExecutionTime += result.ExecutionTime
		totalMemoryUsed += result.MemoryUsed

		if result.Passed {
			testsPassed++
		} else {
			testsFailed++
		}
	}

	response.TestsPassed = testsPassed
	response.TestsFailed = testsFailed
	response.TotalTests = testsPassed + testsFailed
	response.ExecutionTime = totalExecutionTime
	response.MemoryUsed = totalMemoryUsed
	response.Success = testsFailed == 0 && testsPassed > 0

	// Calculate score
	if response.TotalTests > 0 {
		response.Score = (testsPassed * 100) / response.TotalTests
	}

	// Save task attempt to database
	attempt := &entities.TaskAttempt{
		TaskID:        req.TaskID,
		UserID:        userID,
		Language:      req.Language,
		Code:          req.Code,
		Status:        s.getTaskStatus(response.Success),
		TestsPassed:   response.TestsPassed,
		TestsFailed:   response.TestsFailed,
		ExecutionTime: &response.ExecutionTime,
		MemoryUsed:    &response.MemoryUsed,
	}

	if response.Success {
		attempt.Score = &response.Score
	} else if len(response.TestResults) > 0 && response.TestResults[0].Error != "" {
		attempt.ErrorMessage = &response.TestResults[0].Error
	}

	if err := s.db.Create(attempt).Error; err != nil {
		return nil, fmt.Errorf("failed to save task attempt: %w", err)
	}

	// Update user progress if task completed successfully
	if response.Success {
		if err := s.updateUserProgress(userID, req.TaskID); err != nil {
			fmt.Printf("Failed to update user progress: %v\n", err)
		}
	}

	return response, nil
}

func (s *CodeEditorService) runTestCase(req *dto.ValidateTaskRequest, testCase *entities.TestCase) dto.TestCaseResult {
	result := dto.TestCaseResult{
		ID:             testCase.ID,
		Input:          testCase.Input,
		ExpectedOutput: testCase.ExpectedOutput,
	}

	// Execute code with test case input
	execReq := &dto.ExecuteCodeRequest{
		Code:        req.Code,
		Language:    req.Language,
		Input:       testCase.Input,
		TimeLimit:   10,
		MemoryLimit: 256,
	}

	if testCase.TimeLimit != nil {
		execReq.TimeLimit = *testCase.TimeLimit
	}
	if testCase.MemoryLimit != nil {
		execReq.MemoryLimit = *testCase.MemoryLimit
	}

	execResp, err := s.executor.Execute(execReq)
	if err != nil {
		result.Error = err.Error()
		result.Passed = false
		return result
	}

	result.ActualOutput = strings.TrimSpace(execResp.Output)
	result.ExecutionTime = execResp.ExecutionTime
	result.MemoryUsed = execResp.MemoryUsed

	if execResp.Status != "success" {
		result.Error = execResp.Error
		result.Passed = false
		return result
	}

	expectedOutput := strings.TrimSpace(testCase.ExpectedOutput)
	result.Passed = expectedOutput == result.ActualOutput

	return result
}

func (s *CodeEditorService) GetSupportedLanguages() []dto.LanguageConfig {
	return s.executor.GetSupportedLanguages()
}

func (s *CodeEditorService) isLanguageSupported(task entities.Task, language types.LanguageType) bool {
	if len(task.SupportedLanguages) == 0 {
		return true
	}

	for _, lang := range task.SupportedLanguages {
		if lang == string(language) {
			return true
		}
	}
	return false
}

func (s *CodeEditorService) getTaskStatus(success bool) types.TaskStatus {
	if success {
		return types.TaskStatusCompleted
	}
	return types.TaskStatusRejected
}

func (s *CodeEditorService) updateUserProgress(userID uint, taskID uint) error {
	var task entities.Task
	if err := s.db.First(&task, taskID).Error; err != nil {
		return err
	}

	updates := map[string]interface{}{
		"total_tasks_completed": gorm.Expr("total_tasks_completed + 1"),
		"total_points_earned":   gorm.Expr("total_points_earned + ?", task.Points),
	}

	return s.db.Model(&entities.User{}).Where("id = ?", userID).Updates(updates).Error
}