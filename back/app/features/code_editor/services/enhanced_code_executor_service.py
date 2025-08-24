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
from app.features.code_editor.services.judge0_service import Judge0Service
from app.shared.entities.enums import ExecutionStatus
from app.shared.models.code_execution_models import CodeExecution, SupportedLanguage

logger = logging.getLogger(__name__)


class EnhancedCodeExecutorService:
    """🚀 Улучшенный сервис выполнения кода с поддержкой Docker и Judge0"""

    def __init__(self, code_editor_repository: CodeEditorRepository):
        self.code_editor_repository = code_editor_repository
        self.docker_service = CodeExecutorService(code_editor_repository)
        self.judge0_service = Judge0Service(code_editor_repository)

        # Настройки из переменных окружения
        self.use_judge0 = os.getenv("USE_JUDGE0", "false").lower() == "true"
        self.fallback_to_judge0 = (
            os.getenv("FALLBACK_TO_JUDGE0", "true").lower() == "true"
        )
        self.preferred_method = os.getenv(
            "CODE_EXECUTOR_METHOD", "docker"
        ).lower()  # docker | judge0 | auto

    async def execute_code(
        self,
        source_code: str,
        language: SupportedLanguage,
        stdin: Optional[str] = None,
        user_id: Optional[int] = None,
        block_id: Optional[str] = None,
    ) -> CodeExecution:
        """
        Выполняет код, автоматически выбирая оптимальный метод

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
            f"Starting enhanced code execution for language {language.language}"
        )

        # Определяем метод выполнения
        execution_method = self._choose_execution_method(language)

        logger.info(f"Using execution method: {execution_method}")

        try:
            if execution_method == "judge0":
                return await self._execute_with_judge0(
                    source_code, language, stdin, user_id, block_id
                )
            else:
                return await self._execute_with_docker(
                    source_code, language, stdin, user_id, block_id
                )

        except Exception as e:
            logger.error(f"Enhanced code execution failed: {str(e)}")
            # В случае ошибки пытаемся использовать fallback метод
            if execution_method == "docker" and self.fallback_to_judge0:
                logger.info("Falling back to Judge0 after Docker failure")
                try:
                    return await self._execute_with_judge0(
                        source_code, language, stdin, user_id, block_id
                    )
                except Exception as fallback_error:
                    logger.error(f"Judge0 fallback also failed: {str(fallback_error)}")

            # Если все методы не сработали, возвращаем ошибку
            return self._create_error_execution(
                source_code, language, stdin, user_id, block_id, str(e)
            )

    def _choose_execution_method(self, language: SupportedLanguage) -> str:
        """
        Выбирает оптимальный метод выполнения кода

        Args:
            language: Поддерживаемый язык

        Returns:
            Строка с методом выполнения: "docker" или "judge0"
        """
        # Если метод принудительно задан в настройках
        if self.preferred_method == "judge0":
            return "judge0"
        elif self.preferred_method == "docker":
            return "docker"

        # Автоматический выбор
        if self.preferred_method == "auto":
            # Judge0 поддерживает больше языков
            if self.judge0_service.is_language_supported(language.language.value):
                # Используем Judge0 для языков, которые лучше поддерживаются там
                preferred_judge0_languages = [
                    "swift",
                    "kotlin",
                    "scala",
                    "dart",
                    "typescript",
                ]
                if language.language.value.lower() in preferred_judge0_languages:
                    return "judge0"

            # По умолчанию используем Docker
            return "docker"

        # По умолчанию Docker
        return "docker"

    async def _execute_with_docker(
        self,
        source_code: str,
        language: SupportedLanguage,
        stdin: Optional[str] = None,
        user_id: Optional[int] = None,
        block_id: Optional[str] = None,
    ) -> CodeExecution:
        """Выполняет код через Docker"""
        try:
            return await self.docker_service.execute_code(
                source_code, language, stdin, user_id, block_id
            )
        except Exception as e:
            logger.error(f"Docker execution failed: {str(e)}")
            raise

    async def _execute_with_judge0(
        self,
        source_code: str,
        language: SupportedLanguage,
        stdin: Optional[str] = None,
        user_id: Optional[int] = None,
        block_id: Optional[str] = None,
    ) -> CodeExecution:
        """Выполняет код через Judge0"""
        try:
            return await self.judge0_service.execute_code(
                source_code, language, stdin, user_id, block_id
            )
        except Exception as e:
            logger.error(f"Judge0 execution failed: {str(e)}")
            raise

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

    async def get_judge0_languages(self):
        """Получает список поддерживаемых языков Judge0"""
        return await self.judge0_service.get_supported_languages()

    def get_execution_stats(self):
        """Возвращает статистику выполнения"""
        return {
            "preferred_method": self.preferred_method,
            "use_judge0": self.use_judge0,
            "fallback_to_judge0": self.fallback_to_judge0,
            "supported_languages_count": len(self.judge0_service.language_mapping),
        }
