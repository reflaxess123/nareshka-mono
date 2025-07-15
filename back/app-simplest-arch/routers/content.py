import logging
from typing import Optional
from datetime import datetime
from uuid import uuid4

from fastapi import APIRouter, Depends, HTTPException, Query, Request
from pydantic import BaseModel
from sqlalchemy import asc, desc, func, or_, and_
from sqlalchemy.orm import Session, joinedload

from ..auth import get_current_user_from_session, get_current_user_from_session_required
from ..database import get_db
from ..models import ContentBlock, ContentFile, UserContentProgress, UserCategoryProgress, User

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/content", tags=["Content"])

def unescape_text_content(text: Optional[str]) -> Optional[str]:
    """Заменяет экранированные символы на настоящие переносы строк"""
    if not text:
        return text
    return text.replace("\\n", "\n").replace("\\t", "\t")


async def update_user_total_stats_from_content_progress(db: Session, user_id: int):
    """Обновляет общую статистику пользователя на основе UserContentProgress"""
    
    user = db.query(User).filter(User.id == user_id).first()
    if user:
        # Считаем решенные задачи на основе UserContentProgress
        total_solved = db.query(func.count(UserContentProgress.id)).filter(
            and_(
                UserContentProgress.userId == user_id,
                UserContentProgress.solvedCount > 0
            )
        ).join(ContentBlock).join(ContentFile).filter(
            and_(
                ContentFile.mainCategory != 'Test',
                ContentFile.subCategory != 'Test'
            )
        ).scalar() or 0
        
        user.totalTasksSolved = total_solved
        user.lastActivityDate = datetime.now()


async def update_category_progress_from_content_progress(db: Session, user_id: int, block_id: str):
    """Обновляет прогресс по категории на основе UserContentProgress"""
    
    # Получаем блок с информацией о файле
    block = db.query(ContentBlock).options(joinedload(ContentBlock.file)).filter(ContentBlock.id == block_id).first()
    if not block or not block.file:
        return
    
    main_category = block.file.mainCategory
    sub_category = block.file.subCategory
    
    # Находим или создаем запись категорийного прогресса
    category_progress = db.query(UserCategoryProgress).filter(
        and_(
            UserCategoryProgress.userId == user_id,
            UserCategoryProgress.mainCategory == main_category,
            UserCategoryProgress.subCategory == sub_category
        )
    ).first()
    
    if not category_progress:
        # Считаем общее количество задач в этой категории
        total_tasks = db.query(func.count(ContentBlock.id)).join(ContentFile).filter(
            and_(
                ContentFile.mainCategory == main_category,
                ContentFile.subCategory == sub_category,
                ContentBlock.codeContent.isnot(None)  # Только задачи с кодом
            )
        ).scalar() or 0
        
        category_progress = UserCategoryProgress(
            id=str(uuid4()),
            userId=user_id,
            mainCategory=main_category,
            subCategory=sub_category,
            totalTasks=total_tasks,
            firstAttempt=datetime.now()
        )
        db.add(category_progress)
    
    # Пересчитываем статистику на основе UserContentProgress
    solved_blocks = db.query(func.count(UserContentProgress.id)).filter(
        and_(
            UserContentProgress.userId == user_id,
            UserContentProgress.solvedCount > 0
        )
    ).join(ContentBlock).join(ContentFile).filter(
        and_(
            ContentFile.mainCategory == main_category,
            ContentFile.subCategory == sub_category
        )
    ).scalar() or 0
    
    attempted_blocks = db.query(func.count(UserContentProgress.id)).filter(
        UserContentProgress.userId == user_id
    ).join(ContentBlock).join(ContentFile).filter(
        and_(
            ContentFile.mainCategory == main_category,
            ContentFile.subCategory == sub_category
        )
    ).scalar() or 0
    
    # Обновляем статистику
    category_progress.completedTasks = solved_blocks
    category_progress.attemptedTasks = attempted_blocks
    category_progress.lastActivity = datetime.now()
    
    # Рассчитываем успешность
    if attempted_blocks > 0:
        category_progress.successRate = (solved_blocks / attempted_blocks) * 100
    
    # Рассчитываем среднее количество попыток (приблизительно, так как UserContentProgress хранит только количество решений)
    avg_solved_count = db.query(func.avg(UserContentProgress.solvedCount)).filter(
        and_(
            UserContentProgress.userId == user_id,
            UserContentProgress.solvedCount > 0
        )
    ).join(ContentBlock).join(ContentFile).filter(
        and_(
            ContentFile.mainCategory == main_category,
            ContentFile.subCategory == sub_category
        )
    ).scalar() or 1.0
    
    category_progress.averageAttempts = float(avg_solved_count)


@router.get("/blocks")
async def get_content_blocks(
    request: Request,
    db: Session = Depends(get_db),
    page: int = Query(1, ge=1, description="Номер страницы"),
    limit: int = Query(10, ge=1, le=100, description="Количество блоков на странице"),
    webdavPath: Optional[str] = Query(None, description="Часть пути к файлу WebDAV"),
    mainCategory: Optional[str] = Query(None, description="Основная категория контента"),
    subCategory: Optional[str] = Query(None, description="Подкатегория контента"),
    filePathId: Optional[str] = Query(None, description="ID файла для фильтрации блоков"),
    q: Optional[str] = Query(None, description="Полнотекстовый поиск"),
    sortBy: str = Query("orderInFile", description="Поле для сортировки"),
    sortOrder: str = Query("asc", description="Порядок сортировки")
):
    """Получение списка блоков контента с пагинацией и фильтрацией"""

    # Проверяем аутентификацию
    user = get_current_user_from_session(request, db)
    is_authenticated = user is not None
    user_id = user.id if user else None

    # Рассчитываем offset
    offset = (page - 1) * limit

    # Строим базовый запрос с join к ContentFile
    query = db.query(ContentBlock).join(ContentFile)

    # Применяем фильтры по файлу
    if webdavPath:
        query = query.filter(ContentFile.webdavPath.ilike(f"%{webdavPath}%"))

    if mainCategory:
        query = query.filter(func.lower(ContentFile.mainCategory) == func.lower(mainCategory))

    if subCategory:
        query = query.filter(func.lower(ContentFile.subCategory) == func.lower(subCategory))

    if filePathId:
        query = query.filter(ContentFile.id == filePathId)

    # Полнотекстовый поиск
    if q and q.strip():
        search_term = f"%{q.strip()}%"
        query = query.filter(
            or_(
                ContentBlock.blockTitle.ilike(search_term),
                ContentBlock.textContent.ilike(search_term),
                ContentBlock.codeFoldTitle.ilike(search_term)
            )
        )

    # Применяем сортировку
    if sortBy == "createdAt":
        order_field = ContentBlock.createdAt
    elif sortBy == "updatedAt":
        order_field = ContentBlock.updatedAt
    elif sortBy == "orderInFile":
        order_field = ContentBlock.orderInFile
    elif sortBy == "blockLevel":
        order_field = ContentBlock.blockLevel
    elif sortBy == "file.webdavPath":
        order_field = ContentFile.webdavPath
    else:
        order_field = ContentBlock.orderInFile

    if sortOrder == "desc":
        query = query.order_by(desc(order_field))
    else:
        query = query.order_by(asc(order_field))

    # Получаем общее количество для пагинации
    total_count = query.count()

    # Применяем пагинацию
    blocks = query.offset(offset).limit(limit).all()

    # Формируем результат как в Node.js
    result = []
    for block in blocks:
        base_block = {
            "id": block.id,
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
            "companies": block.companies if block.companies else [],
            "rawBlockContentHash": block.rawBlockContentHash,
            "createdAt": block.createdAt,
            "updatedAt": block.updatedAt
        }

        # Добавляем progressEntries только для авторизованных пользователей
        if is_authenticated and user_id:
            progress_entries = db.query(UserContentProgress).filter(
                UserContentProgress.userId == user_id,
                UserContentProgress.blockId == block.id
            ).all()

            # Форматируем progressEntries как в Node.js
            base_block["progressEntries"] = [
                {
                    "id": entry.id,
                    "solvedCount": entry.solvedCount,
                    "createdAt": entry.createdAt,
                    "updatedAt": entry.updatedAt
                }
                for entry in progress_entries
            ]
            
            # Добавляем currentUserSolvedCount для совместимости с frontend
            total_solved_count = sum(entry.solvedCount for entry in progress_entries)
            base_block["currentUserSolvedCount"] = total_solved_count
        else:
            base_block["currentUserSolvedCount"] = 0

        result.append(base_block)

    # Подсчитываем страницы
    total_pages = (total_count + limit - 1) // limit

    return {
        "blocks": result,
        "pagination": {
            "page": page,
            "limit": limit,
            "total": total_count,
            "totalPages": total_pages,
            "hasNext": page < total_pages,
            "hasPrev": page > 1
        }
    }


@router.get("/files")
async def get_content_files(
    db: Session = Depends(get_db),
    page: int = Query(1, ge=1, description="Номер страницы"),
    limit: int = Query(10, ge=1, le=100, description="Количество файлов на странице"),
    mainCategory: Optional[str] = Query(None, description="Основная категория"),
    subCategory: Optional[str] = Query(None, description="Подкатегория"),
    webdavPath: Optional[str] = Query(None, description="Поиск по пути WebDAV")
):
    """Получение списка файлов контента"""

    # Рассчитываем offset
    offset = (page - 1) * limit

    # Строим базовый запрос
    query = db.query(ContentFile)

    # Применяем фильтры
    if mainCategory:
        query = query.filter(func.lower(ContentFile.mainCategory) == func.lower(mainCategory))

    if subCategory:
        query = query.filter(func.lower(ContentFile.subCategory) == func.lower(subCategory))

    if webdavPath:
        query = query.filter(ContentFile.webdavPath.ilike(f"%{webdavPath}%"))

    # Сортировка по пути
    query = query.order_by(asc(ContentFile.webdavPath))

    # Получаем общее количество для пагинации
    total_count = query.count()

    # Применяем пагинацию
    files = query.offset(offset).limit(limit).all()

    # Подсчитываем страницы
    total_pages = (total_count + limit - 1) // limit

    return {
        "files": [
            {
                "id": file.id,
                "webdavPath": file.webdavPath,
                "mainCategory": file.mainCategory,
                "subCategory": file.subCategory,
                "createdAt": file.createdAt,
                "updatedAt": file.updatedAt
            }
            for file in files
        ],
        "pagination": {
            "page": page,
            "limit": limit,
            "totalCount": total_count,
            "totalPages": total_pages,
            "hasNextPage": page < total_pages,
            "hasPrevPage": page > 1
        }
    }


@router.get("/categories")
async def get_content_categories(db: Session = Depends(get_db)):
    """Получение списка всех категорий контента"""

    try:
        # Получаем файлы с категориями как в Node.js
        files = db.query(ContentFile.mainCategory, ContentFile.subCategory).order_by(
            ContentFile.mainCategory.asc(),
            ContentFile.subCategory.asc()
        ).all()

        # Создаем иерархическую карту
        hierarchy_map = {}

        for main_category, sub_category in files:
            # Пропускаем тестовые категории и подкатегории
            if main_category == 'Test' or sub_category == 'Test':
                continue
            if main_category not in hierarchy_map:
                hierarchy_map[main_category] = set()
            if sub_category:
                hierarchy_map[main_category].add(sub_category)

        # Формируем результат как в Node.js
        result = []
        for main_cat in sorted(hierarchy_map.keys()):
            sub_categories = sorted(list(hierarchy_map[main_cat]))
            result.append({
                "name": main_cat,
                "subCategories": sub_categories
            })

        # Возвращаем массив напрямую как в Node.js
        return result

    except Exception as e:
        logger.error(f"Error getting content categories: {e}")
        raise HTTPException(status_code=500, detail="Failed to fetch hierarchical categories")


@router.get("/categories/{category}/subcategories")
async def get_content_subcategories(category: str, db: Session = Depends(get_db)):
    """Получение подкатегорий для указанной категории"""

    try:
        subcategories = db.query(
            ContentFile.subCategory,
            func.count(ContentFile.id).label("count")
        ).filter(
            func.lower(ContentFile.mainCategory) == func.lower(category),
            ContentFile.subCategory.isnot(None)
        ).group_by(ContentFile.subCategory).all()

        return {
            "subcategories": [
                {
                    "name": subcategory,
                    "count": count
                }
                for subcategory, count in subcategories if subcategory
            ]
        }

    except Exception as e:
        logger.error(f"Error getting content subcategories: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")


@router.get("/blocks/{block_id}")
async def get_content_block(
    block_id: str,
    request: Request,
    db: Session = Depends(get_db)
):
    """Получение конкретного блока контента по ID"""

    block = db.query(ContentBlock).filter(ContentBlock.id == block_id).first()
    if not block:
        raise HTTPException(status_code=404, detail="Block not found")

    # Проверяем аутентификацию для прогресса
    user = get_current_user_from_session(request, db)
    is_authenticated = user is not None
    user_id = user.id if user else None

    base_block = {
        "id": block.id,
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
        "companies": block.companies if block.companies else [],
        "rawBlockContentHash": block.rawBlockContentHash,
        "createdAt": block.createdAt,
        "updatedAt": block.updatedAt
    }

    # Добавляем progressEntries только для авторизованных пользователей
    if is_authenticated and user_id:
        progress_entries = db.query(UserContentProgress).filter(
            UserContentProgress.userId == user_id,
            UserContentProgress.blockId == block.id
        ).all()

        # Форматируем progressEntries как в Node.js
        base_block["progressEntries"] = [
            {
                "id": entry.id,
                "solvedCount": entry.solvedCount,
                "createdAt": entry.createdAt,
                "updatedAt": entry.updatedAt
            }
            for entry in progress_entries
        ]
        
        # Добавляем currentUserSolvedCount для совместимости с frontend
        total_solved_count = sum(entry.solvedCount for entry in progress_entries)
        base_block["currentUserSolvedCount"] = total_solved_count
    else:
        base_block["currentUserSolvedCount"] = 0

    return base_block


# Pydantic models для запросов
class ProgressAction(BaseModel):
    action: str  # "increment" или "decrement"


@router.patch("/blocks/{block_id}/progress")
async def update_content_block_progress(
    block_id: str,
    request: Request,
    action_data: ProgressAction,
    db: Session = Depends(get_db)
):
    """Обновление прогресса пользователя по блоку"""

    # Получаем пользователя (обязательно авторизованного)
    user = get_current_user_from_session_required(request, db)
    user_id = user.id

    action = action_data.action
    if action not in ["increment", "decrement"]:
        raise HTTPException(
            status_code=400,
            detail="Invalid action. Must be 'increment' or 'decrement'"
        )

    try:
        # Проверяем, существует ли блок
        block = db.query(ContentBlock).filter(ContentBlock.id == block_id).first()
        if not block:
            raise HTTPException(status_code=404, detail="Content block not found")

        # Ищем существующую запись прогресса
        progress = db.query(UserContentProgress).filter(
            UserContentProgress.userId == user_id,
            UserContentProgress.blockId == block_id
        ).first()

        if action == "increment":
            if progress:
                progress.solvedCount += 1
            else:
                progress = UserContentProgress(
                    id=str(uuid4()),
                    userId=user_id,
                    blockId=block_id,
                    solvedCount=1
                )
                db.add(progress)
        elif progress and progress.solvedCount > 0:
            progress.solvedCount -= 1
        elif not progress:
            progress = UserContentProgress(
                id=str(uuid4()),
                userId=user_id,
                blockId=block_id,
                solvedCount=0
            )
            db.add(progress)

        # Обновляем категорийный прогресс
        await update_category_progress_from_content_progress(db, user_id, block_id)
        
        # ИСПРАВЛЕНИЕ: Обновляем общую статистику пользователя при изменении UserContentProgress
        await update_user_total_stats_from_content_progress(db, user_id)

        db.commit()
        db.refresh(progress)

        return {
            "userId": progress.userId,
            "blockId": progress.blockId,
            "solvedCount": progress.solvedCount,
            "updatedAt": progress.updatedAt
        }

    except Exception as e:
        logger.error(f"Error updating progress for block {block_id}: {e}")
        db.rollback()
        raise HTTPException(status_code=500, detail="Internal server error")
