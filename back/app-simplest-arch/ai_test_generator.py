"""
🤖 AI-генератор тест-кейсов для задач программирования

ИСПОЛЬЗУЕТ ТОЛЬКО:
✅ OpenAI API через ProxyAPI.ru - GPT-4o-mini  
✅ Fallback на паттерны при ошибках
"""

import json
import uuid
import re
import os
from datetime import datetime
from typing import List, Dict, Optional
from dataclasses import dataclass

import aiohttp
from sqlalchemy.orm import Session

from .models import ContentBlock, TestCase
from .schemas import TestCaseAIGenerate


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


class OpenAITestGenerator:
    """🚀 ГЕНЕРАТОР ТЕСТ-КЕЙСОВ через OpenAI + ProxyAPI.ru"""
    
    def __init__(self, config: OpenAIConfig = None):
        self.config = config or OpenAIConfig()
        self.generation_stats = {
            "total_requests": 0,
            "successful_requests": 0,
            "failed_requests": 0,
            "avg_response_time": 0.0
        }
        self.fallback_patterns = self._load_fallback_patterns()
    
    async def generate_test_cases(
        self, 
        db: Session, 
        generate_request: TestCaseAIGenerate
    ) -> List[TestCase]:
        """🎯 ГЛАВНАЯ ФУНКЦИЯ: Генерация тест-кейсов через OpenAI"""
        
        # 1️⃣ Валидация запроса
        block = await self._validate_request(db, generate_request)
        
        # 2️⃣ Анализ задачи
        task_analysis = self._analyze_task(block)
        print(f"📊 Task analysis: {task_analysis}")
        
        # 3️⃣ Генерация через OpenAI
        try:
            patterns = await self._generate_with_openai(block, generate_request, task_analysis)
            if patterns:
                return self._create_test_cases(patterns, generate_request, "openai")
        except Exception as e:
            print(f"❌ OpenAI generation failed: {e}")
        
        # 4️⃣ Fallback на паттерны
        print("🔄 Falling back to pattern-based generation")
        patterns = self._generate_with_patterns(block, generate_request, task_analysis)
        return self._create_test_cases(patterns, generate_request, "patterns")
    
    async def _validate_request(self, db: Session, request: TestCaseAIGenerate) -> ContentBlock:
        """✅ Валидация запроса"""
        block = db.query(ContentBlock).filter(ContentBlock.id == request.blockId).first()
        
        if not block:
            raise ValueError(f"Block {request.blockId} not found")
        
        if not block.codeContent:
            raise ValueError(f"Block {request.blockId} is not a coding task")
        
        return block
    
    async def _generate_with_openai(
        self, 
        block: ContentBlock, 
        request: TestCaseAIGenerate, 
        analysis: Dict
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
                        "content": "You are an expert at generating comprehensive test cases for programming tasks. Always respond with valid JSON."
                    },
                    {
                        "role": "user",
                        "content": prompt
                    }
                ],
                "temperature": self.config.temperature,
                "max_tokens": self.config.max_tokens
            }
            
            headers = {
                "Authorization": f"Bearer {self.config.api_key}",
                "Content-Type": "application/json"
            }
            
            async with aiohttp.ClientSession() as session:
                async with session.post(
                    f"{self.config.base_url}/chat/completions",
                    json=payload,
                    headers=headers,
                    timeout=aiohttp.ClientTimeout(total=self.config.timeout)
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
        self, 
        block: ContentBlock, 
        request: TestCaseAIGenerate, 
        analysis: Dict
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
    "difficulty": "BASIC|INTERMEDIATE|ADVANCED",
    "weight": 1.0
  }}
]

GUIDELINES:
- Create diverse test cases covering normal, edge, and boundary conditions
- Ensure expected outputs are precise and match what the code should produce
- For tasks without input, use empty string ""
- Include both simple and complex scenarios
- Test different input types and sizes where relevant

IMPORTANT: Return ONLY the JSON array, no additional text or markdown formatting.
"""
        return prompt
    
    def _parse_ai_response(self, response: str, request: TestCaseAIGenerate) -> List[TestCasePattern]:
        """🔧 Парсинг ответа OpenAI"""
        
        try:
            # Очистка от markdown
            cleaned = response.strip()
            
            # Удаляем markdown блоки если есть
            if "```json" in cleaned:
                json_match = re.search(r'```json\s*(\[.*?\])\s*```', cleaned, re.DOTALL)
                if json_match:
                    cleaned = json_match.group(1)
            elif "```" in cleaned:
                json_match = re.search(r'```\s*(\[.*?\])\s*```', cleaned, re.DOTALL)
                if json_match:
                    cleaned = json_match.group(1)
            
            # Ищем JSON массив
            if not cleaned.startswith('['):
                json_match = re.search(r'\[.*\]', cleaned, re.DOTALL)
                if json_match:
                    cleaned = json_match.group()
            
            # Парсим JSON
            data = json.loads(cleaned)
            
            if not isinstance(data, list):
                raise ValueError("Response is not a JSON array")
            
            # Создаем паттерны
            patterns = []
            for item in data[:request.count]:
                if not isinstance(item, dict):
                    continue
                
                pattern = TestCasePattern(
                    name=item.get("name", "OpenAI Generated Test"),
                    input=str(item.get("input", "")),
                    expected_output=str(item.get("expected_output", "")),
                    description=item.get("description", "AI generated test case"),
                    difficulty=item.get("difficulty", "BASIC"),
                    weight=float(item.get("weight", 1.0))
                )
                patterns.append(pattern)
            
            return patterns
            
        except Exception as e:
            print(f"⚠️ Failed to parse OpenAI response: {e}")
            print(f"Raw response: {response[:500]}...")
            return []
    
    def _analyze_task(self, block: ContentBlock) -> Dict:
        """📊 Анализ типа задачи"""
        
        code = block.codeContent.lower() if block.codeContent else ""
        text = (block.textContent or "").lower()
        
        analysis = {
            "type": "unknown",
            "language": "python",
            "has_input": "input(" in code or "scanf" in code or "cin" in code,
            "complexity": "basic"
        }
        
        # Определение языка программирования
        if "def " in code and "print(" in code:
            analysis["language"] = "python"
        elif "#include" in code and "printf" in code:
            analysis["language"] = "c"
        elif "public class" in code and "System.out" in code:
            analysis["language"] = "java"
        elif "console.log" in code or "function" in code:
            analysis["language"] = "javascript"
        
        # Определение типа задачи
        if "hello" in code and "world" in code:
            analysis["type"] = "hello_world"
        elif "fibonacci" in text or "фибоначчи" in text:
            analysis["type"] = "fibonacci"
            analysis["complexity"] = "intermediate"
        elif "factorial" in text or "факториал" in text:
            analysis["type"] = "factorial"
            analysis["complexity"] = "intermediate"
        elif "sort" in text or "сортировка" in text:
            analysis["type"] = "sorting"
            analysis["complexity"] = "advanced"
        elif "search" in text or "поиск" in text:
            analysis["type"] = "search"
            analysis["complexity"] = "advanced"
        elif "array" in text or "массив" in text:
            analysis["type"] = "array_processing"
            analysis["complexity"] = "intermediate"
        
        # Определение сложности по ключевым словам
        advanced_keywords = ["class", "import", "lambda", "try", "except", "async", "yield"]
        intermediate_keywords = ["for", "while", "if", "def", "function", "return"]
        
        if any(keyword in code for keyword in advanced_keywords):
            analysis["complexity"] = "advanced"
        elif any(keyword in code for keyword in intermediate_keywords):
            analysis["complexity"] = "intermediate"
        
        return analysis
    
    def _generate_with_patterns(
        self, 
        block: ContentBlock, 
        request: TestCaseAIGenerate, 
        analysis: Dict
    ) -> List[TestCasePattern]:
        """📋 Fallback генерация через паттерны"""
        
        task_type = analysis["type"]
        
        patterns_map = {
            "hello_world": [
                TestCasePattern(
                    name="Basic Hello World Test",
                    input="",
                    expected_output="Hello, World!",
                    description="Standard hello world output test",
                    difficulty="BASIC"
                )
            ],
            "fibonacci": [
                TestCasePattern("Fibonacci Base Case 0", "0", "0", "Test F(0) = 0"),
                TestCasePattern("Fibonacci Base Case 1", "1", "1", "Test F(1) = 1"),
                TestCasePattern("Fibonacci Standard Case", "5", "5", "Test F(5) = 5"),
                TestCasePattern("Fibonacci Larger Case", "10", "55", "Test F(10) = 55")
            ],
            "factorial": [
                TestCasePattern("Factorial Zero", "0", "1", "Test 0! = 1"),
                TestCasePattern("Factorial One", "1", "1", "Test 1! = 1"),
                TestCasePattern("Factorial Five", "5", "120", "Test 5! = 120"),
                TestCasePattern("Factorial Seven", "7", "5040", "Test 7! = 5040")
            ],
            "sorting": [
                TestCasePattern("Sort Empty Array", "[]", "[]", "Test empty array sorting"),
                TestCasePattern("Sort Single Element", "[5]", "[5]", "Test single element"),
                TestCasePattern("Sort Multiple Elements", "[3,1,4,1,5]", "[1,1,3,4,5]", "Test multiple elements"),
                TestCasePattern("Sort Already Sorted", "[1,2,3,4,5]", "[1,2,3,4,5]", "Test already sorted array")
            ]
        }
        
        default_patterns = [
            TestCasePattern(
                name="Basic Functionality Test",
                input="",
                expected_output="Expected Output",
                description="Basic functionality verification",
                difficulty="BASIC"
            ),
            TestCasePattern(
                name="Edge Case Test",
                input="edge_case_input",
                expected_output="edge_case_output",
                description="Edge case handling verification",
                difficulty="INTERMEDIATE"
            )
        ]
        
        patterns = patterns_map.get(task_type, default_patterns)
        return patterns[:request.count]
    
    def _create_test_cases(
        self, 
        patterns: List[TestCasePattern], 
        request: TestCaseAIGenerate, 
        provider: str
    ) -> List[TestCase]:
        """🏗️ Создание объектов TestCase"""
        
        test_cases = []
        for i, pattern in enumerate(patterns):
            test_case = TestCase(
                id=str(uuid.uuid4()),
                blockId=request.blockId,
                name=pattern.name,
                description=pattern.description,
                input=pattern.input,
                expectedOutput=pattern.expected_output,
                difficulty=pattern.difficulty,
                weight=pattern.weight,
                orderIndex=i,
                isAIGenerated=(provider == "openai"),
                generatedAt=datetime.now(),
                generationModel=f"{provider}-{self.config.model if provider == 'openai' else 'patterns'}"
            )
            test_cases.append(test_case)
        
        return test_cases
    
    def _load_fallback_patterns(self) -> Dict:
        """📚 Загрузка fallback паттернов"""
        return {
            "hello_world": ["Hello, World!"],
            "fibonacci": ["0", "1", "1", "2", "3", "5", "8"],
            "factorial": ["1", "1", "2", "6", "24", "120"]
        }
    
    def _update_avg_response_time(self, duration: float):
        """⏱️ Обновление средней время ответа"""
        total = self.generation_stats["successful_requests"]
        if total == 1:
            self.generation_stats["avg_response_time"] = duration
        else:
            current_avg = self.generation_stats["avg_response_time"]
            self.generation_stats["avg_response_time"] = (current_avg * (total - 1) + duration) / total
    
    def get_stats(self) -> Dict:
        """📈 Статистика использования"""
        return {
            "provider": "openai",
            "model": self.config.model,
            "generation_stats": self.generation_stats,
            "config": {
                "base_url": self.config.base_url,
                "model": self.config.model,
                "timeout": self.config.timeout
            }
        }


# Глобальный экземпляр
openai_generator = OpenAITestGenerator() 