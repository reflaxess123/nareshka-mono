from abc import ABC, abstractmethod
from typing import List, Optional, Dict, Any
from datetime import datetime

from ..entities.code_editor import (
    SupportedLanguage,
    CodeExecution,
    UserCodeSolution,
    TestCaseExecution,
    ValidationResult,
    ExecutionStats
)
from ..entities.progress import TestCase
from ..entities.enums import CodeLanguage, ExecutionStatus


class CodeEditorRepository(ABC):
    """Repository для работы с выполнением кода и решениями"""
    
    # SupportedLanguage methods
    @abstractmethod
    async def get_supported_languages(self) -> List[SupportedLanguage]:
        pass
    
    @abstractmethod
    async def get_language_by_id(self, language_id: str) -> Optional[SupportedLanguage]:
        pass
    
    @abstractmethod
    async def get_language_by_enum(self, language: CodeLanguage) -> Optional[SupportedLanguage]:
        pass
    
    # CodeExecution methods
    @abstractmethod
    async def create_code_execution(self, execution: CodeExecution) -> CodeExecution:
        pass
    
    @abstractmethod
    async def update_code_execution(self, execution: CodeExecution) -> CodeExecution:
        pass
    
    @abstractmethod
    async def get_execution_by_id(self, execution_id: str) -> Optional[CodeExecution]:
        pass
    
    @abstractmethod
    async def get_user_executions(self, user_id: int, block_id: Optional[str] = None, limit: int = 20, offset: int = 0) -> List[CodeExecution]:
        pass
    
    @abstractmethod
    async def get_execution_by_id_and_user(self, execution_id: str, user_id: Optional[int]) -> Optional[CodeExecution]:
        pass
    
    # UserCodeSolution methods
    @abstractmethod
    async def create_user_solution(self, solution: UserCodeSolution) -> UserCodeSolution:
        pass
    
    @abstractmethod
    async def update_user_solution(self, solution: UserCodeSolution) -> UserCodeSolution:
        pass
    
    @abstractmethod
    async def get_solution_by_id(self, solution_id: str) -> Optional[UserCodeSolution]:
        pass
    
    @abstractmethod
    async def get_solution_by_user_and_block(self, user_id: int, block_id: str, language_id: str) -> Optional[UserCodeSolution]:
        pass
    
    @abstractmethod
    async def get_user_solutions_for_block(self, user_id: int, block_id: str) -> List[UserCodeSolution]:
        pass
    
    @abstractmethod
    async def get_solution_by_id_and_user(self, solution_id: str, user_id: int) -> Optional[UserCodeSolution]:
        pass
    
    # TestCase methods (reuse from progress module)
    @abstractmethod
    async def get_test_cases_for_block(self, block_id: str) -> List[TestCase]:
        pass
    
    @abstractmethod
    async def get_public_test_cases_for_block(self, block_id: str) -> List[TestCase]:
        pass
    
    @abstractmethod
    async def create_test_case(self, test_case: TestCase) -> TestCase:
        pass
    
    @abstractmethod
    async def update_test_case_stats(self, test_case_id: str, execution_count: int, pass_rate: float) -> None:
        pass
    
    # Content methods (for fallback test cases)
    @abstractmethod
    async def get_content_block_by_id(self, block_id: str) -> Optional[Dict[str, Any]]:
        pass
    
    # Statistics methods
    @abstractmethod
    async def get_execution_stats(self, user_id: int) -> ExecutionStats:
        pass
    
    @abstractmethod
    async def get_execution_count_by_user(self, user_id: int) -> int:
        pass
    
    @abstractmethod
    async def get_successful_execution_count_by_user(self, user_id: int) -> int:
        pass
    
    @abstractmethod
    async def get_average_execution_time(self, user_id: int) -> float:
        pass
    
    @abstractmethod
    async def get_language_stats_by_user(self, user_id: int) -> List[Dict[str, Any]]:
        pass
    
    # Validation methods
    @abstractmethod
    async def validate_code_safety(self, source_code: str, language: CodeLanguage) -> bool:
        pass
    
    @abstractmethod
    async def execute_code_with_language(self, source_code: str, language: SupportedLanguage, stdin: Optional[str] = None) -> Dict[str, Any]:
        pass
    
    @abstractmethod
    async def execute_test_case(self, source_code: str, language: SupportedLanguage, test_input: str, expected_output: str, test_name: str) -> TestCaseExecution:
        pass
    
    @abstractmethod
    async def generate_test_cases_ai(self, block_id: str, count: int = 3) -> List[TestCase]:
        pass
    
    # Comparison methods
    @abstractmethod
    async def compare_outputs(self, actual: str, expected: str, test_name: str = "Unknown") -> bool:
        pass 