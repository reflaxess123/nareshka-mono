"""
🤖 AI-генератор тест-кейсов для задач программирования

ИСПОЛЬЗУЕТ ТОЛЬКО:
✅ OpenAI API через ProxyAPI.ru - GPT-4o-mini
✅ Fallback на паттерны при ошибках
"""

import json
import os
import uuid
from dataclasses import dataclass
from datetime import datetime
from typing import Dict, List, Optional

import aiohttp

from app.core.logging import get_logger
from app.features.code_editor.dto.test_case_dto import TestCaseAIGenerate
from app.features.content.repositories.content_repository import ContentRepository
from app.features.task.repositories.task_repository import TaskRepository
from app.shared.entities.content import ContentBlock
from app.shared.entities.progress_types import TestCase

logger = get_logger(__name__)


@dataclass
class OpenAIConfig:
    """⚙️ Конфигурация OpenAI через ProxyAPI.ru"""

    # 🤖 OpenAI через ProxyAPI.ru
    base_url: str = "https://api.proxyapi.ru/openai/v1"
    api_key: str = os.getenv("PROXYAPI_KEY", "")
    model: str = "gpt-4o-mini"
    timeout: int = 30
    max_tokens: int = 2000
    temperature: float = 0.2

    def __post_init__(self):
        if not self.api_key:
            raise ValueError("PROXYAPI_KEY environment variable is required!")


@dataclass
class TestCasePattern:
    """📋 Паттерн для генерации тест-кейса"""

    name: str
    input: str
    expected_output: str
    description: str
    difficulty: str = "BASIC"
    weight: float = 1.0


class AITestGeneratorService:
    """🚀 Сервис генерации тест-кейсов через OpenAI + ProxyAPI.ru"""

    def __init__(
        self,
        content_repository: ContentRepository,
        task_repository: TaskRepository,
        config: OpenAIConfig = None,
    ):
        self.content_repository = content_repository
        self.task_repository = task_repository
        self.config = config or OpenAIConfig()
        self.generation_stats = {
            "total_requests": 0,
            "successful_requests": 0,
            "failed_requests": 0,
            "avg_response_time": 0.0,
        }
        self.fallback_patterns = self._load_fallback_patterns()

    async def generate_test_cases(
        self, generate_request: TestCaseAIGenerate
    ) -> List[TestCase]:
        """🎯 ГЛАВНАЯ ФУНКЦИЯ: Генерация тест-кейсов через OpenAI"""

        # 1️⃣ Валидация запроса
        block = await self._validate_request(generate_request)

        # 2️⃣ Анализ задачи
        task_analysis = self._analyze_task(block)
        logger.info(f"📊 Task analysis: {task_analysis}")

        # 3️⃣ Генерация через OpenAI
        try:
            patterns = await self._generate_with_openai(
                block, generate_request, task_analysis
            )
            if patterns:
                return await self._create_test_cases(
                    patterns, generate_request, "openai"
                )
        except Exception as e:
            logger.error(f"❌ OpenAI generation failed: {e}")

        # 4️⃣ Fallback на паттерны
        logger.info("🔄 Falling back to pattern-based generation")
        patterns = self._generate_with_patterns(block, generate_request, task_analysis)
        return await self._create_test_cases(patterns, generate_request, "patterns")

    async def _validate_request(self, request: TestCaseAIGenerate) -> ContentBlock:
        """✅ Валидация запроса"""
        block = await self.content_repository.get_by_id(request.blockId)

        if not block:
            raise ValueError(f"Block {request.blockId} not found")

        if not block.codeContent:
            raise ValueError(f"Block {request.blockId} is not a coding task")

        return block

    async def _generate_with_openai(
        self, block: ContentBlock, request: TestCaseAIGenerate, analysis: Dict
    ) -> List[TestCasePattern]:
        """🤖 Генерация через OpenAI API (ProxyAPI.ru)"""

        start_time = datetime.now()
        self.generation_stats["total_requests"] += 1

        try:
            prompt = self._build_smart_prompt(block, request, analysis)

            payload = {
                "model": self.config.model,
                "messages": [
                    {
                        "role": "system",
                        "content": "You are an expert at generating comprehensive test cases for programming tasks. Always respond with valid JSON.",
                    },
                    {"role": "user", "content": prompt},
                ],
                "temperature": self.config.temperature,
                "max_tokens": self.config.max_tokens,
            }

            headers = {
                "Authorization": f"Bearer {self.config.api_key}",
                "Content-Type": "application/json",
            }

            async with aiohttp.ClientSession() as session, session.post(
                f"{self.config.base_url}/chat/completions",
                json=payload,
                headers=headers,
                timeout=aiohttp.ClientTimeout(total=self.config.timeout),
            ) as response:
                if response.status != 200:
                    text = await response.text()
                    raise Exception(f"OpenAI API error {response.status}: {text}")

                result = await response.json()
                ai_response = result["choices"][0]["message"]["content"]

                # Обновляем статистику
                duration = (datetime.now() - start_time).total_seconds()
                self.generation_stats["successful_requests"] += 1
                self._update_avg_response_time(duration)

                return self._parse_ai_response(ai_response, request)

        except Exception as e:
            self.generation_stats["failed_requests"] += 1
            raise e

    def _build_smart_prompt(
        self, block: ContentBlock, request: TestCaseAIGenerate, analysis: Dict
    ) -> str:
        """📝 Умный промпт для OpenAI"""

        prompt = f"""
Generate {request.count} comprehensive test cases for this programming exercise.

CODE TO TEST:
```{analysis.get('language', 'python')}
{block.codeContent}
```

TASK DESCRIPTION:
{block.textContent or "No description provided"}

ANALYSIS:
- Task type: {analysis['type']}
- Complexity: {analysis['complexity']}
- Has input: {analysis['has_input']}
- Language: {analysis['language']}

REQUIREMENTS:
- Difficulty level: {request.difficulty}
- Include edge cases: {request.includeEdgeCases}
- Include error cases: {request.includeErrorCases}

Generate a JSON array with this exact structure:
[
  {{
    "name": "Descriptive test case name",
    "description": "What this test validates",
    "input": "input data (empty string if no input needed)",
    "expected_output": "exact expected output",
    "difficulty": "{request.difficulty}",
    "weight": 1.0
  }}
]

Requirements:
1. Create exactly {request.count} test cases
2. Each test case should be unique and meaningful
3. Cover different scenarios: basic cases, edge cases, boundary conditions
4. If includeEdgeCases=true, include edge cases like empty input, large numbers, special characters
5. If includeErrorCases=true, include inputs that should produce errors or special handling
6. Make expected_output precise and exact - exactly what the code should output
7. Ensure input and expected_output are realistic for the given code
8. Use clear, descriptive names for each test case

Return ONLY the JSON array, no additional text or markdown formatting.
        """

        return prompt.strip()

    def _parse_ai_response(
        self, response: str, request: TestCaseAIGenerate
    ) -> List[TestCasePattern]:
        """🔍 Парсинг ответа от OpenAI"""
        try:
            # Очищаем ответ от markdown и лишних символов
            cleaned_response = response.strip()
            if cleaned_response.startswith("```json"):
                cleaned_response = cleaned_response[7:]
            if cleaned_response.startswith("```"):
                cleaned_response = cleaned_response[3:]
            if cleaned_response.endswith("```"):
                cleaned_response = cleaned_response[:-3]

            # Парсим JSON
            test_cases_data = json.loads(cleaned_response)

            patterns = []
            for i, tc_data in enumerate(test_cases_data):
                if i >= request.count:  # Ограничиваем количество
                    break

                pattern = TestCasePattern(
                    name=tc_data.get("name", f"Test Case {i+1}"),
                    input=tc_data.get("input", ""),
                    expected_output=tc_data.get("expected_output", ""),
                    description=tc_data.get("description", ""),
                    difficulty=tc_data.get("difficulty", request.difficulty),
                    weight=tc_data.get("weight", 1.0),
                )
                patterns.append(pattern)

            logger.info(f"✅ Parsed {len(patterns)} test cases from AI response")
            return patterns

        except (json.JSONDecodeError, KeyError) as e:
            logger.error(f"❌ Failed to parse AI response: {e}")
            logger.error(f"Raw response: {response[:200]}...")
            return []

    def _analyze_task(self, block: ContentBlock) -> Dict:
        """🔍 Анализ задачи программирования"""

        code = block.codeContent or ""
        text = block.textContent or ""

        # Определяем язык программирования
        language = self._detect_language(code, block.codeLanguage)

        # Анализируем тип задачи
        task_type = self._detect_task_type(code, text)

        # Определяем сложность
        complexity = self._assess_complexity(code, text)

        # Проверяем наличие input/output
        has_input = self._has_input_handling(code, language)

        return {
            "language": language,
            "type": task_type,
            "complexity": complexity,
            "has_input": has_input,
            "code_lines": len(code.split("\n")),
            "has_loops": any(
                keyword in code.lower() for keyword in ["for", "while", "loop"]
            ),
            "has_conditions": any(
                keyword in code.lower() for keyword in ["if", "else", "switch", "case"]
            ),
            "has_functions": any(
                keyword in code.lower() for keyword in ["def", "function", "func"]
            ),
        }

    def _detect_language(self, code: str, declared_language: Optional[str]) -> str:
        """🔍 Определение языка программирования"""
        if declared_language:
            return declared_language.lower()

        # Простые эвристики
        if "def " in code or "import " in code or "print(" in code:
            return "python"
        elif "function" in code or "console.log" in code or "const " in code:
            return "javascript"
        elif "#include" in code or "int main" in code:
            return "cpp"
        elif "public class" in code or "System.out" in code:
            return "java"

        return "python"  # По умолчанию

    def _detect_task_type(self, code: str, text: str) -> str:
        """🔍 Определение типа задачи"""
        combined = (code + " " + text).lower()

        if any(word in combined for word in ["sort", "sorted", "order"]):
            return "sorting"
        elif any(word in combined for word in ["search", "find", "index"]):
            return "search"
        elif any(word in combined for word in ["math", "calculate", "sum", "average"]):
            return "math"
        elif any(word in combined for word in ["string", "text", "char"]):
            return "string_processing"
        elif any(word in combined for word in ["array", "list", "data"]):
            return "data_processing"
        else:
            return "general"

    def _assess_complexity(self, code: str, text: str) -> str:
        """🔍 Оценка сложности задачи"""
        lines = len(code.split("\n"))

        if lines <= 10:
            return "basic"
        elif lines <= 25:
            return "intermediate"
        else:
            return "advanced"

    def _has_input_handling(self, code: str, language: str) -> bool:
        """🔍 Проверка наличия обработки ввода"""
        if language == "python":
            return "input(" in code or "sys.stdin" in code
        elif language == "javascript":
            return "prompt(" in code or "readline" in code
        else:
            return "input" in code.lower()

    def _generate_with_patterns(
        self, block: ContentBlock, request: TestCaseAIGenerate, analysis: Dict
    ) -> List[TestCasePattern]:
        """📋 Генерация с помощью паттернов (Fallback)"""

        patterns = []
        task_type = analysis["type"]

        # Выбираем подходящие паттерны
        if task_type in self.fallback_patterns:
            base_patterns = self.fallback_patterns[task_type]

            for i in range(min(request.count, len(base_patterns))):
                pattern = base_patterns[i]
                patterns.append(
                    TestCasePattern(
                        name=f"{pattern['name']} - Generated",
                        input=pattern["input"],
                        expected_output=pattern["expected_output"],
                        description=pattern["description"],
                        difficulty=request.difficulty,
                    )
                )

        # Дополняем универсальными паттернами если нужно
        while len(patterns) < request.count:
            patterns.append(
                TestCasePattern(
                    name=f"Test Case {len(patterns) + 1}",
                    input="",
                    expected_output="Expected result",
                    description="Basic test case",
                    difficulty=request.difficulty,
                )
            )

        return patterns[: request.count]

    async def _create_test_cases(
        self,
        patterns: List[TestCasePattern],
        request: TestCaseAIGenerate,
        provider: str,
    ) -> List[TestCase]:
        """🏗️ Создание TestCase объектов из паттернов"""

        test_cases = []
        current_time = datetime.now()

        for i, pattern in enumerate(patterns):
            test_case = TestCase(
                id=str(uuid.uuid4()),
                blockId=request.blockId,
                name=pattern.name,
                description=pattern.description,
                input=pattern.input,
                expectedOutput=pattern.expected_output,
                isPublic=i < 2,  # Первые 2 тест-кейса публичные
                difficulty=pattern.difficulty,
                weight=pattern.weight,
                timeoutSeconds=30,
                isActive=True,
                orderIndex=i,
                isAIGenerated=provider == "openai",
                executionCount=0,
                passRate=0.0,
                createdAt=current_time,
                updatedAt=current_time,
                generationPrompt=f"Generated by {provider}"
                if provider == "openai"
                else None,
                generatedAt=current_time if provider == "openai" else None,
                generationModel=self.config.model if provider == "openai" else None,
            )
            test_cases.append(test_case)

        # Сохраняем в репозитории
        for test_case in test_cases:
            await self.task_repository.create_test_case(test_case)

        return test_cases

    def _load_fallback_patterns(self) -> Dict:
        """📋 Загрузка fallback паттернов"""
        return {
            "sorting": [
                {
                    "name": "Basic Sort",
                    "input": "[3, 1, 4, 1, 5]",
                    "expected_output": "[1, 1, 3, 4, 5]",
                    "description": "Sort a simple array",
                }
            ],
            "math": [
                {
                    "name": "Basic Calculation",
                    "input": "2 + 2",
                    "expected_output": "4",
                    "description": "Simple arithmetic",
                }
            ],
            "general": [
                {
                    "name": "Basic Test",
                    "input": "",
                    "expected_output": "Expected output",
                    "description": "Basic functionality test",
                }
            ],
        }

    def _update_avg_response_time(self, duration: float):
        """📊 Обновление средней скорости ответа"""
        current_avg = self.generation_stats["avg_response_time"]
        total_successful = self.generation_stats["successful_requests"]

        if total_successful == 1:
            self.generation_stats["avg_response_time"] = duration
        else:
            # Скользящее среднее
            new_avg = (
                (current_avg * (total_successful - 1)) + duration
            ) / total_successful
            self.generation_stats["avg_response_time"] = new_avg

    def get_stats(self) -> Dict:
        """📊 Получение статистики генерации"""
        return {
            **self.generation_stats,
            "success_rate": (
                self.generation_stats["successful_requests"]
                / max(self.generation_stats["total_requests"], 1)
            )
            * 100,
        }
