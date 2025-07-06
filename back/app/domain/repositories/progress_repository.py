from abc import ABC, abstractmethod
from typing import List, Optional, Dict, Any
from datetime import datetime

from ..entities.progress import (
    TaskAttempt, 
    TaskSolution, 
    UserCategoryProgress, 
    LearningPath, 
    UserPathProgress,
    TestCase,
    TestValidationResult
)


class ProgressRepository(ABC):
    """Repository для работы с прогрессом пользователей и заданиями"""
    
    # TaskAttempt methods
    @abstractmethod
    async def create_task_attempt(self, attempt: TaskAttempt) -> TaskAttempt:
        pass
    
    @abstractmethod
    async def get_task_attempt_by_id(self, attempt_id: str) -> Optional[TaskAttempt]:
        pass
    
    @abstractmethod
    async def get_task_attempts_by_user_and_block(self, user_id: int, block_id: str) -> List[TaskAttempt]:
        pass
    
    @abstractmethod
    async def get_recent_task_attempts(self, user_id: int, limit: int = 10) -> List[Dict[str, Any]]:
        pass
    
    @abstractmethod
    async def get_next_attempt_number(self, user_id: int, block_id: str) -> int:
        pass
    
    # TaskSolution methods
    @abstractmethod
    async def create_task_solution(self, solution: TaskSolution) -> TaskSolution:
        pass
    
    @abstractmethod
    async def update_task_solution(self, solution: TaskSolution) -> TaskSolution:
        pass
    
    @abstractmethod
    async def get_task_solution_by_user_and_block(self, user_id: int, block_id: str) -> Optional[TaskSolution]:
        pass
    
    # UserCategoryProgress methods
    @abstractmethod
    async def create_category_progress(self, progress: UserCategoryProgress) -> UserCategoryProgress:
        pass
    
    @abstractmethod
    async def update_category_progress(self, progress: UserCategoryProgress) -> UserCategoryProgress:
        pass
    
    @abstractmethod
    async def get_category_progress_by_user_and_category(self, user_id: int, main_category: str, sub_category: Optional[str] = None) -> Optional[UserCategoryProgress]:
        pass
    
    @abstractmethod
    async def get_unified_category_progress(self, user_id: int) -> List[Dict[str, Any]]:
        pass
    
    # LearningPath methods
    @abstractmethod
    async def create_learning_path(self, path: LearningPath) -> LearningPath:
        pass
    
    @abstractmethod
    async def get_learning_path_by_id(self, path_id: str) -> Optional[LearningPath]:
        pass
    
    @abstractmethod
    async def get_active_learning_paths(self) -> List[LearningPath]:
        pass
    
    # UserPathProgress methods
    @abstractmethod
    async def create_path_progress(self, progress: UserPathProgress) -> UserPathProgress:
        pass
    
    @abstractmethod
    async def update_path_progress(self, progress: UserPathProgress) -> UserPathProgress:
        pass
    
    @abstractmethod
    async def get_path_progress_by_user_and_path(self, user_id: int, path_id: str) -> Optional[UserPathProgress]:
        pass
    
    # TestCase methods
    @abstractmethod
    async def create_test_case(self, test_case: TestCase) -> TestCase:
        pass
    
    @abstractmethod
    async def get_test_cases_by_block_id(self, block_id: str) -> List[TestCase]:
        pass
    
    @abstractmethod
    async def get_public_test_cases_by_block_id(self, block_id: str) -> List[TestCase]:
        pass
    
    # TestValidationResult methods
    @abstractmethod
    async def create_test_validation_result(self, result: TestValidationResult) -> TestValidationResult:
        pass
    
    @abstractmethod
    async def get_test_validation_results_by_attempt_id(self, attempt_id: str) -> List[TestValidationResult]:
        pass
    
    # Analytics methods
    @abstractmethod
    async def get_overall_stats(self, user_id: int) -> Dict[str, Any]:
        pass
    
    @abstractmethod
    async def get_progress_analytics(self) -> Dict[str, Any]:
        pass
    
    @abstractmethod
    async def sync_user_content_progress(self, user_id: int, block_id: str) -> None:
        pass
    
    @abstractmethod
    async def update_user_stats(self, user_id: int) -> None:
        pass 