package dto

type ExecuteCodeResponse struct {
	Output        string `json:"output"`
	Error         string `json:"error,omitempty"`
	ExecutionTime int    `json:"execution_time"`
	MemoryUsed    int    `json:"memory_used"`
	Status        string `json:"status"`
	ExitCode      int    `json:"exit_code"`
}

type ValidateTaskResponse struct {
	Success      bool                    `json:"success"`
	Score        int                     `json:"score"`
	TestsPassed  int                     `json:"tests_passed"`
	TestsFailed  int                     `json:"tests_failed"`
	TotalTests   int                     `json:"total_tests"`
	TestResults  []TestCaseResult        `json:"test_results"`
	ExecutionTime int                    `json:"execution_time"`
	MemoryUsed   int                     `json:"memory_used"`
	ErrorMessage string                  `json:"error_message,omitempty"`
}

type TestCaseResult struct {
	ID             uint   `json:"id"`
	Input          string `json:"input"`
	ExpectedOutput string `json:"expected_output"`
	ActualOutput   string `json:"actual_output"`
	Passed         bool   `json:"passed"`
	ExecutionTime  int    `json:"execution_time"`
	MemoryUsed     int    `json:"memory_used"`
	Error          string `json:"error,omitempty"`
}

type LanguageConfig struct {
	Name           string `json:"name"`
	Version        string `json:"version"`
	FileExtension  string `json:"file_extension"`
	CompileCommand string `json:"compile_command,omitempty"`
	RunCommand     string `json:"run_command"`
	DockerImage    string `json:"docker_image"`
	TimeLimit      int    `json:"time_limit"`
	MemoryLimit    int    `json:"memory_limit"`
}