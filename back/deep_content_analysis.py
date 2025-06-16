#!/usr/bin/env python3

import logging
import re
import json
from collections import defaultdict, Counter
from typing import List, Dict, Any, Tuple, Set
from dataclasses import dataclass, asdict
from sqlalchemy.orm import sessionmaker
from sqlalchemy import create_engine
import difflib

from app.config import settings
from app.models import ContentBlock, ContentFile, UserContentProgress

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@dataclass
class TaskAnalysis:
    """Детальный анализ одной задачи"""
    id: str
    title: str
    category: str
    subcategory: str
    path_titles: List[str]
    
    # Контент
    text_content: str
    code_content: str
    code_language: str
    code_lines: int
    
    # Анализ сложности
    complexity_score: float
    difficulty_factors: List[str]
    
    # Концепции и темы
    programming_concepts: List[str]
    js_features_used: List[str]
    keywords: Set[str]
    
    # Связи с другими задачами
    similar_tasks: List[str]
    prerequisite_concepts: List[str]
    
    # Метаданные
    estimated_time_minutes: int
    target_skill_level: str
    
    # НОВЫЕ ПОЛЯ для более точного анализа
    path_depth: int
    order_in_file: int
    pedagogical_type: str  # "explanation", "example", "exercise", "challenge"
    text_complexity: float
    user_success_rate: float
    avg_solve_time: float

@dataclass
class ConceptCluster:
    """Кластер задач по концепции"""
    concept_name: str
    task_ids: List[str]
    difficulty_range: Tuple[float, float]
    common_patterns: List[str]
    learning_sequence: List[str]

@dataclass
class PathStructureAnalysis:
    """Анализ структуры pathTitles"""
    full_path: str
    depth: int
    parent_path: str
    task_count: int
    avg_complexity: float
    completion_rate: float
    recommended_order: List[str]

class DeepContentAnalyzer:
    """Глубокий анализ содержания задач для mindmap"""
    
    def __init__(self):
        self.js_concepts = {
            # Базовые концепции
            'variables': ['let', 'const', 'var'],
            'functions': ['function', '=>', 'return'],
            'conditionals': ['if', 'else', 'switch', 'case'],
            'loops': ['for', 'while', 'forEach', 'map', 'filter'],
            
            # Структуры данных
            'arrays': ['Array', r'\[\]', 'push', 'pop', 'slice', 'splice', 'indexOf'],
            'objects': ['Object', r'\{\}', 'keys', 'values', 'entries'],
            'strings': ['String', 'charAt', 'substring', 'split', 'join'],
            
            # Продвинутые концепции
            'classes': ['class', 'constructor', 'extends', 'super'],
            'async': ['async', 'await', 'Promise', r'\.then', r'\.catch'],
            'closures': ['closure', 'lexical', 'scope'],
            'destructuring': [r'\.\.\.', r'\{.*\}.*=', r'\[.*\].*='],
            'modules': ['import', 'export', 'require'],
            
            # ES6+ фичи
            'arrow_functions': ['=>'],
            'template_literals': ['`', r'\$\{'],
            'spread_operator': [r'\.\.\.'],
            'rest_parameters': [r'\.\.\.\\w+\)'],
            
            # DOM и Web APIs
            'dom': ['document', 'getElementById', 'querySelector'],
            'events': ['addEventListener', 'onClick', 'onSubmit'],
            
            # Алгоритмы
            'sorting': ['sort', 'bubble', 'quick', 'merge'],
            'searching': ['find', 'search', 'binary', 'linear'],
            'recursion': ['recursive', 'recursion', 'factorial'],
            
            # Паттерны
            'error_handling': ['try', 'catch', 'throw', 'finally'],
            'regex': ['RegExp', r'\/.*\/', 'test', 'match'],
            'functional': ['map', 'filter', 'reduce', 'curry'],
        }
        
        self.complexity_indicators = {
            'high': ['async', 'Promise', 'class', 'prototype', 'closure', 'recursive', 'regex'],
            'medium': ['forEach', 'map', 'filter', 'destructuring', '=>', 'template'],
            'low': ['if', 'for', 'function', 'return', 'console']
        }

    def analyze_all_tasks(self) -> Dict[str, Any]:
        """Полный анализ всех задач"""
        # Подключение к базе данных
        db_url = settings.database_url
        if db_url.startswith("postgres://"):
            db_url = db_url.replace("postgres://", "postgresql://", 1)
        
        engine = create_engine(db_url)
        SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
        db = SessionLocal()
        
        try:
            logger.info("🔍 НАЧИНАЕМ ГЛУБОКИЙ АНАЛИЗ СОДЕРЖАНИЯ ЗАДАЧ...")
            
            # Получаем все блоки с кодом И пользовательский прогресс
            blocks = db.query(ContentBlock).filter(
                ContentBlock.codeContent.isnot(None),
                ContentBlock.codeContent != ""
            ).all()
            
            # Получаем статистику пользователей
            user_stats = self.get_user_statistics(db, blocks)
            
            logger.info(f"📊 Анализируем {len(blocks)} блоков...")
            
            # Анализируем каждую задачу детально
            task_analyses = []
            for i, block in enumerate(blocks):
                if i % 50 == 0:
                    logger.info(f"   Проанализировано {i}/{len(blocks)}...")
                
                analysis = self.analyze_single_task(block, user_stats.get(block.id, {}))
                task_analyses.append(analysis)
            
            logger.info("🧠 Анализируем связи между задачами...")
            
            # Находим связи между задачами
            task_connections = self.find_task_connections(task_analyses)
            
            # Группируем задачи по концепциям
            concept_clusters = self.create_concept_clusters(task_analyses)
            
            # Определяем последовательности изучения
            learning_sequences = self.determine_learning_sequences(task_analyses, concept_clusters)
            
            # Анализируем структуру pathTitles ДЕТАЛЬНО
            path_structure = self.analyze_path_structure_detailed(task_analyses)
            
            # Анализируем педагогические паттерны
            pedagogical_analysis = self.analyze_pedagogical_patterns(task_analyses)
            
            # НОВАЯ ФУНКЦИЯ: Создаем структуру по темам
            logger.info("🎯 Создаем структуру по основным темам...")
            topic_structure = self.create_topic_based_structure(task_analyses)
            
            return {
                'task_analyses': task_analyses,
                'task_connections': task_connections,
                'concept_clusters': concept_clusters,
                'learning_sequences': learning_sequences,
                'path_structure': path_structure,
                'pedagogical_analysis': pedagogical_analysis,
                'user_statistics': user_stats,
                'summary_stats': self.generate_summary_stats(task_analyses),
                'topic_structure': topic_structure  # Новое поле
            }
            
        finally:
            db.close()

    def get_user_statistics(self, db, blocks: List[ContentBlock]) -> Dict[str, Dict]:
        """Получает статистику пользователей по задачам"""
        user_stats = {}
        block_ids = [block.id for block in blocks]
        
        # Получаем прогресс пользователей
        progress_records = db.query(UserContentProgress).filter(
            UserContentProgress.blockId.in_(block_ids)
        ).all()
        
        # Группируем по блокам
        from collections import defaultdict
        block_progress = defaultdict(list)
        for progress in progress_records:
            block_progress[progress.blockId].append(progress)
        
        # Вычисляем статистику для каждого блока
        for block_id, progresses in block_progress.items():
            total_users = len(progresses)
            solved_users = len([p for p in progresses if p.solvedCount > 0])
            success_rate = solved_users / total_users if total_users > 0 else 0.0
            
            user_stats[block_id] = {
                'total_users': total_users,
                'solved_users': solved_users,
                'success_rate': success_rate,
                'avg_attempts': sum(p.solvedCount for p in progresses) / total_users if total_users > 0 else 0.0
            }
        
        return user_stats

    def analyze_single_task(self, block: ContentBlock, user_stats: Dict) -> TaskAnalysis:
        """Детальный анализ одной задачи"""
        
        # Базовая информация
        file_info = block.file if hasattr(block, 'file') and block.file else None
        category = file_info.mainCategory if file_info else "Unknown"
        subcategory = file_info.subCategory if file_info else "Unknown"
        
        # Анализ кода
        code_content = block.codeContent or ""
        text_content = block.textContent or ""
        code_lines = len([line for line in code_content.split('\n') if line.strip()])
        
        # Определяем концепции
        programming_concepts = self.identify_concepts(code_content, text_content)
        js_features = self.identify_js_features(code_content)
        
        # Анализ сложности
        complexity_score, difficulty_factors = self.calculate_complexity(code_content, text_content)
        
        # Извлекаем ключевые слова
        keywords = self.extract_keywords(code_content, text_content, block.blockTitle)
        
        # Определяем уровень навыков
        target_skill_level = self.determine_skill_level(complexity_score, programming_concepts)
        
        # Оценка времени
        estimated_time = self.estimate_time(code_content, text_content, complexity_score)
        
        # Определяем пререквизиты
        prerequisites = self.identify_prerequisites(programming_concepts, js_features)
        
        # НОВЫЕ ПОЛЯ для более точного анализа
        path_depth = len(block.pathTitles) if block.pathTitles else 0
        order_in_file = block.orderInFile if hasattr(block, 'orderInFile') else 0
        pedagogical_type = self.determine_pedagogical_type(text_content, code_content, block.blockTitle)
        text_complexity = self.calculate_text_complexity(text_content)
        user_success_rate = user_stats.get('success_rate', 0.0)
        avg_solve_time = user_stats.get('avg_attempts', 0.0)
        
        return TaskAnalysis(
            id=block.id,
            title=block.blockTitle,
            category=category,
            subcategory=subcategory,
            path_titles=block.pathTitles or [],
            text_content=text_content[:500] + "..." if len(text_content) > 500 else text_content,
            code_content=code_content,
            code_language=block.codeLanguage or "js",
            code_lines=code_lines,
            complexity_score=complexity_score,
            difficulty_factors=difficulty_factors,
            programming_concepts=programming_concepts,
            js_features_used=js_features,
            keywords=keywords,
            similar_tasks=[],  # Заполним позже
            prerequisite_concepts=prerequisites,
            estimated_time_minutes=estimated_time,
            target_skill_level=target_skill_level,
            path_depth=path_depth,
            order_in_file=order_in_file,
            pedagogical_type=pedagogical_type,
            text_complexity=text_complexity,
            user_success_rate=user_success_rate,
            avg_solve_time=avg_solve_time
        )

    def identify_concepts(self, code: str, text: str) -> List[str]:
        """Определяет программистские концепции в задаче"""
        content = (code + " " + text).lower()
        found_concepts = []
        
        for concept, patterns in self.js_concepts.items():
            for pattern in patterns:
                if re.search(pattern, content, re.IGNORECASE):
                    found_concepts.append(concept)
                    break
        
        return found_concepts

    def identify_js_features(self, code: str) -> List[str]:
        """Определяет используемые JS фичи"""
        features = []
        
        # ES6+ фичи
        if '=>' in code:
            features.append('arrow_functions')
        if '...' in code:
            features.append('spread_operator')
        if '`' in code and '${' in code:
            features.append('template_literals')
        if re.search(r'const\s*\{.*\}\s*=', code):
            features.append('object_destructuring')
        if re.search(r'const\s*\[.*\]\s*=', code):
            features.append('array_destructuring')
        
        # Async/await
        if 'async' in code or 'await' in code:
            features.append('async_await')
        if 'Promise' in code:
            features.append('promises')
        
        # Классы
        if 'class ' in code:
            features.append('es6_classes')
        if 'constructor' in code:
            features.append('constructor')
        if 'extends' in code:
            features.append('inheritance')
        
        # Функциональное программирование
        fp_methods = ['map', 'filter', 'reduce', 'forEach', 'find', 'some', 'every']
        for method in fp_methods:
            if f'.{method}(' in code:
                features.append(f'array_{method}')
        
        return features

    def calculate_complexity(self, code: str, text: str) -> Tuple[float, List[str]]:
        """Вычисляет сложность задачи и факторы сложности"""
        complexity = 0.0
        factors = []
        
        # Базовая сложность от длины кода
        lines = len([line for line in code.split('\n') if line.strip()])
        if lines > 50:
            complexity += 2.0
            factors.append(f"Длинный код ({lines} строк)")
        elif lines > 20:
            complexity += 1.0
            factors.append(f"Средний код ({lines} строк)")
        
        # Сложность от вложенности
        brace_depth = 0
        max_depth = 0
        for char in code:
            if char == '{':
                brace_depth += 1
                max_depth = max(max_depth, brace_depth)
            elif char == '}':
                brace_depth -= 1
        
        if max_depth > 4:
            complexity += 2.0
            factors.append(f"Глубокая вложенность ({max_depth})")
        elif max_depth > 2:
            complexity += 1.0
            factors.append(f"Средняя вложенность ({max_depth})")
        
        # Сложность от индикаторов
        content = (code + " " + text).lower()
        for level, indicators in self.complexity_indicators.items():
            count = sum(1 for indicator in indicators if indicator in content)
            if level == 'high':
                complexity += count * 1.5
                if count > 0:
                    factors.append(f"Сложные концепции ({count})")
            elif level == 'medium':
                complexity += count * 0.5
                if count > 2:
                    factors.append(f"Средние концепции ({count})")
        
        # Алгоритмическая сложность
        if any(word in content for word in ['recursive', 'recursion', 'fibonacci', 'factorial']):
            complexity += 3.0
            factors.append("Рекурсия")
        
        if any(word in content for word in ['sort', 'bubble', 'quick', 'merge', 'heap']):
            complexity += 2.0
            factors.append("Алгоритмы сортировки")
        
        if any(word in content for word in ['tree', 'graph', 'linked list', 'queue', 'stack']):
            complexity += 2.5
            factors.append("Структуры данных")
        
        return round(complexity, 2), factors

    def extract_keywords(self, code: str, text: str, title: str) -> Set[str]:
        """Извлекает ключевые слова из задачи"""
        content = f"{title} {text} {code}".lower()
        
        # Убираем комментарии и строки
        content = re.sub(r'//.*$', '', content, flags=re.MULTILINE)
        content = re.sub(r'/\*.*?\*/', '', content, flags=re.DOTALL)
        content = re.sub(r'"[^"]*"', '', content)
        content = re.sub(r"'[^']*'", '', content)
        
        # Извлекаем слова
        words = re.findall(r'\b[a-zA-Z]{3,}\b', content)
        
        # Фильтруем стоп-слова
        stop_words = {
            'function', 'return', 'const', 'let', 'var', 'for', 'while', 'if', 'else',
            'true', 'false', 'null', 'undefined', 'this', 'new', 'class', 'extends',
            'console', 'log', 'length', 'push', 'pop', 'shift', 'unshift'
        }
        
        keywords = set(word for word in words if word not in stop_words and len(word) > 2)
        return keywords

    def determine_skill_level(self, complexity: float, concepts: List[str]) -> str:
        """Определяет целевой уровень навыков"""
        advanced_concepts = ['classes', 'async', 'closures', 'recursion', 'modules']
        
        if complexity >= 5.0 or any(concept in advanced_concepts for concept in concepts):
            return "advanced"
        elif complexity >= 2.0 or len(concepts) >= 4:
            return "intermediate"
        else:
            return "beginner"

    def estimate_time(self, code: str, text: str, complexity: float) -> int:
        """Оценивает время изучения в минутах"""
        base_time = 15  # минимальное время
        
        # Время на чтение
        text_words = len(text.split()) if text else 0
        reading_time = text_words / 3  # 3 слова в секунду, переводим в минуты
        
        # Время на анализ кода
        code_lines = len([line for line in code.split('\n') if line.strip()])
        code_time = code_lines * 0.5  # 30 секунд на строку
        
        # Модификатор сложности
        complexity_modifier = 1 + (complexity / 10)
        
        total_time = int((base_time + reading_time + code_time) * complexity_modifier)
        return min(max(total_time, 10), 120)  # от 10 до 120 минут

    def identify_prerequisites(self, concepts: List[str], features: List[str]) -> List[str]:
        """Определяет необходимые предварительные знания"""
        prerequisites = []
        
        # Базовые пререквизиты
        concept_deps = {
            'arrays': ['variables', 'functions'],
            'objects': ['variables', 'functions'],
            'classes': ['objects', 'functions'],
            'async': ['functions', 'objects'],
            'closures': ['functions', 'variables'],
            'modules': ['functions', 'objects']
        }
        
        for concept in concepts:
            if concept in concept_deps:
                prerequisites.extend(concept_deps[concept])
        
        return list(set(prerequisites))

    def find_task_connections(self, analyses: List[TaskAnalysis]) -> Dict[str, List[str]]:
        """Находит связи между задачами на основе реального содержания"""
        connections = {}
        
        for i, task in enumerate(analyses):
            task_connections = []
            
            # 1. Связи по pathTitles (одинаковые пути)
            same_path_tasks = [
                other.id for other in analyses 
                if other.id != task.id and other.path_titles == task.path_titles
            ]
            task_connections.extend(same_path_tasks[:3])  # максимум 3
            
            # 2. Связи по концепциям (общие JS features)
            concept_similarity_tasks = []
            for other in analyses:
                if other.id != task.id:
                    common_concepts = set(task.js_features_used) & set(other.js_features_used)
                    if len(common_concepts) >= 2:  # минимум 2 общих концепции
                        concept_similarity_tasks.append((other.id, len(common_concepts)))
            
            # Берем топ-3 по количеству общих концепций
            concept_similarity_tasks.sort(key=lambda x: x[1], reverse=True)
            task_connections.extend([task_id for task_id, _ in concept_similarity_tasks[:3]])
            
            # 3. Связи по сложности (похожие по уровню)
            similar_complexity_tasks = [
                other.id for other in analyses 
                if other.id != task.id and 
                abs(other.complexity_score - task.complexity_score) <= 0.3
            ]
            task_connections.extend(similar_complexity_tasks[:2])  # максимум 2
            
            # 4. Связи по педагогическому типу
            same_pedagogy_tasks = [
                other.id for other in analyses 
                if other.id != task.id and other.pedagogical_type == task.pedagogical_type
            ]
            task_connections.extend(same_pedagogy_tasks[:2])  # максимум 2
            
            # Убираем дубликаты и ограничиваем
            connections[task.id] = list(set(task_connections))[:5]  # максимум 5 связей
            
        return connections

    def create_concept_clusters(self, analyses: List[TaskAnalysis]) -> Dict[str, List[str]]:
        """Группирует задачи по концепциям на основе реального анализа"""
        clusters = {}
        
        # Группировка по основным JS концепциям
        main_concepts = ['arrays', 'functions', 'objects', 'strings', 'async', 'classes', 'regex']
        
        for concept in main_concepts:
            # Находим задачи, которые содержат эту концепцию
            tasks_with_concept = [
                analysis.id for analysis in analyses 
                if concept in analysis.programming_concepts
            ]
            
            if tasks_with_concept:
                clusters[concept] = tasks_with_concept
        
        # Группировка по pathTitles (первый элемент пути)
        path_clusters = {}
        for analysis in analyses:
            if analysis.path_titles:
                main_path = analysis.path_titles[0]
                if main_path not in path_clusters:
                    path_clusters[main_path] = []
                path_clusters[main_path].append(analysis.id)
        
        # Добавляем path-based кластеры
        for path_name, task_ids in path_clusters.items():
            if len(task_ids) >= 3:  # минимум 3 задачи в кластере
                clusters[f"path_{path_name}"] = task_ids
        
        # Группировка по сложности
        beginner_tasks = [a.id for a in analyses if a.complexity_score <= 1.0]
        intermediate_tasks = [a.id for a in analyses if 1.0 < a.complexity_score <= 2.5]
        advanced_tasks = [a.id for a in analyses if a.complexity_score > 2.5]
        
        if beginner_tasks:
            clusters['difficulty_beginner'] = beginner_tasks
        if intermediate_tasks:
            clusters['difficulty_intermediate'] = intermediate_tasks
        if advanced_tasks:
            clusters['difficulty_advanced'] = advanced_tasks
        
        return clusters

    def determine_learning_sequences(self, analyses: List[TaskAnalysis], 
                                   concept_clusters: Dict[str, List[str]]) -> Dict[str, List[str]]:
        """Определяет оптимальные последовательности изучения"""
        sequences = {}
        
        # 1. Последовательность по сложности внутри каждого кластера
        for cluster_name, task_ids in concept_clusters.items():
            if cluster_name.startswith('path_') or cluster_name in ['arrays', 'functions', 'objects']:
                # Сортируем задачи в кластере по сложности
                cluster_tasks = [a for a in analyses if a.id in task_ids]
                cluster_tasks.sort(key=lambda x: (x.complexity_score, x.path_depth, x.order_in_file))
                
                sequences[f"sequence_{cluster_name}"] = [task.id for task in cluster_tasks]
        
        # 2. Общая последовательность изучения концепций
        concept_prerequisites = {
            'variables': [],
            'functions': ['variables'],
            'arrays': ['variables', 'functions'],
            'objects': ['variables', 'functions'],
            'strings': ['variables', 'functions'],
            'loops': ['variables', 'functions', 'arrays'],
            'conditionals': ['variables'],
            'classes': ['variables', 'functions', 'objects'],
            'async': ['variables', 'functions', 'objects'],
            'regex': ['strings', 'functions']
        }
        
        # Создаем рекомендуемую последовательность
        recommended_sequence = []
        for concept in ['variables', 'functions', 'conditionals', 'arrays', 'objects', 'strings', 'classes', 'async']:
            if concept in concept_clusters:
                # Берем несколько самых простых задач из каждой концепции
                concept_tasks = [a for a in analyses if a.id in concept_clusters[concept]]
                concept_tasks.sort(key=lambda x: x.complexity_score)
                recommended_sequence.extend([task.id for task in concept_tasks[:3]])  # топ-3 простых
        
        sequences['recommended_learning_path'] = recommended_sequence
        
        return sequences

    def analyze_path_structure_detailed(self, analyses: List[TaskAnalysis]) -> Dict[str, Any]:
        """Анализирует структуру pathTitles"""
        path_analysis = {
            'depth_distribution': defaultdict(int),
            'common_paths': defaultdict(int),
            'path_hierarchies': defaultdict(list)
        }
        
        for analysis in analyses:
            path_depth = len(analysis.path_titles)
            path_analysis['depth_distribution'][path_depth] += 1
            
            # Анализируем общие пути
            for i in range(1, len(analysis.path_titles) + 1):
                partial_path = ' > '.join(analysis.path_titles[:i])
                path_analysis['common_paths'][partial_path] += 1
            
            # Строим иерархии
            if analysis.path_titles:
                root = analysis.path_titles[0]
                path_analysis['path_hierarchies'][root].append(analysis.id)
        
        return path_analysis

    def analyze_pedagogical_patterns(self, analyses: List[TaskAnalysis]) -> Dict[str, Any]:
        """Анализирует педагогические паттерны"""
        pedagogical_analysis = {
            'explanation_count': 0,
            'example_count': 0,
            'exercise_count': 0,
            'challenge_count': 0,
            'practice_count': 0
        }
        
        for analysis in analyses:
            if analysis.pedagogical_type == "explanation":
                pedagogical_analysis['explanation_count'] += 1
            elif analysis.pedagogical_type == "example":
                pedagogical_analysis['example_count'] += 1
            elif analysis.pedagogical_type == "exercise":
                pedagogical_analysis['exercise_count'] += 1
            elif analysis.pedagogical_type == "challenge":
                pedagogical_analysis['challenge_count'] += 1
            else:
                pedagogical_analysis['practice_count'] += 1
        
        return pedagogical_analysis

    def generate_summary_stats(self, analyses: List[TaskAnalysis]) -> Dict[str, Any]:
        """Генерирует сводную статистику"""
        return {
            'total_tasks': len(analyses),
            'by_category': Counter(a.category for a in analyses),
            'by_skill_level': Counter(a.target_skill_level for a in analyses),
            'complexity_distribution': {
                'min': min(a.complexity_score for a in analyses),
                'max': max(a.complexity_score for a in analyses),
                'avg': sum(a.complexity_score for a in analyses) / len(analyses)
            },
            'most_common_concepts': Counter(
                concept for a in analyses for concept in a.programming_concepts
            ).most_common(20),
            'most_common_features': Counter(
                feature for a in analyses for feature in a.js_features_used
            ).most_common(20),
            'estimated_total_time_hours': sum(a.estimated_time_minutes for a in analyses) / 60
        }

    def print_detailed_report(self, analysis_result: Dict[str, Any]):
        """Выводит детальный отчет анализа"""
        analyses = analysis_result['task_analyses']
        clusters = analysis_result['concept_clusters']
        sequences = analysis_result['learning_sequences']
        stats = analysis_result['summary_stats']
        
        print("\n" + "="*80)
        print("🔍 ДЕТАЛЬНЫЙ АНАЛИЗ СОДЕРЖАНИЯ ЗАДАЧ NARESHKA")
        print("="*80)
        
        # Общая статистика
        print(f"\n📊 ОБЩАЯ СТАТИСТИКА:")
        print(f"   Всего задач: {stats['total_tasks']}")
        print(f"   Общее время изучения: {stats['estimated_total_time_hours']:.1f} часов")
        print(f"   Средняя сложность: {stats['complexity_distribution']['avg']:.2f}")
        
        # Распределение по уровням
        print(f"\n🎯 РАСПРЕДЕЛЕНИЕ ПО УРОВНЯМ:")
        for level, count in stats['by_skill_level'].items():
            percentage = (count / stats['total_tasks']) * 100
            print(f"   {level.capitalize()}: {count} задач ({percentage:.1f}%)")
        
        # Топ концепции
        print(f"\n🧠 ТОП-10 КОНЦЕПЦИЙ:")
        for concept, count in stats['most_common_concepts'][:10]:
            print(f"   {concept}: {count} задач")
        
        # Примеры задач по уровням
        print(f"\n📝 ПРИМЕРЫ ЗАДАЧ ПО УРОВНЯМ:")
        
        for level in ['beginner', 'intermediate', 'advanced']:
            level_tasks = [a for a in analyses if a.target_skill_level == level]
            if level_tasks:
                print(f"\n--- {level.upper()} УРОВЕНЬ ---")
                for i, task in enumerate(level_tasks[:3]):  # Показываем 3 примера
                    print(f"\n{i+1}. {task.title}")
                    print(f"   ID: {task.id}")
                    print(f"   Категория: {task.category} / {task.subcategory}")
                    print(f"   Сложность: {task.complexity_score}")
                    print(f"   Концепции: {', '.join(task.programming_concepts[:5])}")
                    print(f"   JS фичи: {', '.join(task.js_features_used[:5])}")
                    print(f"   Время изучения: {task.estimated_time_minutes} мин")
                    
                    # Показываем код (первые 5 строк)
                    code_lines = task.code_content.split('\n')[:5]
                    print(f"   Код:")
                    for j, line in enumerate(code_lines, 1):
                        if line.strip():
                            print(f"      {j}: {line}")
                    total_lines = len(task.code_content.split('\n'))
                    if total_lines > 5:
                        remaining_lines = total_lines - 5
                        print(f"      ... (еще {remaining_lines} строк)")
        
        # Кластеры концепций
        print(f"\n🎯 КЛАСТЕРЫ КОНЦЕПЦИЙ:")
        for cluster_name, task_ids in list(clusters.items())[:10]:
            print(f"\n--- {cluster_name.upper()} ---")
            print(f"   Задач: {len(task_ids)}")
            
            # Вычисляем диапазон сложности для кластера
            cluster_tasks = [a for a in analyses if a.id in task_ids]
            if cluster_tasks:
                min_complexity = min(task.complexity_score for task in cluster_tasks)
                max_complexity = max(task.complexity_score for task in cluster_tasks)
                print(f"   Сложность: {min_complexity:.1f} - {max_complexity:.1f}")
                
                # Показываем примеры задач кластера
                for task in cluster_tasks[:3]:
                    print(f"      • {task.title} (сложность: {task.complexity_score})")
        
        # Рекомендуемые последовательности
        print(f"\n📚 РЕКОМЕНДУЕМЫЕ ПОСЛЕДОВАТЕЛЬНОСТИ ИЗУЧЕНИЯ:")
        
        skill_sequences = sequences.get('by_skill_level', {})
        for level, task_ids in skill_sequences.items():
            if task_ids:
                print(f"\n--- {level.upper()} ПУТЬ ---")
                level_tasks = [a for a in analyses if a.id in task_ids[:5]]
                for i, task in enumerate(level_tasks, 1):
                    print(f"   {i}. {task.title} (сложность: {task.complexity_score})")
        
        # Детальные примеры интересных задач
        print(f"\n🔥 ИНТЕРЕСНЫЕ ЗАДАЧИ ДЛЯ MINDMAP:")
        
        # Самая простая задача
        simplest = min(analyses, key=lambda a: a.complexity_score)
        print(f"\n--- САМАЯ ПРОСТАЯ ЗАДАЧА ---")
        self.print_task_detail(simplest)
        
        # Самая сложная задача
        most_complex = max(analyses, key=lambda a: a.complexity_score)
        print(f"\n--- САМАЯ СЛОЖНАЯ ЗАДАЧА ---")
        self.print_task_detail(most_complex)
        
        # Задача с наибольшим количеством концепций
        most_concepts = max(analyses, key=lambda a: len(a.programming_concepts))
        print(f"\n--- ЗАДАЧА С НАИБОЛЬШИМ КОЛИЧЕСТВОМ КОНЦЕПЦИЙ ---")
        self.print_task_detail(most_concepts)

    def print_task_detail(self, task: TaskAnalysis):
        """Выводит детальную информацию о задаче"""
        print(f"   Название: {task.title}")
        print(f"   ID: {task.id}")
        print(f"   Категория: {task.category} / {task.subcategory}")
        print(f"   Путь: {' > '.join(task.path_titles) if task.path_titles else 'Нет'}")
        print(f"   Сложность: {task.complexity_score}")
        print(f"   Факторы сложности: {', '.join(task.difficulty_factors)}")
        print(f"   Концепции: {', '.join(task.programming_concepts)}")
        print(f"   JS фичи: {', '.join(task.js_features_used)}")
        print(f"   Пререквизиты: {', '.join(task.prerequisite_concepts)}")
        print(f"   Время изучения: {task.estimated_time_minutes} мин")
        print(f"   Уровень: {task.target_skill_level}")
        
        if task.text_content:
            print(f"   Описание: {task.text_content[:200]}...")
        
        print(f"   Код ({task.code_lines} строк):")
        code_lines = task.code_content.split('\n')[:8]
        for i, line in enumerate(code_lines, 1):
            if line.strip():
                print(f"      {i}: {line}")
        total_lines = len(task.code_content.split('\n'))
        if total_lines > 8:
            remaining_lines = total_lines - 8
            print(f"      ... (еще {remaining_lines} строк)")

    def calculate_text_complexity(self, text: str) -> float:
        """Анализирует сложность текстового описания"""
        if not text:
            return 0.0
        
        complexity = 0.0
        
        # Длина текста
        word_count = len(text.split())
        complexity += min(word_count / 100, 2.0)  # до 2 баллов за длину
        
        # Сложные термины
        complex_terms = [
            'алгоритм', 'рекурсия', 'итерация', 'сложность', 'оптимизация',
            'архитектура', 'паттерн', 'полиморфизм', 'инкапсуляция', 'наследование',
            'асинхронность', 'промис', 'колбэк', 'замыкание', 'прототип'
        ]
        
        text_lower = text.lower()
        complex_term_count = sum(1 for term in complex_terms if term in text_lower)
        complexity += complex_term_count * 0.5
        
        # Количество примеров кода в тексте
        code_examples = text.count('```') + text.count('`')
        complexity += code_examples * 0.3
        
        # Математические формулы или сложные объяснения
        math_indicators = ['O(', 'θ(', 'время выполнения', 'пространственная сложность']
        math_count = sum(1 for indicator in math_indicators if indicator in text_lower)
        complexity += math_count * 1.0
        
        return round(complexity, 2)

    def determine_pedagogical_type(self, text: str, code: str, title: str) -> str:
        """Определяет педагогический тип задачи"""
        content = (text + " " + title).lower()
        
        # Индикаторы типов
        if any(word in content for word in ['объяснение', 'понятие', 'что такое', 'определение']):
            return "explanation"
        elif any(word in content for word in ['пример', 'рассмотрим', 'демонстрация']):
            return "example"
        elif any(word in content for word in ['задача', 'реализуйте', 'создайте', 'напишите']):
            return "exercise"
        elif any(word in content for word in ['сложная', 'advanced', 'экспертный', 'challenge']):
            return "challenge"
        else:
            return "practice"

    def create_topic_based_structure(self, analyses: List[TaskAnalysis]) -> Dict[str, Any]:
        """Создает структуру на основе 10 основных тем JavaScript"""
        
        # 10 основных тем с конфигурацией
        CORE_TOPICS = {
            'closures': {
                'title': 'Замыкания',
                'icon': '🔒',
                'color': '#8B5CF6',
                'description': 'Замыкания, области видимости, лексическое окружение',
                'keywords': [
                    'closure', 'hello world', 'counter', 'makeCounter', 'canGetCount',
                    'createFunctionArray', 'lexical', 'scope', 'замыка', 'замыкание',
                    'ad(5)()', 'count()', 'callback'
                ]
            },
            'custom_functions': {
                'title': 'Кастомные методы и функции',
                'icon': '⚡',
                'color': '#F59E0B',
                'description': 'Каррирование, композиция, мемоизация, перегрузка',
                'keywords': [
                    'sum(1)(2)(3)', 'add(', 'compose', 'pipe', 'memo', 'memoize',
                    'перегрузка', 'curry', 'функций', 'методы', 'каррирование'
                ]
            },
            'classes': {
                'title': 'Классы',
                'icon': '🏗️',
                'color': '#EF4444',
                'description': 'ES6 классы, наследование, паттерны проектирования',
                'keywords': [
                    'class', 'constructor', 'singleton', 'queue', 'stack', 'store',
                    'extends', 'super', 'getInstance', 'cat', 'List<T>', 'new '
                ]
            },
            'arrays': {
                'title': 'Массивы',
                'icon': '📊',
                'color': '#10B981',
                'description': 'Операции с массивами, алгоритмы, манипуляции',
                'keywords': [
                    'array', 'findMinMax', 'twoSum', 'chunk', 'moveZeroes',
                    'removeEvenIndexedElements', 'getConcatenation', 'maxElementIndex',
                    'массив', 'splice', 'push', 'pop'
                ]
            },
            'matrices': {
                'title': 'Матрицы',
                'icon': '🔢',
                'color': '#3B82F6',
                'description': 'Двумерные массивы, алгоритмы на матрицах',
                'keywords': [
                    'matrix', 'grid', 'battleship', 'rotate', 'spiral', 'island',
                    'transpose', 'celebrity', 'countShips', 'numIslands',
                    'матрица', 'board'
                ]
            },
            'objects': {
                'title': 'Объекты',
                'icon': '📦',
                'color': '#06B6D4',
                'description': 'Структуры данных, деревья, обход графов',
                'keywords': [
                    'tree', 'dfs', 'bfs', 'collectValues', 'children', 'value',
                    'left', 'right', 'root', 'объект', 'nodes', 'traverse'
                ]
            },
            'promises': {
                'title': 'Промисы',
                'icon': '⏳',
                'color': '#8B5CF6',
                'description': 'Асинхронность, промисы, async/await',
                'keywords': [
                    'promise', 'async', 'await', 'sleep', 'timeout', 'timeLimit',
                    'withTimeout', 'sumPromises', 'setTimeout', 'then', 'catch',
                    'промис', 'асинхрон'
                ]
            },
            'strings': {
                'title': 'Строки',
                'icon': '🔤',
                'color': '#F97316',
                'description': 'Работа со строками, алгоритмы на строках',
                'keywords': [
                    'string', 'reverse', 'anagram', 'palindrome', 'greet',
                    'lengthOfLastWord', 'compress', 'строка', 'charAt', 'substring'
                ]
            },
            'throttle_debounce': {
                'title': 'Throttle & Debounce',
                'icon': '🎛️',
                'color': '#EC4899',
                'description': 'Контроль вызовов функций, производительность',
                'keywords': [
                    'throttle', 'debounce', 'useThrottle', 'useDebounce',
                    'тротл', 'дебаунс', 'задержка', 'производительность'
                ]
            },
            'numbers': {
                'title': 'Числа',
                'icon': '🧮',
                'color': '#84CC16',
                'description': 'Математические операции, алгоритмы с числами',
                'keywords': [
                    'factorial', 'fibonacci', 'reverseNumber', 'fizzBuzz',
                    'sumOfNumber', 'largestPossibleNumber', 'факториал',
                    'число', 'математик'
                ]
            }
        }
        
        logger.info(f"🔍 Группируем {len(analyses)} задач по 10 основным темам...")
        
        # Группируем задачи по темам
        topic_structure = {}
        unassigned_tasks = []
        
        for topic_key, topic_config in CORE_TOPICS.items():
            topic_tasks = []
            
            for analysis in analyses:
                # Проверяем по ключевым словам в заголовке, коде и описании
                content = (
                    analysis.title + " " + 
                    analysis.code_content + " " + 
                    analysis.text_content + " " +
                    " ".join(analysis.path_titles)
                ).lower()
                
                # Проверяем совпадения с ключевыми словами
                matches = 0
                for keyword in topic_config['keywords']:
                    if keyword.lower() in content:
                        matches += 1
                
                # Если есть совпадения, добавляем к теме
                if matches > 0:
                    topic_tasks.append({
                        'id': analysis.id,
                        'title': analysis.title,
                        'complexity': analysis.complexity_score,
                        'skill_level': analysis.target_skill_level,
                        'time_minutes': analysis.estimated_time_minutes,
                        'concepts': analysis.programming_concepts,
                        'js_features': analysis.js_features_used,
                        'companies': self.extract_companies_from_text(analysis.text_content),
                        'matches': matches,  # количество совпадений
                        'code_preview': analysis.code_content[:200] + "..." if len(analysis.code_content) > 200 else analysis.code_content,
                        'text_preview': analysis.text_content[:150] + "..." if len(analysis.text_content) > 150 else analysis.text_content
                    })
            
            # Убираем дубликаты (задача может подходить к нескольким темам)
            # Оставляем задачу в теме с наибольшим количеством совпадений
            unique_tasks = {}
            for task in topic_tasks:
                task_id = task['id']
                if task_id not in unique_tasks or task['matches'] > unique_tasks[task_id]['matches']:
                    unique_tasks[task_id] = task
            
            topic_tasks = list(unique_tasks.values())
            
            # Сортируем по сложности
            topic_tasks.sort(key=lambda x: (x['complexity'], x['time_minutes']))
            
            # Вычисляем статистику
            total_tasks = len(topic_tasks)
            avg_complexity = sum(t['complexity'] for t in topic_tasks) / total_tasks if total_tasks > 0 else 0
            difficulty_distribution = self.calculate_difficulty_distribution(topic_tasks)
            
            topic_structure[topic_key] = {
                'config': topic_config,
                'tasks': topic_tasks,
                'total_tasks': total_tasks,
                'avg_complexity': round(avg_complexity, 2),
                'difficulty_distribution': difficulty_distribution,
                'estimated_total_time': sum(t['time_minutes'] for t in topic_tasks),
                'top_companies': self.get_top_companies(topic_tasks),
                'skill_progression': self.calculate_skill_progression(topic_tasks)
            }
            
            logger.info(f"   📌 {topic_config['title']}: {total_tasks} задач (сложность: {round(avg_complexity, 2)})")
        
        # Находим неназначенные задачи
        assigned_task_ids = set()
        for topic_data in topic_structure.values():
            for task in topic_data['tasks']:
                assigned_task_ids.add(task['id'])
        
        unassigned_tasks = [a for a in analyses if a.id not in assigned_task_ids]
        
        logger.info(f"✅ Создана структура: {len(assigned_task_ids)} задач распределено, {len(unassigned_tasks)} не назначено")
        
        return {
            'topics': topic_structure,
            'unassigned_tasks': [
                {
                    'id': task.id,
                    'title': task.title,
                    'complexity': task.complexity_score,
                    'concepts': task.programming_concepts
                }
                for task in unassigned_tasks
            ],
            'total_assigned': len(assigned_task_ids),
            'total_unassigned': len(unassigned_tasks),
            'coverage_percentage': round((len(assigned_task_ids) / len(analyses)) * 100, 1)
        }

    def extract_companies_from_text(self, text: str) -> List[str]:
        """Извлекает названия компаний из описания задачи"""
        if not text:
            return []
            
        companies = []
        text = text.lower()
        
        # Паттерны для поиска компаний
        company_patterns = [
            r'встречалось в\s*[-\s]*([^\n]+)',
            r'попадалось в\s*[-\s]*([^\n]+)',
            r'собеседован[ие|иях].*?в\s+([а-яё\s\-\.]+)',
            r'компани[ия|и]\s+([а-яё\s\-\.]+)',
        ]
        
        for pattern in company_patterns:
            matches = re.findall(pattern, text, re.IGNORECASE | re.MULTILINE)
            for match in matches:
                # Очищаем и разбиваем по разделителям
                clean_companies = re.split(r'[,\n\-]', match.strip())
                for company in clean_companies:
                    company = company.strip()
                    if company and len(company) > 2:
                        companies.append(company.title())
        
        return list(set(companies))

    def calculate_difficulty_distribution(self, tasks: List[Dict]) -> Dict[str, int]:
        """Рассчитывает распределение по уровням сложности"""
        distribution = {'beginner': 0, 'intermediate': 0, 'advanced': 0}
        
        for task in tasks:
            level = task.get('skill_level', 'intermediate')
            if level in distribution:
                distribution[level] += 1
        
        return distribution

    def get_top_companies(self, tasks: List[Dict]) -> List[Dict[str, Any]]:
        """Возвращает топ компаний по количеству упоминаний"""
        company_count = Counter()
        
        for task in tasks:
            for company in task.get('companies', []):
                company_count[company] += 1
        
        return [
            {'name': company, 'count': count}
            for company, count in company_count.most_common(5)
        ]

    def calculate_skill_progression(self, tasks: List[Dict]) -> List[str]:
        """Рассчитывает рекомендуемую последовательность изучения"""
        # Сортируем по сложности и времени изучения
        sorted_tasks = sorted(tasks, key=lambda x: (x['complexity'], x['time_minutes']))
        
        # Возвращаем первые 10 задач как рекомендуемую последовательность
        return [task['id'] for task in sorted_tasks[:10]]

def main():
    """Запуск детального анализа"""
    analyzer = DeepContentAnalyzer()
    result = analyzer.analyze_all_tasks()
    
    # Сохраняем результат в JSON для дальнейшего использования
    output_file = "detailed_analysis_result.json"
    
    # Преобразуем dataclass объекты в словари для JSON
    json_result = {
        'task_analyses': [asdict(analysis) for analysis in result['task_analyses']],
        'concept_clusters': result['concept_clusters'],  # уже словарь
        'learning_sequences': result['learning_sequences'],
        'path_structure': result['path_structure'],
        'pedagogical_analysis': result['pedagogical_analysis'],
        'user_statistics': result['user_statistics'],
        'summary_stats': result['summary_stats']
    }
    
    # Конвертируем set в list для JSON
    for task in json_result['task_analyses']:
        task['keywords'] = list(task['keywords'])
    
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(json_result, f, ensure_ascii=False, indent=2)
    
    print(f"\n💾 Результат сохранен в файл: {output_file}")
    
    # Выводим детальный отчет
    analyzer.print_detailed_report(result)

if __name__ == "__main__":
    main()