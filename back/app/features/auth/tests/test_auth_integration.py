"""
Интеграционные тесты для auth модуля
"""

import pytest
from unittest.mock import AsyncMock, MagicMock
from app.shared.models.user import User
from app.features.auth.repositories.user_repository import UserRepository
from app.features.auth.services.user_service import UserService
from app.features.auth.dto.requests import RegisterRequest, LoginRequest
from app.shared.types.common import UserRole


class TestAuthIntegration:
    """Интеграционные тесты auth модуля"""
    
    def test_user_model_creation(self):
        """Тест создания модели User"""
        user = User(
            id=1,
            email="test@example.com",
            username="testuser",
            password_hash="hashed_password",
            first_name="Test",
            last_name="User",
            role=UserRole.USER,
            is_active=True
        )
        
        assert user.id == 1
        assert user.email == "test@example.com"
        assert user.username == "testuser"
        assert user.is_user() == True
        assert user.is_admin() == False
        assert user.has_permission(UserRole.USER) == True
    
    def test_user_repository_creation(self):
        """Тест создания UserRepository"""
        mock_db_manager = MagicMock()
        repository = UserRepository(mock_db_manager)
        assert repository is not None
        assert repository.db_manager == mock_db_manager
    
    def test_user_service_creation(self):
        """Тест создания UserService"""
        mock_repository = MagicMock()
        service = UserService(mock_repository)
        assert service is not None
        assert service.user_repository == mock_repository
    
    def test_password_hashing(self):
        """Тест хеширования паролей"""
        mock_repository = MagicMock()
        service = UserService(mock_repository)
        
        password = "test_password_123"
        hashed = service.hash_password(password)
        
        assert hashed != password
        assert len(hashed) > 20
        assert service.verify_password(password, hashed) == True
        assert service.verify_password("wrong_password", hashed) == False
    
    def test_token_creation(self):
        """Тест создания токенов"""
        mock_repository = MagicMock()
        service = UserService(mock_repository)
        
        user_id = 123
        access_token = service.create_access_token(user_id)
        refresh_token = service.create_refresh_token(user_id)
        
        assert access_token is not None
        assert refresh_token is not None
        assert access_token != refresh_token
        assert len(access_token) > 50
        assert len(refresh_token) > 50
    
    def test_token_verification(self):
        """Тест валидации токенов"""
        mock_repository = MagicMock()
        service = UserService(mock_repository)
        
        user_id = 123
        access_token = service.create_access_token(user_id)
        
        # Проверяем валидный токен
        payload = service.verify_token(access_token, "access")
        assert payload["sub"] == str(user_id)
        assert payload["type"] == "access"
        
        # Проверяем неверный тип токена
        with pytest.raises(Exception):
            service.verify_token(access_token, "refresh")
    
    def test_request_dto_validation(self):
        """Тест валидации request DTOs"""
        # Валидный запрос регистрации
        register_request = RegisterRequest(
            email="test@example.com",
            username="testuser",
            password="SecurePass123!",
            first_name="Test",
            last_name="User"
        )
        
        assert register_request.email == "test@example.com"
        assert register_request.username == "testuser"
        
        # Валидный запрос логина
        login_request = LoginRequest(
            email_or_username="test@example.com",
            password="SecurePass123!"
        )
        
        assert login_request.email_or_username == "test@example.com"
        assert login_request.password == "SecurePass123!"
    
    def test_user_permissions(self):
        """Тест системы ролей и разрешений"""
        # Обычный пользователь
        user = User(
            id=1,
            email="user@example.com",
            username="user",
            password_hash="hash",
            role=UserRole.USER,
            is_active=True
        )
        
        assert user.is_user() == True
        assert user.is_admin() == False
        assert user.has_permission(UserRole.USER) == True
        assert user.has_permission(UserRole.ADMIN) == False
        
        # Администратор
        admin = User(
            id=2,
            email="admin@example.com",
            username="admin",
            password_hash="hash",
            role=UserRole.ADMIN,
            is_active=True
        )
        
        assert admin.is_user() == True  # Admin тоже user
        assert admin.is_admin() == True
        assert admin.has_permission(UserRole.USER) == True
        assert admin.has_permission(UserRole.ADMIN) == True


if __name__ == "__main__":
    # Простой запуск тестов
    test = TestAuthIntegration()
    
    print("🧪 Running auth integration tests...")
    
    try:
        test.test_user_model_creation()
        print("✅ User model creation")
        
        test.test_user_repository_creation()
        print("✅ User repository creation")
        
        test.test_user_service_creation()
        print("✅ User service creation")
        
        test.test_password_hashing()
        print("✅ Password hashing")
        
        test.test_token_creation()
        print("✅ Token creation")
        
        test.test_token_verification()
        print("✅ Token verification")
        
        test.test_request_dto_validation()
        print("✅ Request DTO validation")
        
        test.test_user_permissions()
        print("✅ User permissions")
        
        print("\n🎉 All auth tests passed!")
        
    except Exception as e:
        print(f"\n❌ Test failed: {e}")
        import traceback
        traceback.print_exc() 


