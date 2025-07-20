package services

import (
	"bytes"
	"context"
	"fmt"
	"os"
	"os/exec"
	"path/filepath"
	"strings"
	"time"
	"nareshka-backend/app/shared/types"
	"nareshka-backend/app/features/code_editor/dto"
)

type CodeExecutorService struct {
	workDir string
}

func NewCodeExecutorService() *CodeExecutorService {
	workDir := "/tmp/nareshka-code-execution"
	os.MkdirAll(workDir, 0755)
	return &CodeExecutorService{
		workDir: workDir,
	}
}

func (e *CodeExecutorService) Execute(req *dto.ExecuteCodeRequest) (*dto.ExecuteCodeResponse, error) {
	config := e.getLanguageConfig(req.Language)
	if config == nil {
		return nil, fmt.Errorf("unsupported language: %s", req.Language)
	}

	// Create temporary directory for this execution
	execDir := filepath.Join(e.workDir, fmt.Sprintf("exec_%d", time.Now().UnixNano()))
	if err := os.MkdirAll(execDir, 0755); err != nil {
		return nil, fmt.Errorf("failed to create execution directory: %w", err)
	}
	defer os.RemoveAll(execDir)

	// Write code to file
	codeFile := filepath.Join(execDir, "code"+config.FileExtension)
	if err := os.WriteFile(codeFile, []byte(req.Code), 0644); err != nil {
		return nil, fmt.Errorf("failed to write code file: %w", err)
	}

	// Write input to file if provided
	inputFile := filepath.Join(execDir, "input.txt")
	if req.Input != "" {
		if err := os.WriteFile(inputFile, []byte(req.Input), 0644); err != nil {
			return nil, fmt.Errorf("failed to write input file: %w", err)
		}
	}

	// Set timeouts
	timeLimit := req.TimeLimit
	if timeLimit <= 0 {
		timeLimit = config.TimeLimit
	}

	// Execute in Docker container
	response := e.executeInDocker(config, execDir, codeFile, inputFile, timeLimit)
	return response, nil
}

func (e *CodeExecutorService) executeInDocker(config *dto.LanguageConfig, execDir, codeFile, inputFile string, timeLimit int) *dto.ExecuteCodeResponse {
	ctx, cancel := context.WithTimeout(context.Background(), time.Duration(timeLimit)*time.Second)
	defer cancel()

	// Prepare Docker command
	dockerCmd := []string{
		"docker", "run", "--rm",
		"--network", "none", // No network access
		"--memory", "256m",   // Memory limit
		"--cpus", "0.5",      // CPU limit
		"-v", fmt.Sprintf("%s:/workspace", execDir),
		"-w", "/workspace",
		config.DockerImage,
	}

	// Add compilation step if needed
	if config.CompileCommand != "" {
		compileCmd := strings.ReplaceAll(config.CompileCommand, "{file}", "code"+config.FileExtension)
		dockerCmd = append(dockerCmd, "sh", "-c", compileCmd+" && "+config.RunCommand)
	} else {
		runCmd := strings.ReplaceAll(config.RunCommand, "{file}", "code"+config.FileExtension)
		dockerCmd = append(dockerCmd, "sh", "-c", runCmd)
	}

	// Execute
	startTime := time.Now()
	cmd := exec.CommandContext(ctx, dockerCmd[0], dockerCmd[1:]...)
	
	// Set input if provided
	if inputFile != "" && fileExists(inputFile) {
		cmd.Stdin = strings.NewReader(readFile(inputFile))
	}

	var stdout, stderr bytes.Buffer
	cmd.Stdout = &stdout
	cmd.Stderr = &stderr

	err := cmd.Run()
	executionTime := int(time.Since(startTime).Milliseconds())

	response := &dto.ExecuteCodeResponse{
		Output:        stdout.String(),
		ExecutionTime: executionTime,
		MemoryUsed:    0, // TODO: Get actual memory usage
	}

	if err != nil {
		response.Error = stderr.String()
		response.Status = "error"
		if ctx.Err() == context.DeadlineExceeded {
			response.Error = "Time limit exceeded"
			response.Status = "timeout"
		}
		response.ExitCode = 1
	} else {
		response.Status = "success"
		response.ExitCode = 0
	}

	return response
}

func (e *CodeExecutorService) getLanguageConfig(lang types.LanguageType) *dto.LanguageConfig {
	configs := map[types.LanguageType]*dto.LanguageConfig{
		types.LanguagePython: {
			Name:          "Python",
			Version:       "3.11",
			FileExtension: ".py",
			RunCommand:    "python3 {file}",
			DockerImage:   "python:3.11-alpine",
			TimeLimit:     10,
			MemoryLimit:   256,
		},
		types.LanguageJavaScript: {
			Name:          "Node.js",
			Version:       "20",
			FileExtension: ".js",
			RunCommand:    "node {file}",
			DockerImage:   "node:20-alpine",
			TimeLimit:     10,
			MemoryLimit:   256,
		},
		types.LanguageJava: {
			Name:           "Java",
			Version:        "17",
			FileExtension:  ".java",
			CompileCommand: "javac {file}",
			RunCommand:     "java -cp . Main",
			DockerImage:    "openjdk:17-alpine",
			TimeLimit:      15,
			MemoryLimit:    512,
		},
		types.LanguageCPP: {
			Name:           "C++",
			Version:        "11",
			FileExtension:  ".cpp",
			CompileCommand: "g++ -o program {file}",
			RunCommand:     "./program",
			DockerImage:    "gcc:11-alpine",
			TimeLimit:      10,
			MemoryLimit:    256,
		},
		types.LanguageGo: {
			Name:          "Go",
			Version:       "1.21",
			FileExtension: ".go",
			RunCommand:    "go run {file}",
			DockerImage:   "golang:1.21-alpine",
			TimeLimit:     10,
			MemoryLimit:   256,
		},
		types.LanguageRust: {
			Name:           "Rust",
			Version:        "1.70",
			FileExtension:  ".rs",
			CompileCommand: "rustc -o program {file}",
			RunCommand:     "./program",
			DockerImage:    "rust:1.70-alpine",
			TimeLimit:      15,
			MemoryLimit:    256,
		},
	}

	return configs[lang]
}

func (e *CodeExecutorService) GetSupportedLanguages() []dto.LanguageConfig {
	languages := []dto.LanguageConfig{}
	for lang := range map[types.LanguageType]bool{
		types.LanguagePython:     true,
		types.LanguageJavaScript: true,
		types.LanguageJava:       true,
		types.LanguageCPP:        true,
		types.LanguageGo:         true,
		types.LanguageRust:       true,
	} {
		if config := e.getLanguageConfig(lang); config != nil {
			languages = append(languages, *config)
		}
	}
	return languages
}

func fileExists(path string) bool {
	_, err := os.Stat(path)
	return !os.IsNotExist(err)
}

func readFile(path string) string {
	content, err := os.ReadFile(path)
	if err != nil {
		return ""
	}
	return string(content)
}