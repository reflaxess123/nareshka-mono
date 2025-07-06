"""Admin DTOs for API requests and responses."""

from typing import List, Optional, Dict, Any
from pydantic import BaseModel, EmailStr
from datetime import datetime


# Request DTOs
class CreateUserRequest(BaseModel):
    email: EmailStr
    password: str
    role: str = "USER"


class UpdateUserRequest(BaseModel):
    email: Optional[EmailStr] = None
    password: Optional[str] = None
    role: Optional[str] = None


class CreateContentFileRequest(BaseModel):
    webdav_path: str
    main_category: str
    sub_category: str


class UpdateContentFileRequest(BaseModel):
    webdav_path: Optional[str] = None
    main_category: Optional[str] = None
    sub_category: Optional[str] = None


class CreateContentBlockRequest(BaseModel):
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


class UpdateContentBlockRequest(BaseModel):
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


class CreateTheoryCardRequest(BaseModel):
    anki_guid: Optional[str] = None
    card_type: str
    deck: str
    category: str
    sub_category: Optional[str] = None
    question_block: str
    answer_block: str
    tags: List[str] = []
    order_index: int = 0


class UpdateTheoryCardRequest(BaseModel):
    anki_guid: Optional[str] = None
    card_type: Optional[str] = None
    deck: Optional[str] = None
    category: Optional[str] = None
    sub_category: Optional[str] = None
    question_block: Optional[str] = None
    answer_block: Optional[str] = None
    tags: Optional[List[str]] = None
    order_index: Optional[int] = None


class BulkDeleteRequest(BaseModel):
    ids: List[str]


# Response DTOs
class SystemStatsResponse(BaseModel):
    users: Dict[str, int]
    content: Dict[str, int]
    progress: Dict[str, int]


class UserStatsResponse(BaseModel):
    id: str
    email: str
    role: str
    created_at: datetime
    updated_at: datetime
    _count: Dict[str, int] = {}

    class Config:
        from_attributes = True


class ContentStatsResponse(BaseModel):
    total_files: int
    total_blocks: int
    files_by_category: Dict[str, int]
    blocks_by_category: Dict[str, int]


class AdminContentFileResponse(BaseModel):
    id: str
    webdav_path: str
    main_category: str
    sub_category: str
    created_at: datetime
    updated_at: datetime
    _count: Dict[str, int] = {}

    class Config:
        from_attributes = True


class AdminContentBlockResponse(BaseModel):
    id: str
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
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class AdminTheoryCardResponse(BaseModel):
    id: str
    anki_guid: Optional[str] = None
    card_type: str
    deck: str
    category: str
    sub_category: Optional[str] = None
    question_block: str
    answer_block: str
    tags: List[str] = []
    order_index: int = 0
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class AdminUserResponse(BaseModel):
    id: str
    email: str
    role: str
    created_at: datetime
    updated_at: datetime
    _count: Dict[str, int] = {}

    class Config:
        from_attributes = True


class BulkDeleteResponse(BaseModel):
    deleted_count: int
    failed_ids: List[str] = []
    error_messages: List[str] = []

    class Config:
        from_attributes = True


class PaginatedUsersResponse(BaseModel):
    users: List[UserStatsResponse]
    total: int
    page: int
    limit: int
    totalPages: int = 0


class PaginatedContentFilesResponse(BaseModel):
    files: List[AdminContentFileResponse]
    total: int
    page: int
    limit: int
    totalPages: int = 0


class PaginatedContentBlocksResponse(BaseModel):
    blocks: List[AdminContentBlockResponse]
    total: int
    page: int
    limit: int
    totalPages: int = 0


class PaginatedTheoryCardsResponse(BaseModel):
    cards: List[AdminTheoryCardResponse]
    total: int
    page: int
    limit: int
    totalPages: int = 0


class HealthResponse(BaseModel):
    status: str
    module: str 