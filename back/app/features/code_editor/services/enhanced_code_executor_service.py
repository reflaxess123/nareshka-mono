"""
🚀 Улучшенный сервис выполнения кода с поддержкой Docker и Judge0
Автоматически выбирает оптимальный метод выполнения
"""

import logging
import os
from typing import Optional

from app.features.code_editor.repositories.code_editor_repository import (
    CodeEditorRepository,
)
from app.features.code_editor.services.code_executor_service import CodeExecutorService
# Judge0Service удален
from app.shared.entities.enums import ExecutionStatus
from app.shared.models.code_execution_models import CodeExecution, SupportedLanguage

logger = logging.getLogger(__name__)


class EnhancedCodeExecutorService:
    """🚀 Сервис выполнения кода через Docker"""

    def __init__(self, code_editor_repository: CodeEditorRepository):
        self.code_editor_repository = code_editor_repository
        self.docker_service = CodeExecutorService(code_editor_repository)

    async def execute_code(
        self,
        source_code: str,
        language: SupportedLanguage,
        stdin: Optional[str] = None,
        user_id: Optional[int] = None,
        block_id: Optional[str] = None,
    ) -> CodeExecution:
        """
        Выполняет код через Docker

        Args:
            source_code: Исходный код для выполнения
            language: Объект поддерживаемого языка
            stdin: Входные данные для программы
            user_id: ID пользователя (опционально)
            block_id: ID блока (опционально)

        Returns:
            CodeExecution объект с результатами выполнения
        """
        logger.info(
            f"Starting code execution for language {language.language}"
        )

        try:
            return await self.docker_service.execute_code(
                source_code, language, stdin, user_id, block_id
            )
        except Exception as e:
            logger.error(f"Code execution failed: {str(e)}")
            return self._create_error_execution(
                source_code, language, stdin, user_id, block_id, str(e)
            )


    def _create_error_execution(
        self,
        source_code: str,
        language: SupportedLanguage,
        stdin: Optional[str] = None,
        user_id: Optional[int] = None,
        block_id: Optional[str] = None,
        error_message: str = "Execution failed",
    ) -> CodeExecution:
        """Создает объект CodeExecution с ошибкой"""
        import uuid
        from datetime import datetime

        execution = CodeExecution()
        execution.id = str(uuid.uuid4())
        execution.userId = user_id
        execution.blockId = block_id
        execution.languageId = language.id
        execution.sourceCode = source_code
        execution.stdin = stdin
        execution.status = ExecutionStatus.ERROR
        execution.stdout = None
        execution.stderr = None
        execution.exitCode = 1
        execution.executionTimeMs = 0
        execution.memoryUsedMB = None
        execution.containerLogs = None
        execution.errorMessage = error_message
        execution.createdAt = datetime.now()
        execution.completedAt = datetime.now()

        return execution

    async def get_supported_languages(self):
        """Получает список поддерживаемых языков"""
        return await self.docker_service.get_supported_languages()

    async def get_execution_by_id(self, execution_id: str):
        """Получает выполнение по ID"""
        return await self.docker_service.get_execution_by_id(execution_id)

    async def get_user_executions(
        self,
        user_id: int,
        block_id: Optional[str] = None,
        limit: int = 20,
        offset: int = 0,
    ):
        """Получает историю выполнений пользователя"""
        return await self.docker_service.get_user_executions(
            user_id, block_id, limit, offset
        )

    def validate_code_safety(self, source_code: str, language):
        """Проверяет безопасность кода"""
        return self.docker_service.validate_code_safety(source_code, language)

    def get_execution_stats(self):
        """Возвращает статистику выполнения"""
        return {
            "execution_method": "docker_only",
            "supported_languages_count": 0,  # TODO: получить из docker_service
        }
