import json
import logging
import os
import tempfile
import time
import uuid
from typing import Any, Dict, List, Optional
import platform

import docker
from docker.errors import APIError, ContainerError, ImageNotFound

from .models import CodeLanguage, ExecutionStatus, SupportedLanguage

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


class CodeExecutor:
    """Сервис для безопасного выполнения кода в изолированных Docker контейнерах"""

    def __init__(self):
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
                logger.warning(f"Cannot connect to Docker: {str(e)}. Code execution will be disabled.")
                raise CodeExecutionError("Docker service is not available. Please ensure Docker Desktop is running.")
        return self.docker_client

    async def execute_code(
        self,
        source_code: str,
        language: SupportedLanguage,
        stdin: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Выполняет код в изолированном Docker контейнере
        
        Args:
            source_code: Исходный код для выполнения
            language: Объект поддерживаемого языка
            stdin: Входные данные для программы
            
        Returns:
            Словарь с результатами выполнения
        """
        execution_id = str(uuid.uuid4())
        start_time = time.time()

        logger.info(f"Starting code execution {execution_id} for language {language.language}")

        try:
            # Проверяем доступность Docker перед выполнением
            try:
                self._get_docker_client()
            except CodeExecutionError as e:
                return {
                    "status": ExecutionStatus.ERROR,
                    "errorMessage": str(e),
                    "executionTimeMs": int((time.time() - start_time) * 1000)
                }
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

                execution_time = int((time.time() - start_time) * 1000)
                result["executionTimeMs"] = execution_time

                logger.info(f"Code execution {execution_id} completed in {execution_time}ms")
                return result

        except Exception as e:
            logger.error(f"Code execution {execution_id} failed: {str(e)}")
            return {
                "status": ExecutionStatus.ERROR,
                "errorMessage": str(e),
                "executionTimeMs": int((time.time() - start_time) * 1000)
            }

    async def _run_in_container(
        self,
        temp_dir: str,
        language: SupportedLanguage,
        execution_id: str,
        stdin_file: Optional[str] = None
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
                "stderr": True
            }

            logger.info(f"Running container with config: {json.dumps(container_config, indent=2)}")

            # Запускаем контейнер
            start_time = time.time()
            docker_client = self._get_docker_client()
            container = docker_client.containers.run(**container_config)

            # Получаем результат
            logs = container.decode("utf-8") if isinstance(container, bytes) else str(container)

            execution_time = int((time.time() - start_time) * 1000)

            return {
                "status": ExecutionStatus.SUCCESS,
                "stdout": logs,
                "stderr": None,
                "exitCode": 0,
                "executionTimeMs": execution_time,
                "containerLogs": f"Container executed successfully in {execution_time}ms"
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
                "containerLogs": f"Container error: {str(e)}"
            }

        except ImageNotFound:
            return {
                "status": ExecutionStatus.ERROR,
                "errorMessage": f"Docker image {language.dockerImage} not found",
                "containerLogs": f"Image {language.dockerImage} not available"
            }

        except APIError as e:
            if "timeout" in str(e).lower():
                return {
                    "status": ExecutionStatus.TIMEOUT,
                    "errorMessage": f"Execution timed out after {language.timeoutSeconds} seconds",
                    "containerLogs": f"Container timeout: {str(e)}"
                }
            else:
                return {
                    "status": ExecutionStatus.ERROR,
                    "errorMessage": f"Docker API error: {str(e)}",
                    "containerLogs": f"Docker API error: {str(e)}"
                }

    def _prepare_command(self, language: SupportedLanguage, stdin_file: Optional[str]) -> str:
        """Подготавливает команду для выполнения в контейнере"""

        if language.language == CodeLanguage.PYTHON:
            if stdin_file:
                return "sh -c 'python -B main.py < input.txt'"
            else:
                return "python -B main.py"

        elif language.language == CodeLanguage.JAVASCRIPT:
            if stdin_file:
                return "sh -c 'node main.js < input.txt'"
            else:
                return "node main.js"

        elif language.language == CodeLanguage.JAVA:
            # Для Java нужна компиляция
            if stdin_file:
                return "sh -c 'javac main.java && java Main < input.txt'"
            else:
                return "sh -c 'javac main.java && java Main'"

        elif language.language == CodeLanguage.CPP:
            # Для C++ нужна компиляция
            if stdin_file:
                return "sh -c 'g++ -o main main.cpp && ./main < input.txt'"
            else:
                return "sh -c 'g++ -o main main.cpp && ./main'"

        elif language.language == CodeLanguage.GO:
            if stdin_file:
                return "sh -c 'go run main.go < input.txt'"
            else:
                return "go run main.go"

        else:
            # Используем команду из настроек языка
            base_command = language.runCommand.replace("{file}", f"main{language.fileExtension}")
            if stdin_file:
                return f"sh -c '{base_command} < input.txt'"
            else:
                return base_command

    def validate_code_safety(self, source_code: str, language: CodeLanguage) -> bool:
        """
        Базовая проверка безопасности кода
        
        Args:
            source_code: Исходный код
            language: Язык программирования
            
        Returns:
            True если код считается безопасным
        """
        # Список запрещенных паттернов
        forbidden_patterns = [
            # Системные команды
            "system", "exec", "eval", "subprocess", "os.system",
            # Файловые операции
            "open(", "file(", "input(", "raw_input(",
            # Сетевые операции
            "socket", "urllib", "requests", "http",
            # Импорт опасных модулей
            "import os", "import sys", "import subprocess",
            "from os", "from sys", "from subprocess",
            # Опасные JavaScript функции
            "require(", "process.", "fs.", "child_process",
            # Бесконечные циклы (базовая проверка)
            "while True:", "while(true)", "for(;;)"
        ]

        source_lower = source_code.lower()

        for pattern in forbidden_patterns:
            if pattern.lower() in source_lower:
                logger.warning(f"Potentially unsafe code detected: {pattern}")
                return False

        # Проверка размера кода
        if len(source_code) > 10000:  # 10KB лимит
            logger.warning("Code size exceeds limit")
            return False

        return True

    async def get_supported_languages(self) -> List[SupportedLanguage]:
        """Возвращает список поддерживаемых языков"""
        # В реальной реализации это будет запрос к БД
        # Пока возвращаем базовые языки
        return [
            {
                "id": "python39",
                "name": "Python 3.9",
                "language": CodeLanguage.PYTHON,
                "version": "3.9",
                "dockerImage": "python:3.9-alpine",
                "fileExtension": ".py",
                "runCommand": "python {file}",
                "timeoutSeconds": 10,
                "memoryLimitMB": 128,
                "isEnabled": True
            },
            {
                "id": "node18",
                "name": "Node.js 18",
                "language": CodeLanguage.JAVASCRIPT,
                "version": "18",
                "dockerImage": "node:18-alpine",
                "fileExtension": ".js",
                "runCommand": "node {file}",
                "timeoutSeconds": 10,
                "memoryLimitMB": 128,
                "isEnabled": True
            }
        ]


# Глобальный экземпляр исполнителя кода
code_executor = CodeExecutor()
