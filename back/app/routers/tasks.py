import logging
from typing import Optional, List, Dict, Any, Union

from fastapi import APIRouter, Depends, HTTPException, Query, Request
from pydantic import BaseModel
from sqlalchemy import asc, desc, func, or_
from sqlalchemy.orm import Session

from ..auth import get_current_user_from_session
from ..database import get_db
from ..models import ContentBlock, ContentFile, TheoryCard, UserContentProgress, UserTheoryProgress

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/tasks", tags=["Tasks"])

def unescape_text_content(text: Optional[str]) -> Optional[str]:
    """Заменяет экранированные символы на настоящие переносы строк"""
    if not text:
        return text
    return text.replace("\\n", "\n").replace("\\t", "\t")

class TaskItem(BaseModel):
    id: str
    type: str
    title: str
    description: Optional[str] = None
    category: str
    subCategory: Optional[str] = None
    
    # Поля для content_block
    fileId: Optional[str] = None
    pathTitles: Optional[List[str]] = None
    blockLevel: Optional[int] = None
    orderInFile: Optional[int] = None
    textContent: Optional[str] = None
    codeContent: Optional[str] = None
    codeLanguage: Optional[str] = None
    isCodeFoldable: Optional[bool] = None
    codeFoldTitle: Optional[str] = None
    extractedUrls: Optional[List[str]] = None
    
    # Поля для theory_quiz
    questionBlock: Optional[str] = None
    answerBlock: Optional[str] = None
    tags: Optional[List[str]] = None
    orderIndex: Optional[int] = None
    
    # Прогресс пользователя
    currentUserSolvedCount: int = 0
    
    # Метаданные
    createdAt: str
    updatedAt: str

@router.get("/items")
async def get_task_items(
    request: Request,
    db: Session = Depends(get_db),
    page: int = Query(1, ge=1, description="Номер страницы"),
    limit: int = Query(10, ge=1, le=100, description="Количество элементов на странице"),
    mainCategories: List[str] = Query([], description="Фильтр по основным категориям (множественный)"),
    subCategories: List[str] = Query([], description="Подкатегории (множественный)"),
    q: Optional[str] = Query(None, description="Полнотекстовый поиск"),
    sortBy: str = Query("orderInFile", description="Поле для сортировки"),
    sortOrder: str = Query("asc", description="Порядок сортировки"),
    itemType: Optional[str] = Query(None, description="Тип: content_block, theory_quiz или all"),
    onlyUnsolved: Optional[bool] = Query(None, description="Только нерешенные"),
    companies: Optional[str] = Query(None, description="Фильтр по компаниям (через запятую, deprecated)"),
    companiesList: List[str] = Query([], description="Фильтр по компаниям (множественный)")
):
    """Получение объединенного списка задач (content blocks + quiz карточки)"""
    
    user = get_current_user_from_session(request, db)
    is_authenticated = user is not None
    user_id = user.id if user else None
    
    final_companies = list(companiesList) if companiesList else []
    if companies:
        company_list = [c.strip() for c in companies.split(',') if c.strip()]
        for company in company_list:
            if company not in final_companies:
                final_companies.append(company)
    
    all_items = []
    
    if not itemType or itemType in ["content_block", "all"]:
        content_blocks = await _get_content_blocks(
            db, user_id, is_authenticated, mainCategories, subCategories, q, onlyUnsolved, final_companies
        )
        all_items.extend(content_blocks)
    
    if not itemType or itemType in ["theory_quiz", "all"]:
        if not final_companies:
            quiz_cards = await _get_quiz_cards(
                db, user_id, is_authenticated, mainCategories, subCategories, q, onlyUnsolved
            )
            all_items.extend(quiz_cards)
    
    all_items = _sort_items(all_items, sortBy, sortOrder)
    
    offset = (page - 1) * limit
    total_count = len(all_items)
    paginated_items = all_items[offset:offset + limit]
    
    total_pages = (total_count + limit - 1) // limit
    
    return {
        "data": paginated_items,
        "pagination": {
            "page": page,
            "limit": limit,
            "total": total_count,
            "totalPages": total_pages,
            "hasNext": page < total_pages,
            "hasPrev": page > 1
        }
    }

async def _get_content_blocks(
    db: Session, 
    user_id: Optional[int], 
    is_authenticated: bool,
    main_categories: List[str],
    sub_categories: List[str],
    q: Optional[str] = None,
    only_unsolved: Optional[bool] = None,
    companies: Optional[List[str]] = None
) -> List[Dict[str, Any]]:
    query = db.query(ContentBlock).join(ContentFile)
    
    if main_categories:
        query = query.filter(func.lower(ContentFile.mainCategory).in_(map(lambda x: x.lower(), main_categories)))
    if sub_categories:
        query = query.filter(func.lower(ContentFile.subCategory).in_(map(lambda x: x.lower(), sub_categories)))
    if q and q.strip():
        search_term = f"%{q.strip()}%"
        query = query.filter(
            or_(
                ContentBlock.blockTitle.ilike(search_term),
                ContentBlock.textContent.ilike(search_term),
                ContentBlock.codeFoldTitle.ilike(search_term)
            )
        )
    
    if companies and companies:
        # Фильтруем по пересечению с массивом companies
        query = query.filter(
            or_(
                *[func.lower(func.array_to_string(ContentBlock.companies, ',', '')).contains(company) 
                  for company in companies]
            )
        )
    
    blocks = query.order_by(asc(ContentBlock.orderInFile)).all()
    
    progress_map = {}
    if is_authenticated and user_id and blocks:
        block_ids = [block.id for block in blocks]
        progresses = db.query(UserContentProgress).filter(
            UserContentProgress.userId == user_id,
            UserContentProgress.blockId.in_(block_ids)
        ).all()
        progress_map = {p.blockId: p.solvedCount for p in progresses}
    
    result = []
    for block in blocks:
        solved_count = progress_map.get(block.id, 0)
        
        if only_unsolved and solved_count > 0:
            continue
        
        item = {
            "id": block.id,
            "type": "content_block",
            
            "fileId": block.fileId,
            "file": {
                "id": block.file.id,
                "webdavPath": block.file.webdavPath,
                "mainCategory": block.file.mainCategory,
                "subCategory": block.file.subCategory
            },
            "pathTitles": block.pathTitles,
            "blockTitle": block.blockTitle,
            "blockLevel": block.blockLevel,
            "orderInFile": block.orderInFile,
            "textContent": unescape_text_content(block.textContent),
            "codeContent": block.codeContent,
            "codeLanguage": block.codeLanguage,
            "isCodeFoldable": block.isCodeFoldable,
            "codeFoldTitle": block.codeFoldTitle,
            "extractedUrls": block.extractedUrls,
            "companies": block.companies or [],
            "rawBlockContentHash": block.rawBlockContentHash,
            
            "progressEntries": [
                {
                    "id": f"content_progress_{block.id}",
                    "solvedCount": solved_count,
                    "createdAt": block.createdAt.isoformat(),
                    "updatedAt": block.updatedAt.isoformat()
                }
            ] if solved_count > 0 else [],
            
            "createdAt": block.createdAt.isoformat(),
            "updatedAt": block.updatedAt.isoformat()
        }
        result.append(item)
    
    return result

async def _get_quiz_cards(
    db: Session,
    user_id: Optional[int],
    is_authenticated: bool, 
    main_categories: List[str],
    sub_categories: List[str],
    q: Optional[str] = None,
    only_unsolved: Optional[bool] = None
) -> List[Dict[str, Any]]:  
    query = db.query(TheoryCard).filter(
        or_(
            TheoryCard.category == "JS QUIZ",
            TheoryCard.category == "REACT QUIZ"
        )
    )
    
    if main_categories:
        # Преобразуем основные категории в quiz категории
        quiz_categories = []
        for main_cat in main_categories:
            if main_cat.upper() == "JS":
                quiz_categories.append("JS QUIZ")
            elif main_cat.upper() == "REACT":
                quiz_categories.append("REACT QUIZ")
        
        if quiz_categories:
            query = query.filter(TheoryCard.category.in_(quiz_categories))
        else:
            return []  # Нет соответствующих quiz категорий
    
    if sub_categories:
        # Фильтруем подкатегории, если не "QUIZ"
        non_quiz_subcategories = [sub for sub in sub_categories if sub.upper() != "QUIZ"]
        if non_quiz_subcategories:
            query = query.filter(func.lower(TheoryCard.subCategory).in_(map(lambda x: x.lower(), non_quiz_subcategories)))
    
    if q and q.strip():
        search_term = f"%{q.strip()}%"
        query = query.filter(
            or_(
                TheoryCard.questionBlock.ilike(search_term),
                TheoryCard.answerBlock.ilike(search_term)
            )
        )
    
    cards = query.order_by(asc(TheoryCard.orderIndex)).all()
    
    progress_map = {}
    if is_authenticated and user_id and cards:
        card_ids = [card.id for card in cards]
        progresses = db.query(UserTheoryProgress).filter(
            UserTheoryProgress.userId == user_id,
            UserTheoryProgress.cardId.in_(card_ids)
        ).all()
        progress_map = {p.cardId: p.solvedCount for p in progresses}
    
    result = []
    for card in cards:
        solved_count = progress_map.get(card.id, 0)
        
        if only_unsolved and solved_count > 0:
            continue
        
        item = {
            "id": card.id,
            "type": "theory_quiz",
            
            "fileId": None,
            "file": {
                "id": None,
                "webdavPath": f"/quiz/{card.category.lower().replace(' ', '_')}/quiz",
                "mainCategory": card.category.replace(" QUIZ", ""),
                "subCategory": "QUIZ"
            },
            "pathTitles": [card.category.replace(" QUIZ", ""), "QUIZ"],
            "blockTitle": f"Quiz: {card.subCategory or 'Общие вопросы'}",
            "blockLevel": 1,
            "orderInFile": card.orderIndex,
            "textContent": unescape_text_content(card.questionBlock),
            "codeContent": None,
            "codeLanguage": None,
            "isCodeFoldable": False,
            "codeFoldTitle": None,
            "extractedUrls": [],
            "rawBlockContentHash": None,
            
            "questionBlock": unescape_text_content(card.questionBlock),
            "answerBlock": unescape_text_content(card.answerBlock),
            "tags": card.tags,
            
            "progressEntries": [
                {
                    "id": f"quiz_progress_{card.id}",
                    "solvedCount": solved_count,
                    "createdAt": card.createdAt.isoformat(),
                    "updatedAt": card.updatedAt.isoformat()
                }
            ] if solved_count > 0 else [],
            
            "createdAt": card.createdAt.isoformat(),
            "updatedAt": card.updatedAt.isoformat()
        }
        result.append(item)
    
    return result

def _sort_items(items: List[Dict[str, Any]], sort_by: str, sort_order: str) -> List[Dict[str, Any]]:
    reverse = sort_order == "desc"
    
    if sort_by == "category":
        items.sort(key=lambda x: x["file"]["mainCategory"], reverse=reverse)
    elif sort_by == "title" or sort_by == "blockTitle":
        items.sort(key=lambda x: x["blockTitle"], reverse=reverse)
    elif sort_by == "createdAt":
        items.sort(key=lambda x: x["createdAt"], reverse=reverse)
    elif sort_by == "type":
        items.sort(key=lambda x: x["type"], reverse=reverse)
    elif sort_by == "orderInFile":
        items.sort(key=lambda x: x["orderInFile"], reverse=reverse)
    else: 
        items.sort(key=lambda x: (x["file"]["mainCategory"], x["orderInFile"]), reverse=reverse)
    
    return items

@router.get("/categories")
async def get_task_categories(db: Session = Depends(get_db)):
    try:
        content_categories = db.query(
            ContentFile.mainCategory,
            ContentFile.subCategory
        ).join(ContentBlock).distinct().all()
        
        quiz_categories = db.query(
            TheoryCard.category,
            TheoryCard.subCategory
        ).filter(
            or_(
                TheoryCard.category == "JS QUIZ",
                TheoryCard.category == "REACT QUIZ"
            )
        ).distinct().all()
        
        hierarchy_map = {}
        
        for main_cat, sub_cat in content_categories:
            # Пропускаем тестовые категории и подкатегории
            if main_cat == 'Test' or sub_cat == 'Test':
                continue
            if main_cat not in hierarchy_map:
                hierarchy_map[main_cat] = set()
            if sub_cat:
                hierarchy_map[main_cat].add(sub_cat)
        
        for quiz_cat, sub_cat in quiz_categories:
            main_cat = quiz_cat.replace(" QUIZ", "")  
            
            # Пропускаем тестовые категории и подкатегории
            if main_cat == 'Test' or sub_cat == 'Test':
                continue
            
            if main_cat not in hierarchy_map:
                hierarchy_map[main_cat] = set()
            
            hierarchy_map[main_cat].add("QUIZ")
        
        result = []
        for main_cat in sorted(hierarchy_map.keys()):
            sub_categories = sorted(list(hierarchy_map[main_cat]))
            result.append({
                "name": main_cat,
                "subCategories": sub_categories  
            })
        
        return result
        
    except Exception as e:
        logger.error(f"Error getting task categories: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")

@router.get("/companies")
async def get_companies(
    db: Session = Depends(get_db),
    mainCategories: List[str] = Query([], description="Фильтр по основным категориям"),
    subCategories: List[str] = Query([], description="Фильтр по подкатегориям")
):
    """Получение списка компаний из задач с учетом фильтров"""
    try:
        # Базовый запрос для получения компаний
        query = db.query(ContentBlock.companies).filter(
            ContentBlock.companies.isnot(None),
            ContentBlock.companies != []
        )
        
        # Добавляем фильтр по категориям, если указаны
        if mainCategories or subCategories:
            query = query.join(ContentFile)
            
            if mainCategories:
                query = query.filter(func.lower(ContentFile.mainCategory).in_(map(lambda x: x.lower(), mainCategories)))
            if subCategories:
                query = query.filter(func.lower(ContentFile.subCategory).in_(map(lambda x: x.lower(), subCategories)))
        
        results = query.distinct().all()
        
        # Собираем все компании в один список
        all_companies = set()
        for result in results:
            if result[0]:  # result[0] это массив companies
                for company in result[0]:
                    if company and company.strip():
                        all_companies.add(company.strip())
        
        # Сортируем по алфавиту
        companies_list = sorted(list(all_companies))
        
        return {
            "companies": companies_list,
            "total": len(companies_list)
        }
    
    except Exception as e:
        logger.error(f"Error getting companies: {e}")
        raise HTTPException(status_code=500, detail="Internal server error") 