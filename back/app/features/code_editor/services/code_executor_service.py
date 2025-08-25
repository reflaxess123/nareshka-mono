"""
🐳 Сервис выполнения кода в изолированных Docker контейнерах
"""

import json
import logging
import os
import platform
import re
import tempfile
import time
import uuid
from datetime import datetime
from typing import Any, Dict, List, Optional

import docker
from docker.errors import ContainerError, ImageNotFound

from app.features.code_editor.repositories.code_editor_repository import (
    CodeEditorRepository,
)
from app.shared.models.code_execution_models import CodeExecution, SupportedLanguage
from app.shared.models.enums import CodeLanguage, ExecutionStatus

logger = logging.getLogger(__name__)


# Кроссплатформенный путь к общей директории для выполнения кода
def get_shared_exec_dir():
    """Получает путь к общей директории для выполнения кода в зависимости от ОС"""
    if platform.system() == "Windows":
        # В Windows используем C:\temp\nareshka-executions
        base_dir = "C:\\temp\\nareshka-executions"
    else:
        # В Unix-подобных системах используем /tmp/nareshka-executions
        base_dir = "/tmp/nareshka-executions"

    os.makedirs(base_dir, exist_ok=True)
    return base_dir


SHARED_EXEC_DIR = get_shared_exec_dir()


class CodeExecutionError(Exception):
    """Кастомное исключение для ошибок выполнения кода"""

    pass


class CodeExecutorService:
    """🐳 Сервис для безопасного выполнения кода в изолированных Docker контейнерах"""

    def __init__(self, code_editor_repository: CodeEditorRepository):
        self.code_editor_repository = code_editor_repository
        self.docker_client = None
        self.execution_timeout = 30  # Максимальное время выполнения в секундах
        self.max_memory = "256m"  # Максимальная память

    def _get_docker_client(self):
        """Ленивая инициализация Docker клиента"""
        if self.docker_client is None:
            try:
                self.docker_client = docker.from_env()
            except Exception as e:
                # Временно возвращаем заглушку вместо ошибки
                logger.warning(
                    f"Cannot connect to Docker: {str(e)}. Code execution will be disabled."
                )
                raise CodeExecutionError(
                    "Docker service is not available. Please ensure Docker Desktop is running."
                ) from e
        return self.docker_client

    async def execute_code(
        self,
        source_code: str,
        language: SupportedLanguage,
        stdin: Optional[str] = None,
        user_id: Optional[int] = None,
        block_id: Optional[str] = None,
    ) -> CodeExecution:
        """
        Выполняет код в изолированном Docker контейнере

        Args:
            source_code: Исходный код для выполнения
            language: Объект поддерживаемого языка
            stdin: Входные данные для программы
            user_id: ID пользователя (опционально)
            block_id: ID блока (опционально)

        Returns:
            CodeExecution объект с результатами выполнения
        """
        execution_id = str(uuid.uuid4())
        start_time = time.time()

        logger.info(
            f"Starting code execution {execution_id} for language {language.language}"
        )

        # Создаем объект CodeExecution
        execution = CodeExecution(
            id=execution_id,
            userId=user_id,
            blockId=block_id,
            languageId=language.id,
            sourceCode=source_code,
            stdin=stdin,
            status=ExecutionStatus.PENDING,
            stdout=None,
            stderr=None,
            exitCode=None,
            executionTimeMs=None,
            memoryUsedMB=None,
            containerLogs=None,
            errorMessage=None,
            createdAt=datetime.now(),
            completedAt=None,
        )

        try:
            # Проверяем доступность Docker перед выполнением
            try:
                self._get_docker_client()
            except CodeExecutionError as e:
                execution.status = ExecutionStatus.ERROR
                execution.errorMessage = str(e)
                execution.executionTimeMs = int((time.time() - start_time) * 1000)
                execution.completedAt = datetime.now()
                await self.code_editor_repository.save_execution(execution)
                return execution

            # Создаем временную директорию для файлов в общем месте
            with tempfile.TemporaryDirectory(dir=SHARED_EXEC_DIR) as temp_dir:
                # Даем права на чтение и выполнение для всех, чтобы
                # пользователь 'nobody' в дочернем контейнере мог получить доступ
                os.chmod(temp_dir, 0o777)

                # Записываем исходный код в файл
                source_file = os.path.join(temp_dir, f"main{language.fileExtension}")
                with open(source_file, "w", encoding="utf-8") as f:
                    f.write(source_code)
                # Даем права на чтение и запись всем
                os.chmod(source_file, 0o666)

                # Записываем входные данные если есть
                stdin_file = None
                if stdin:
                    stdin_file = os.path.join(temp_dir, "input.txt")
                    with open(stdin_file, "w", encoding="utf-8") as f:
                        f.write(stdin)
                    # Даем права на чтение и запись всем
                    os.chmod(stdin_file, 0o666)

                # Выполняем код в контейнере
                result = await self._run_in_container(
                    temp_dir, language, execution_id, stdin_file
                )

                # Обновляем объект выполнения
                execution.status = result["status"]
                execution.stdout = result.get("stdout")
                execution.stderr = result.get("stderr")
                execution.exitCode = result.get("exitCode")
                execution.executionTimeMs = int((time.time() - start_time) * 1000)
                execution.memoryUsedMB = result.get("memoryUsedMB")
                execution.containerLogs = result.get("containerLogs")
                execution.errorMessage = result.get("errorMessage")
                execution.completedAt = datetime.now()

                logger.info(
                    f"Code execution {execution_id} completed in {execution.executionTimeMs}ms"
                )

        except Exception as e:
            logger.error(f"Code execution {execution_id} failed: {str(e)}")
            execution.status = ExecutionStatus.ERROR
            execution.errorMessage = str(e)
            execution.executionTimeMs = int((time.time() - start_time) * 1000)
            execution.completedAt = datetime.now()

        # Сохраняем результат в репозитории
        await self.code_editor_repository.save_execution(execution)
        return execution

    async def _run_in_container(
        self,
        temp_dir: str,
        language: SupportedLanguage,
        execution_id: str,
        stdin_file: Optional[str] = None,
    ) -> Dict[str, Any]:
        """Запускает код в Docker контейнере"""

        try:
            # Подготавливаем команду
            command = self._prepare_command(language, stdin_file)

            # Настройки контейнера
            container_config = {
                "image": language.dockerImage,
                "command": command,
                "working_dir": "/code",
                "volumes": {temp_dir: {"bind": "/code", "mode": "ro"}},
                "mem_limit": f"{language.memoryLimitMB}m",
                "memswap_limit": f"{language.memoryLimitMB}m",
                "cpu_quota": 50000,  # 50% CPU
                "network_disabled": True,  # Отключаем сеть
                "read_only": True,  # Только чтение файловой системы
                "user": "nobody",  # Запускаем от непривилегированного пользователя
                "cap_drop": ["ALL"],  # Убираем все capabilities
                "security_opt": ["no-new-privileges"],
                "pids_limit": 50,  # Ограничиваем количество процессов
                "remove": True,  # Удаляем контейнер после выполнения
                "detach": False,
                "stdout": True,
                "stderr": True,
            }

            logger.info(
                f"Running container with config: {json.dumps(container_config, indent=2)}"
            )

            # Запускаем контейнер
            start_time = time.time()
            docker_client = self._get_docker_client()
            container = docker_client.containers.run(**container_config)

            # Получаем результат
            logs = (
                container.decode("utf-8")
                if isinstance(container, bytes)
                else str(container)
            )

            execution_time = int((time.time() - start_time) * 1000)

            return {
                "status": ExecutionStatus.SUCCESS,
                "stdout": logs,
                "stderr": None,
                "exitCode": 0,
                "executionTimeMs": execution_time,
                "containerLogs": f"Container executed successfully in {execution_time}ms",
            }

        except ContainerError as e:
            # Контейнер завершился с ошибкой
            stderr = e.stderr.decode("utf-8") if e.stderr else ""
            stdout = ""

            return {
                "status": ExecutionStatus.ERROR,
                "stdout": stdout,
                "stderr": stderr,
                "exitCode": e.exit_status,
                "errorMessage": f"Runtime error (exit code {e.exit_status})",
                "containerLogs": f"Container error: {str(e)}",
            }

        except ImageNotFound:
            return {
                "status": ExecutionStatus.ERROR,
                "errorMessage": f"Docker image {language.dockerImage} not found",
                "containerLogs": "Docker image not available",
            }

        except Exception as e:
            return {
                "status": ExecutionStatus.ERROR,
                "errorMessage": f"Container execution failed: {str(e)}",
                "containerLogs": f"Unexpected error: {str(e)}",
            }

    def _prepare_command(
        self, language: SupportedLanguage, stdin_file: Optional[str]
    ) -> str:
        """Подготавливает команду для выполнения в контейнере"""

        base_command = language.runCommand.replace(
            "{file}", f"main{language.fileExtension}"
        )

        # Если есть компиляция
        if language.compileCommand:
            compile_cmd = language.compileCommand.replace(
                "{file}", f"main{language.fileExtension}"
            )
            if stdin_file:
                return f"bash -c '{compile_cmd} && {base_command} < input.txt'"
            else:
                return f"bash -c '{compile_cmd} && {base_command}'"
        # Только выполнение
        elif stdin_file:
            return f"bash -c '{base_command} < input.txt'"
        else:
            return base_command

    def validate_code_safety(self, source_code: str, language: CodeLanguage) -> bool:
        """
        Проверяет безопасность кода перед выполнением

        Args:
            source_code: Исходный код для проверки
            language: Язык программирования

        Returns:
            True если код безопасен, False - если содержит опасные конструкции
        """

        # Общие опасные паттерны
        dangerous_patterns = [
            # Файловые операции
            r"\bopen\s*\(",
            r"\bfile\s*\(",
            r"\bwith\s+open",
            r"\.write\s*\(",
            r"\.read\s*\(",
            # Системные вызовы
            r"\bos\.",
            r"\bsystem\s*\(",
            r"\bsubprocess\.",
            r"\beval\s*\(",
            r"\bexec\s*\(",
            # Сеть
            r"\bsocket\.",
            r"\brequests\.",
            r"\burllib\.",
            r"\bhttplib\.",
            # Импорты опасных модулей
            r"import\s+os",
            r"import\s+sys",
            r"import\s+subprocess",
            r"import\s+socket",
            r"from\s+os\s+import",
            r"from\s+sys\s+import",
        ]

        # Языко-специфичные проверки
        if language == CodeLanguage.PYTHON:
            dangerous_patterns.extend(
                [
                    r"__import__\s*\(",
                    r"globals\s*\(",
                    r"locals\s*\(",
                    r"vars\s*\(",
                    r"dir\s*\(",
                ]
            )
        elif language == CodeLanguage.JAVASCRIPT:
            dangerous_patterns.extend(
                [
                    r"require\s*\(",
                    r"fs\.",
                    r"process\.",
                    r"child_process",
                ]
            )
        elif language in [CodeLanguage.CPP, CodeLanguage.C]:
            dangerous_patterns.extend(
                [
                    r"#include\s*<fstream>",
                    r"#include\s*<cstdlib>",
                    r"system\s*\(",
                    r"popen\s*\(",
                ]
            )

        # Проверяем код на наличие опасных паттернов
        for pattern in dangerous_patterns:
            if re.search(pattern, source_code, re.IGNORECASE):
                logger.warning(
                    f"Dangerous code pattern found in user code: '{pattern}'"
                )
                return False

        return True

    async def get_supported_languages(self) -> List[SupportedLanguage]:
        """Получает список поддерживаемых языков программирования"""
        return await self.code_editor_repository.get_supported_languages()

    async def get_execution_by_id(self, execution_id: str) -> Optional[CodeExecution]:
        """Получает выполнение по ID"""
        return await self.code_editor_repository.get_execution_by_id(execution_id)

    async def get_user_executions(
        self,
        user_id: int,
        block_id: Optional[str] = None,
        limit: int = 20,
        offset: int = 0,
    ) -> List[CodeExecution]:
        """Получает историю выполнений пользователя"""
        return await self.code_editor_repository.get_user_executions(
            user_id, block_id, limit, offset
        )
