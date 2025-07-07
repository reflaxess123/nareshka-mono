"""Маппер для Content entities"""

from typing import List, Optional
from datetime import datetime

from ...domain.entities.content import ContentFile as DomainContentFile, ContentBlock as DomainContentBlock, UserContentProgress as DomainUserContentProgress
from ...domain.entities.enums import ProgressStatus
from ..models.content_models import ContentFile as InfraContentFile, ContentBlock as InfraContentBlock, UserContentProgress as InfraUserContentProgress


class ContentMapper:
    """Маппер для конвертации Content entities между domain и infrastructure слоями"""
    
    @staticmethod
    def content_file_to_domain(infra_content_file: InfraContentFile) -> DomainContentFile:
        """Конвертирует Infrastructure ContentFile в Domain ContentFile"""
        if not infra_content_file:
            return None
            
        return DomainContentFile(
            id=infra_content_file.id,
            webdavPath=infra_content_file.webdavPath,
            mainCategory=infra_content_file.mainCategory,
            subCategory=infra_content_file.subCategory,
            lastFileHash=infra_content_file.lastFileHash,
            createdAt=infra_content_file.createdAt,
            updatedAt=infra_content_file.updatedAt
        )
    
    @staticmethod
    def content_file_to_infrastructure(domain_content_file: DomainContentFile) -> InfraContentFile:
        """Конвертирует Domain ContentFile в Infrastructure ContentFile"""
        if not domain_content_file:
            return None
            
        return InfraContentFile(
            id=domain_content_file.id,
            webdavPath=domain_content_file.webdavPath,
            mainCategory=domain_content_file.mainCategory,
            subCategory=domain_content_file.subCategory,
            lastFileHash=domain_content_file.lastFileHash,
            createdAt=domain_content_file.createdAt,
            updatedAt=domain_content_file.updatedAt
        )
    
    @staticmethod
    def content_block_to_domain(infra_content_block: InfraContentBlock) -> DomainContentBlock:
        """Конвертирует Infrastructure ContentBlock в Domain ContentBlock"""
        if not infra_content_block:
            return None
            
        return DomainContentBlock(
            id=infra_content_block.id,
            fileId=infra_content_block.fileId,
            pathTitles=infra_content_block.pathTitles or [],
            blockTitle=infra_content_block.blockTitle,
            blockLevel=infra_content_block.blockLevel,
            orderInFile=infra_content_block.orderInFile,
            textContent=infra_content_block.textContent,
            codeContent=infra_content_block.codeContent,
            codeLanguage=infra_content_block.codeLanguage,
            isCodeFoldable=infra_content_block.isCodeFoldable or False,
            codeFoldTitle=infra_content_block.codeFoldTitle,
            extractedUrls=infra_content_block.extractedUrls or [],
            companies=infra_content_block.companies or [],
            rawBlockContentHash=infra_content_block.rawBlockContentHash,
            createdAt=infra_content_block.createdAt,
            updatedAt=infra_content_block.updatedAt
        )
    
    @staticmethod
    def content_block_to_infrastructure(domain_content_block: DomainContentBlock) -> InfraContentBlock:
        """Конвертирует Domain ContentBlock в Infrastructure ContentBlock"""
        if not domain_content_block:
            return None
            
        return InfraContentBlock(
            id=domain_content_block.id,
            fileId=domain_content_block.fileId,
            pathTitles=domain_content_block.pathTitles,
            blockTitle=domain_content_block.blockTitle,
            blockLevel=domain_content_block.blockLevel,
            orderInFile=domain_content_block.orderInFile,
            textContent=domain_content_block.textContent,
            codeContent=domain_content_block.codeContent,
            codeLanguage=domain_content_block.codeLanguage,
            isCodeFoldable=domain_content_block.isCodeFoldable,
            codeFoldTitle=domain_content_block.codeFoldTitle,
            extractedUrls=domain_content_block.extractedUrls,
            companies=domain_content_block.companies,
            rawBlockContentHash=domain_content_block.rawBlockContentHash,
            createdAt=domain_content_block.createdAt,
            updatedAt=domain_content_block.updatedAt
        )
    
    @staticmethod
    def user_content_progress_to_domain(infra_progress: InfraUserContentProgress) -> DomainUserContentProgress:
        """Конвертирует Infrastructure UserContentProgress в Domain UserContentProgress"""
        if not infra_progress:
            return None
            
        return DomainUserContentProgress(
            id=infra_progress.id,
            userId=infra_progress.userId,
            blockId=infra_progress.blockId,
            solvedCount=infra_progress.solvedCount,
            createdAt=infra_progress.createdAt,
            updatedAt=infra_progress.updatedAt
        )
    
    @staticmethod
    def user_content_progress_to_infrastructure(domain_progress: DomainUserContentProgress) -> InfraUserContentProgress:
        """Конвертирует Domain UserContentProgress в Infrastructure UserContentProgress"""
        if not domain_progress:
            return None
            
        return InfraUserContentProgress(
            id=domain_progress.id,
            userId=domain_progress.userId,
            blockId=domain_progress.blockId,
            solvedCount=domain_progress.solvedCount,
            createdAt=domain_progress.createdAt,
            updatedAt=domain_progress.updatedAt
        )
    
    @staticmethod
    def content_file_list_to_domain(infra_files: List[InfraContentFile]) -> List[DomainContentFile]:
        """Конвертирует список Infrastructure ContentFiles в Domain ContentFiles"""
        if not infra_files:
            return []
        return [ContentMapper.content_file_to_domain(file) for file in infra_files if file]
    
    @staticmethod
    def content_block_list_to_domain(infra_blocks: List[InfraContentBlock]) -> List[DomainContentBlock]:
        """Конвертирует список Infrastructure ContentBlocks в Domain ContentBlocks"""
        if not infra_blocks:
            return []
        return [ContentMapper.content_block_to_domain(block) for block in infra_blocks if block]
    
    @staticmethod
    def user_content_progress_list_to_domain(infra_progress: List[InfraUserContentProgress]) -> List[DomainUserContentProgress]:
        """Конвертирует список Infrastructure UserContentProgress в Domain UserContentProgress"""
        if not infra_progress:
            return []
        return [ContentMapper.user_content_progress_to_domain(progress) for progress in infra_progress if progress] 