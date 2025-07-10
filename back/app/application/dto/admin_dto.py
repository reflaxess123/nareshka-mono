"""DTO для административных операций"""

from typing import Dict, List, Optional

from pydantic import EmailStr

from .base_dto import (
    BaseResponse,
    BulkActionRequest,
    BulkActionResponse,
    CreateRequest,
    IdentifiedResponse,
    PaginatedResponse,
    UpdateRequest,
)


# Request DTOs
class CreateUserRequest(CreateRequest):
    email: EmailStr
    password: str
    role: str = "USER"


class UpdateUserRequest(UpdateRequest):
    email: Optional[EmailStr] = None
    password: Optional[str] = None
    role: Optional[str] = None


class CreateContentFileRequest(CreateRequest):
    webdav_path: str
    main_category: str
    sub_category: str


class UpdateContentFileRequest(UpdateRequest):
    webdav_path: Optional[str] = None
    main_category: Optional[str] = None
    sub_category: Optional[str] = None


class CreateContentBlockRequest(CreateRequest):
    file_id: str
    path_titles: List[str]
    block_title: str
    block_level: int
    order_in_file: int
    text_content: Optional[str] = None
    code_content: Optional[str] = None
    code_language: Optional[str] = None
    is_code_foldable: bool = False
    code_fold_title: Optional[str] = None
    extracted_urls: List[str] = []


class UpdateContentBlockRequest(UpdateRequest):
    file_id: Optional[str] = None
    path_titles: Optional[List[str]] = None
    block_title: Optional[str] = None
    block_level: Optional[int] = None
    order_in_file: Optional[int] = None
    text_content: Optional[str] = None
    code_content: Optional[str] = None
    code_language: Optional[str] = None
    is_code_foldable: Optional[bool] = None
    code_fold_title: Optional[str] = None
    extracted_urls: Optional[List[str]] = None


class CreateTheoryCardRequest(CreateRequest):
    anki_guid: Optional[str] = None
    card_type: str
    deck: str
    category: str
    sub_category: Optional[str] = None
    question_block: str
    answer_block: str
    tags: List[str] = []
    order_index: int = 0


class UpdateTheoryCardRequest(UpdateRequest):
    anki_guid: Optional[str] = None
    card_type: Optional[str] = None
    deck: Optional[str] = None
    category: Optional[str] = None
    sub_category: Optional[str] = None
    question_block: Optional[str] = None
    answer_block: Optional[str] = None
    tags: Optional[List[str]] = None
    order_index: Optional[int] = None


BulkDeleteRequest = BulkActionRequest  # Алиас для совместимости


# Response DTOs
class SystemStatsResponse(BaseResponse):
    users: Dict[str, int]
    content: Dict[str, int]
    progress: Dict[str, int]


class UserStatsResponse(IdentifiedResponse):
    id: int  # User ID - integer
    email: str
    role: str
    _count: Dict[str, int] = {}


class ContentStatsResponse(BaseResponse):
    total_files: int
    total_blocks: int
    files_by_category: Dict[str, int]
    blocks_by_category: Dict[str, int]


class AdminContentFileResponse(IdentifiedResponse):
    id: str  # ContentFile ID - string
    webdav_path: str
    main_category: str
    sub_category: str
    _count: Dict[str, int] = {}


class AdminContentBlockResponse(IdentifiedResponse):
    id: str  # ContentBlock ID - string
    file_id: str
    path_titles: List[str]
    block_title: str
    block_level: int
    order_in_file: int
    text_content: Optional[str] = None
    code_content: Optional[str] = None
    code_language: Optional[str] = None
    is_code_foldable: bool = False
    code_fold_title: Optional[str] = None
    extracted_urls: List[str] = []


class AdminTheoryCardResponse(IdentifiedResponse):
    id: str  # TheoryCard ID - string
    anki_guid: Optional[str] = None
    card_type: str
    deck: str
    category: str
    sub_category: Optional[str] = None
    question_block: str
    answer_block: str
    tags: List[str] = []
    order_index: int = 0


class AdminUserResponse(IdentifiedResponse):
    id: int  # User ID - integer
    email: str
    role: str
    _count: Dict[str, int] = {}


# Используем алиас BulkActionResponse для совместимости
BulkDeleteResponse = BulkActionResponse


# Типизированные пагинированные ответы - заменяют 4 дублирующихся класса
PaginatedUsersResponse = PaginatedResponse[UserStatsResponse]
PaginatedContentFilesResponse = PaginatedResponse[AdminContentFileResponse]
PaginatedContentBlocksResponse = PaginatedResponse[AdminContentBlockResponse]
PaginatedTheoryCardsResponse = PaginatedResponse[AdminTheoryCardResponse]


class HealthResponse(BaseResponse):
    status: str
    module: str
