"""
🏛️ Judge0 API сервис для выполнения кода через внешний API
Интеграция с ce.judge0.com для поддержки 60+ языков программирования
"""

import base64
import logging
import os
import time
import uuid
from typing import Any, Dict, List, Optional, Tuple

import httpx
from app.features.code_editor.repositories.code_editor_repository import CodeEditorRepository
from app.shared.models.code_execution_models import CodeExecution, SupportedLanguage
from app.shared.entities.enums import ExecutionStatus

logger = logging.getLogger(__name__)


class Judge0Service:
    """🏛️ Сервис для выполнения кода через Judge0 API"""

    def __init__(self, code_editor_repository: CodeEditorRepository):
        self.code_editor_repository = code_editor_repository
        self.base_url = os.getenv("JUDGE0_URL", "https://ce.judge0.com")
        self.api_key = os.getenv("JUDGE0_API_KEY")
        self.rapidapi_host = os.getenv("RAPIDAPI_HOST")
        self.timeout = 30  # Таймаут для HTTP запросов
        self.max_wait_time = 60  # Максимальное время ожидания результата

        # Маппинг языков из нашей системы в Judge0 language IDs
        self.language_mapping = {
            "PYTHON": 71,  # Python 3.8.1
            "JAVASCRIPT": 63,  # JavaScript (Node.js 12.14.0)
            "JAVA": 62,  # Java (OpenJDK 13.0.1)
            "CPP": 54,  # C++ (GCC 9.2.0)
            "C": 50,  # C (GCC 9.2.0)
            "CSHARP": 51,  # C# (Mono 6.6.0.161)
            "GO": 60,  # Go (1.13.5)
            "RUST": 73,  # Rust (1.40.0)
            "PHP": 68,  # PHP (7.4.1)
            "RUBY": 72,  # Ruby (2.7.0)
            "SWIFT": 83,  # Swift (5.2.3)
            "KOTLIN": 78,  # Kotlin (1.3.70)
            "SCALA": 81,  # Scala (2.13.2)
            "TYPESCRIPT": 74,  # TypeScript (3.7.4)
            "DART": 90,  # Dart (2.19.2)
        }

    async def execute_code(
        self,
        source_code: str,
        language: SupportedLanguage,
        stdin: Optional[str] = None,
        user_id: Optional[int] = None,
        block_id: Optional[str] = None,
    ) -> CodeExecution:
        """
        Выполняет код через Judge0 API

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
            f"Starting Judge0 code execution {execution_id} for language {language.language}"
        )

        # Создаем объект CodeExecution (используем модель БД)
        from datetime import datetime
        execution = CodeExecution()
        execution.id = execution_id
        execution.userId = user_id
        execution.blockId = block_id
        execution.languageId = language.id
        execution.sourceCode = source_code
        execution.stdin = stdin
        execution.status = ExecutionStatus.PENDING
        execution.stdout = None
        execution.stderr = None
        execution.exitCode = None
        execution.executionTimeMs = None
        execution.memoryUsedMB = None
        execution.containerLogs = None
        execution.errorMessage = None
        execution.createdAt = datetime.now()
        execution.completedAt = None

        try:
            # Получаем Judge0 language ID
            judge0_language_id = self._get_judge0_language_id(language.language.value)
            if judge0_language_id is None:
                execution.status = ExecutionStatus.ERROR
                execution.errorMessage = f"Language {language.language.value} not supported by Judge0"
                execution.executionTimeMs = int((time.time() - start_time) * 1000)
                execution.completedAt = datetime.now()
                await self.code_editor_repository.save_execution(execution)
                return execution

            # Отправляем код на выполнение
            submission_token = await self._submit_code(
                source_code, judge0_language_id, stdin
            )
            if not submission_token:
                execution.status = ExecutionStatus.ERROR
                execution.errorMessage = "Failed to submit code to Judge0"
                execution.executionTimeMs = int((time.time() - start_time) * 1000)
                execution.completedAt = datetime.now()
                await self.code_editor_repository.save_execution(execution)
                return execution

            # Ждем результат выполнения
            result = await self._wait_for_result(submission_token)
            
            # Обновляем объект выполнения
            execution.status = result["status"]
            execution.stdout = result.get("stdout")
            execution.stderr = result.get("stderr")
            execution.exitCode = result.get("exitCode")
            execution.executionTimeMs = int((time.time() - start_time) * 1000)
            execution.memoryUsedMB = result.get("memoryUsedMB")
            execution.containerLogs = f"Judge0 execution completed with token {submission_token}"
            execution.errorMessage = result.get("errorMessage")
            execution.completedAt = datetime.now()

            logger.info(
                f"Judge0 code execution {execution_id} completed in {execution.executionTimeMs}ms"
            )

        except Exception as e:
            logger.error(f"Judge0 code execution {execution_id} failed: {str(e)}")
            execution.status = ExecutionStatus.ERROR
            execution.errorMessage = str(e)
            execution.executionTimeMs = int((time.time() - start_time) * 1000)
            execution.completedAt = datetime.now()

        # Сохраняем результат в репозитории
        await self.code_editor_repository.save_execution(execution)
        return execution

    def _get_judge0_language_id(self, language: str) -> Optional[int]:
        """Получает Judge0 language ID для нашего языка"""
        return self.language_mapping.get(language.upper())

    async def _submit_code(
        self, source_code: str, language_id: int, stdin: Optional[str] = None
    ) -> Optional[str]:
        """
        Отправляет код на выполнение в Judge0 API

        Args:
            source_code: Исходный код
            language_id: ID языка в Judge0
            stdin: Входные данные

        Returns:
            Token submission или None в случае ошибки
        """
        try:
            # Кодируем исходный код в base64
            encoded_source = base64.b64encode(source_code.encode()).decode()
            
            # Подготавливаем данные для отправки
            submission_data = {
                "source_code": encoded_source,
                "language_id": language_id,
                "stdin": base64.b64encode(stdin.encode()).decode() if stdin else None,
            }

            # Подготавливаем заголовки
            headers = {"Content-Type": "application/json"}
            if self.api_key and "rapidapi.com" in self.base_url:
                headers.update({
                    "X-RapidAPI-Key": self.api_key,
                    "X-RapidAPI-Host": self.rapidapi_host
                })

            async with httpx.AsyncClient(timeout=self.timeout) as client:
                response = await client.post(
                    f"{self.base_url}/submissions",
                    json=submission_data,
                    params={"wait": "false"},  # Асинхронное выполнение
                    headers=headers
                )
                
                if response.status_code == 201:
                    result = response.json()
                    return result.get("token")
                else:
                    logger.error(f"Judge0 submission failed: {response.status_code} - {response.text}")
                    return None

        except Exception as e:
            logger.error(f"Error submitting code to Judge0: {str(e)}")
            return None

    async def _wait_for_result(self, token: str) -> Dict[str, Any]:
        """
        Ждет результат выполнения от Judge0 API

        Args:
            token: Token submission

        Returns:
            Словарь с результатами выполнения
        """
        wait_start = time.time()
        
        while time.time() - wait_start < self.max_wait_time:
            try:
                # Подготавливаем заголовки для RapidAPI
                headers = {}
                if self.api_key and "rapidapi.com" in self.base_url:
                    headers = {
                        "X-RapidAPI-Key": self.api_key,
                        "X-RapidAPI-Host": self.rapidapi_host
                    }

                async with httpx.AsyncClient(timeout=self.timeout) as client:
                    response = await client.get(
                        f"{self.base_url}/submissions/{token}",
                        headers=headers
                    )
                    
                    if response.status_code == 200:
                        result = response.json()
                        status_id = result.get("status", {}).get("id", 0)
                        
                        # Status IDs: 1-2 = в очереди/обработке, 3 = выполнено, 4+ = различные ошибки
                        if status_id > 2:  # Выполнение завершено
                            return self._parse_judge0_result(result)
                    
                    # Ждем перед следующей проверкой
                    await self._async_sleep(1)
                    
            except Exception as e:
                logger.error(f"Error checking Judge0 result: {str(e)}")
                return {
                    "status": ExecutionStatus.ERROR,
                    "errorMessage": f"Error checking result: {str(e)}",
                }
        
        # Таймаут
        return {
            "status": ExecutionStatus.ERROR,
            "errorMessage": "Execution timeout exceeded",
        }

    def _parse_judge0_result(self, judge0_result: Dict[str, Any]) -> Dict[str, Any]:
        """
        Парсит результат от Judge0 API в наш формат

        Args:
            judge0_result: Результат от Judge0 API

        Returns:
            Словарь с результатами в нашем формате
        """
        status_info = judge0_result.get("status", {})
        status_id = status_info.get("id", 0)
        
        # Декодируем base64 данные
        stdout = None
        stderr = None
        
        if judge0_result.get("stdout"):
            try:
                stdout = base64.b64decode(judge0_result["stdout"]).decode("utf-8")
            except Exception:
                stdout = judge0_result["stdout"]  # Fallback to raw data
        
        if judge0_result.get("stderr"):
            try:
                stderr = base64.b64decode(judge0_result["stderr"]).decode("utf-8")
            except Exception:
                stderr = judge0_result["stderr"]  # Fallback to raw data
        
        # Преобразуем статус Judge0 в наш ExecutionStatus
        if status_id == 3:  # Accepted
            status = ExecutionStatus.SUCCESS
            error_message = None
        elif status_id in [4, 5]:  # Wrong Answer, Time Limit Exceeded
            status = ExecutionStatus.ERROR
            error_message = status_info.get("description", "Execution failed")
        elif status_id == 6:  # Compilation Error
            status = ExecutionStatus.ERROR
            error_message = "Compilation error"
        elif status_id in [7, 8, 9]:  # Runtime errors
            status = ExecutionStatus.ERROR
            error_message = status_info.get("description", "Runtime error")
        else:
            status = ExecutionStatus.ERROR
            error_message = status_info.get("description", "Unknown error")

        return {
            "status": status,
            "stdout": stdout,
            "stderr": stderr,
            "exitCode": 0 if status_id == 3 else 1,
            "memoryUsedMB": judge0_result.get("memory", 0) / 1024 if judge0_result.get("memory") else None,  # KB to MB
            "errorMessage": error_message,
        }

    async def _async_sleep(self, seconds: float):
        """Асинхронный sleep"""
        import asyncio
        await asyncio.sleep(seconds)

    async def get_supported_languages(self) -> List[Dict[str, Any]]:
        """
        Получает список поддерживаемых языков из Judge0 API
        
        Returns:
            Список языков с их ID и информацией
        """
        try:
            # Подготавливаем заголовки для RapidAPI
            headers = {}
            if self.api_key and "rapidapi.com" in self.base_url:
                headers = {
                    "X-RapidAPI-Key": self.api_key,
                    "X-RapidAPI-Host": self.rapidapi_host
                }

            async with httpx.AsyncClient(timeout=self.timeout) as client:
                response = await client.get(
                    f"{self.base_url}/languages",
                    headers=headers
                )
                
                if response.status_code == 200:
                    languages = response.json()
                    # Фильтруем только те языки, которые мы поддерживаем
                    supported = []
                    for lang in languages:
                        for our_lang, judge0_id in self.language_mapping.items():
                            if lang.get("id") == judge0_id:
                                supported.append({
                                    "name": our_lang.lower(),
                                    "judge0_id": judge0_id,
                                    "judge0_name": lang.get("name"),
                                    "version": lang.get("version", ""),
                                })
                                break
                    return supported
                else:
                    logger.error(f"Failed to get Judge0 languages: {response.status_code}")
                    return []
                    
        except Exception as e:
            logger.error(f"Error getting Judge0 languages: {str(e)}")
            return []

    def is_language_supported(self, language: str) -> bool:
        """Проверяет, поддерживается ли язык Judge0"""
        return language.upper() in self.language_mapping