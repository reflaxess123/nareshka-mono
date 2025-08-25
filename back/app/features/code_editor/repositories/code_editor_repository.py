"""Репозиторий для работы с редактором кода"""

import logging
from abc import ABC, abstractmethod
from typing import Any, Dict, List, Optional

import docker
from sqlalchemy import func
from sqlalchemy.orm import Session

from app.features.code_editor.exceptions.code_editor_exceptions import (
    CodeExecutionError,
)
from app.shared.models.content_models import ContentBlock
from app.shared.models.enums import CodeLanguage, ExecutionStatus
from app.shared.models.code_execution_models import (
    CodeExecution,
    SupportedLanguage,
    UserCodeSolution,
)
from app.shared.models.test_case_models import TestCase

logger = logging.getLogger(__name__)


class CodeEditorRepositoryInterface(ABC):
    """Интерфейс репозитория для работы с редактором кода"""

    @abstractmethod
    async def get_supported_languages(self) -> List[SupportedLanguage]:
        pass

    @abstractmethod
    async def get_language_by_id(self, language_id: str) -> Optional[SupportedLanguage]:
        pass

    @abstractmethod
    async def get_language_by_enum(
        self, language: CodeLanguage
    ) -> Optional[SupportedLanguage]:
        pass

    @abstractmethod
    async def create_code_execution(self, execution: CodeExecution) -> CodeExecution:
        pass

    @abstractmethod
    async def update_code_execution(self, execution: CodeExecution) -> CodeExecution:
        pass

    @abstractmethod
    async def save_execution(self, execution: CodeExecution) -> CodeExecution:
        pass

    @abstractmethod
    async def get_execution_by_id(self, execution_id: str) -> Optional[CodeExecution]:
        pass

    @abstractmethod
    async def get_user_executions(
        self,
        user_id: int,
        block_id: Optional[str] = None,
        limit: int = 20,
        offset: int = 0,
    ) -> List[CodeExecution]:
        pass

    @abstractmethod
    async def validate_code_safety(
        self, source_code: str, language: CodeLanguage
    ) -> bool:
        pass

    @abstractmethod
    async def execute_code_with_language(
        self, source_code: str, language: SupportedLanguage, stdin: Optional[str] = None
    ) -> Dict[str, Any]:
        pass


class CodeEditorRepository(CodeEditorRepositoryInterface):
    """Репозиторий для работы с редактором кода"""

    def __init__(self, session: Session):
        self.session = session
        try:
            self.docker_client = docker.from_env()
            logger.info("Docker client успешно инициализирован")
        except Exception as e:
            logger.warning(f"Не удалось подключиться к Docker: {e}")
            self.docker_client = None

    async def get_supported_languages(self) -> List[SupportedLanguage]:
        """Получение списка поддерживаемых языков"""
        logger.info("Получение поддерживаемых языков")

        try:
            languages = (
                self.session.query(SupportedLanguage)
                .filter(SupportedLanguage.isEnabled == True)
                .all()
            )

            logger.info(f"Найдено {len(languages)} поддерживаемых языков")
            return languages

        except Exception as e:
            logger.error(f"Ошибка при получении языков: {e}")
            return []

    async def get_language_by_id(self, language_id: str) -> Optional[SupportedLanguage]:
        """Получение языка по ID"""
        logger.info(f"Получение языка по ID: {language_id}")

        try:
            language = (
                self.session.query(SupportedLanguage)
                .filter(SupportedLanguage.id == language_id)
                .first()
            )

            if language:
                logger.info(f"Язык найден: {language.name}")
            else:
                logger.warning(f"Язык не найден: {language_id}")

            return language

        except Exception as e:
            logger.error(f"Ошибка при получении языка: {e}")
            return None

    async def get_language_by_enum(
        self, language: CodeLanguage
    ) -> Optional[SupportedLanguage]:
        """Получение языка по enum"""
        logger.info(f"Получение языка по enum: {language}")

        try:
            lang_obj = (
                self.session.query(SupportedLanguage)
                .filter(
                    SupportedLanguage.language == language,
                    SupportedLanguage.isEnabled == True,
                )
                .first()
            )

            if lang_obj:
                logger.info(f"Язык найден: {lang_obj.name}")
            else:
                logger.warning(f"Язык не найден или отключен: {language}")

            return lang_obj

        except Exception as e:
            logger.error(f"Ошибка при получении языка: {e}")
            return None

    async def create_code_execution(self, execution: CodeExecution) -> CodeExecution:
        """Создание записи о выполнении кода"""
        logger.info(f"Создание выполнения кода: {execution.id}")

        try:
            self.session.add(execution)
            self.session.commit()
            self.session.refresh(execution)

            logger.info(f"Выполнение создано: {execution.id}")
            return execution

        except Exception as e:
            logger.error(f"Ошибка при создании выполнения: {e}")
            self.session.rollback()
            raise

    async def update_code_execution(self, execution: CodeExecution) -> CodeExecution:
        """Обновление записи о выполнении кода"""
        logger.info(f"Обновление выполнения кода: {execution.id}")

        try:
            self.session.merge(execution)
            self.session.commit()

            logger.info(f"Выполнение обновлено: {execution.id}")
            return execution

        except Exception as e:
            logger.error(f"Ошибка при обновлении выполнения: {e}")
            self.session.rollback()
            raise

    async def save_execution(self, execution: CodeExecution) -> CodeExecution:
        """Сохранение выполнения (создание или обновление)"""
        logger.info(f"Сохранение выполнения кода: {execution.id}")

        try:
            # Проверяем, существует ли уже выполнение
            existing = (
                self.session.query(CodeExecution)
                .filter(CodeExecution.id == execution.id)
                .first()
            )

            if existing:
                # Обновляем существующее
                for key, value in execution.__dict__.items():
                    if not key.startswith("_") and hasattr(existing, key):
                        setattr(existing, key, value)
                self.session.commit()
                logger.info(f"Выполнение обновлено: {execution.id}")
                return existing
            else:
                # Создаем новое
                self.session.add(execution)
                self.session.commit()
                self.session.refresh(execution)
                logger.info(f"Выполнение создано: {execution.id}")
                return execution

        except Exception as e:
            logger.error(f"Ошибка при сохранении выполнения: {e}")
            self.session.rollback()
            raise

    async def get_execution_by_id(self, execution_id: str) -> Optional[CodeExecution]:
        """Получение выполнения по ID"""
        logger.info(f"Получение выполнения по ID: {execution_id}")

        try:
            execution = (
                self.session.query(CodeExecution)
                .filter(CodeExecution.id == execution_id)
                .first()
            )

            if execution:
                logger.info(f"Выполнение найдено: {execution_id}")
            else:
                logger.warning(f"Выполнение не найдено: {execution_id}")

            return execution

        except Exception as e:
            logger.error(f"Ошибка при получении выполнения: {e}")
            return None

    async def get_user_executions(
        self,
        user_id: int,
        block_id: Optional[str] = None,
        limit: int = 20,
        offset: int = 0,
    ) -> List[CodeExecution]:
        """Получение выполнений пользователя"""
        logger.info(f"Получение выполнений пользователя {user_id}")

        try:
            query = self.session.query(CodeExecution).filter(
                CodeExecution.userId == user_id
            )

            if block_id:
                query = query.filter(CodeExecution.blockId == block_id)

            executions = (
                query.order_by(CodeExecution.createdAt.desc())
                .limit(limit)
                .offset(offset)
                .all()
            )

            logger.info(
                f"Найдено {len(executions)} выполнений для пользователя {user_id}"
            )
            return executions

        except Exception as e:
            logger.error(f"Ошибка при получении выполнений: {e}")
            return []

    async def validate_code_safety(
        self, source_code: str, language: CodeLanguage
    ) -> bool:
        """Валидация безопасности кода"""
        logger.info(f"Валидация безопасности кода для языка {language}")

        try:
            # Список запрещенных паттернов
            dangerous_patterns = {
                CodeLanguage.PYTHON: [
                    "__import__",
                    "exec",
                    "eval",
                    "compile",
                    "open",
                    "file",
                    "input",
                    "raw_input",
                    "reload",
                    "globals",
                    "locals",
                    "os.",
                    "sys.",
                    "subprocess",
                    "shutil",
                    "socket",
                    "urllib",
                    "requests",
                    "pickle",
                    "marshal",
                ],
                CodeLanguage.JAVASCRIPT: [
                    "require",
                    "import",
                    "fetch",
                    "XMLHttpRequest",
                    "document",
                    "window",
                    "global",
                    "process",
                    "Buffer",
                    "eval",
                    "Function",
                    "setTimeout",
                    "setInterval",
                ],
                CodeLanguage.JAVA: [
                    "System.exit",
                    "Runtime",
                    "ProcessBuilder",
                    "File",
                    "FileInputStream",
                    "FileOutputStream",
                    "Socket",
                    "ServerSocket",
                    "Class.forName",
                    "reflect",
                ],
            }

            patterns = dangerous_patterns.get(language, [])

            for pattern in patterns:
                if pattern in source_code:
                    logger.warning(f"Обнаружен опасный паттерн: {pattern}")
                    return False

            logger.info("Код прошел проверку безопасности")
            return True

        except Exception as e:
            logger.error(f"Ошибка при валидации безопасности: {e}")
            return False

    async def execute_code_with_language(
        self, source_code: str, language: SupportedLanguage, stdin: Optional[str] = None
    ) -> Dict[str, Any]:
        """Выполнение кода в Docker контейнере"""
        logger.info(f"Выполнение кода на языке {language.name}")

        if self.docker_client is None:
            logger.error("Docker клиент недоступен. Убедитесь, что Docker запущен.")
            raise CodeExecutionError(
                "", "Docker недоступен. Убедитесь, что Docker Desktop запущен."
            )

        try:
            # Подготовка контейнера
            container_config = {
                "image": language.dockerImage,
                "mem_limit": f"{language.memoryLimitMB}m",
                "network_disabled": True,
                "stdin_open": True,
                "tty": False,
                "detach": True,
                "remove": True,
            }

            # Команда для выполнения
            if language.compileCommand:
                command = f"{language.compileCommand} && {language.runCommand}"
            else:
                command = language.runCommand

            container_config["command"] = ["sh", "-c", command]

            # Создание и запуск контейнера
            container = self.docker_client.containers.run(**container_config)

            # Отправка кода в контейнер
            if stdin:
                container.stdin.write(f"{source_code}\n{stdin}")
            else:
                container.stdin.write(source_code)
            container.stdin.close()

            # Ожидание завершения с таймаутом
            try:
                result = container.wait(timeout=language.timeoutSeconds)
                exit_code = result["StatusCode"]
            except Exception:
                container.kill()
                raise CodeExecutionError("", "Превышен таймаут выполнения")

            # Получение результатов
            stdout = container.logs(stdout=True, stderr=False).decode("utf-8")
            stderr = container.logs(stdout=False, stderr=True).decode("utf-8")

            # Получение статистики
            stats = container.stats(stream=False)
            memory_used = (
                stats.get("memory_stats", {}).get("usage", 0) / 1024 / 1024
            )  # MB

            execution_result = {
                "stdout": stdout,
                "stderr": stderr,
                "exit_code": exit_code,
                "execution_time_ms": 0,  # TODO: Замерить реальное время
                "memory_used_mb": memory_used,
                "container_logs": container.logs().decode("utf-8")[
                    :1000
                ],  # Ограничиваем размер
            }

            logger.info(f"Код выполнен, exit_code: {exit_code}")
            return execution_result

        except Exception as e:
            logger.error(f"Ошибка при выполнении кода: {e}")
            raise CodeExecutionError("", str(e))

    async def create_user_solution(
        self, solution: UserCodeSolution
    ) -> UserCodeSolution:
        """Создание решения пользователя"""
        logger.info(f"Создание решения: {solution.id}")

        try:
            self.session.add(solution)
            self.session.commit()
            self.session.refresh(solution)

            logger.info(f"Решение создано: {solution.id}")
            return solution

        except Exception as e:
            logger.error(f"Ошибка при создании решения: {e}")
            self.session.rollback()
            raise

    async def get_solution_by_id(self, solution_id: str) -> Optional[UserCodeSolution]:
        """Получение решения по ID"""
        logger.info(f"Получение решения по ID: {solution_id}")

        try:
            solution = (
                self.session.query(UserCodeSolution)
                .filter(UserCodeSolution.id == solution_id)
                .first()
            )

            if solution:
                logger.info(f"Решение найдено: {solution_id}")
            else:
                logger.warning(f"Решение не найдено: {solution_id}")

            return solution

        except Exception as e:
            logger.error(f"Ошибка при получении решения: {e}")
            return None

    async def get_user_solutions_for_block(
        self, user_id: int, block_id: str
    ) -> List[UserCodeSolution]:
        """Получение решений пользователя для блока"""
        logger.info(f"Получение решений пользователя {user_id} для блока {block_id}")

        try:
            solutions = (
                self.session.query(UserCodeSolution)
                .filter(
                    UserCodeSolution.userId == user_id,
                    UserCodeSolution.blockId == block_id,
                )
                .order_by(UserCodeSolution.updatedAt.desc())
                .all()
            )

            logger.info(f"Найдено {len(solutions)} решений")
            return solutions

        except Exception as e:
            logger.error(f"Ошибка при получении решений: {e}")
            return []

    async def get_execution_stats(self, user_id: int) -> Dict[str, Any]:
        """Получение статистики выполнений пользователя"""
        logger.info(f"Получение статистики выполнений для пользователя {user_id}")

        try:
            # Общее количество выполнений
            total_executions = (
                self.session.query(func.count(CodeExecution.id))
                .filter(CodeExecution.userId == user_id)
                .scalar()
                or 0
            )

            # Успешные выполнения
            successful_executions = (
                self.session.query(func.count(CodeExecution.id))
                .filter(
                    CodeExecution.userId == user_id,
                    CodeExecution.status == ExecutionStatus.SUCCESS,
                    CodeExecution.exitCode == 0,
                )
                .scalar()
                or 0
            )

            # Среднее время выполнения
            avg_time = (
                self.session.query(func.avg(CodeExecution.executionTimeMs))
                .filter(
                    CodeExecution.userId == user_id,
                    CodeExecution.executionTimeMs.isnot(None),
                )
                .scalar()
                or 0.0
            )

            # Статистика по языкам
            language_stats = (
                self.session.query(
                    SupportedLanguage.language,
                    SupportedLanguage.name,
                    func.count(CodeExecution.id).label("executions"),
                )
                .join(CodeExecution)
                .filter(CodeExecution.userId == user_id)
                .group_by(SupportedLanguage.language, SupportedLanguage.name)
                .all()
            )

            lang_stats_dict = [
                {
                    "language": lang.language,
                    "name": lang.name,
                    "executions": lang.executions,
                }
                for lang in language_stats
            ]

            stats = {
                "totalExecutions": total_executions,
                "successfulExecutions": successful_executions,
                "averageExecutionTime": float(avg_time),
                "languageStats": lang_stats_dict,
            }

            logger.info(f"Статистика получена: {total_executions} выполнений")
            return stats

        except Exception as e:
            logger.error(f"Ошибка при получении статистики: {e}")
            return {
                "totalExecutions": 0,
                "successfulExecutions": 0,
                "averageExecutionTime": 0.0,
                "languageStats": [],
            }

    async def get_test_cases_for_block(self, block_id: str) -> List[TestCase]:
        """Получение тест-кейсов для блока"""
        logger.info(f"Получение тест-кейсов для блока {block_id}")

        try:
            test_cases = (
                self.session.query(TestCase)
                .filter(TestCase.blockId == block_id, TestCase.isActive == True)
                .order_by(TestCase.orderIndex)
                .all()
            )

            logger.info(f"Найдено {len(test_cases)} тест-кейсов")
            return test_cases

        except Exception as e:
            logger.error(f"Ошибка при получении тест-кейсов: {e}")
            return []

    async def get_content_block_by_id(self, block_id: str) -> Optional[ContentBlock]:
        """Получение контент-блока по ID"""
        logger.info(f"Получение контент-блока {block_id}")

        try:
            block = (
                self.session.query(ContentBlock)
                .filter(ContentBlock.id == block_id)
                .first()
            )

            if block:
                logger.info(f"Контент-блок найден: {block_id}")
            else:
                logger.warning(f"Контент-блок не найден: {block_id}")

            return block

        except Exception as e:
            logger.error(f"Ошибка при получении контент-блока: {e}")
            return None
