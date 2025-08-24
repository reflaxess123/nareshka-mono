"""
Интеграционные тесты для auth модуля
"""

from unittest.mock import MagicMock
import pytest

from app.features.auth.dto.auth_dto import LoginRequest, RegisterRequest, UserResponse
from app.features.auth.services.auth_service import AuthService
from app.features.auth.repositories.sqlalchemy_user_repository import SQLAlchemyUserRepository
from app.shared.models.user_models import User
from app.shared.models.enums import UserRole


class TestAuthIntegration:
    """Интеграционные тесты auth модуля"""

    def test_auth_service_creation(self):
        """Тест создания AuthService"""
        mock_repository = MagicMock()
        service = AuthService(mock_repository)
        
        assert service is not None
        assert service.user_repository == mock_repository
        assert service.pwd_context is not None
        assert service.redis_client is not None

    def test_user_repository_creation(self):
        """Тест создания SQLAlchemyUserRepository"""
        repository = SQLAlchemyUserRepository()
        assert repository is not None

    def test_password_hashing(self):
        """Тест хеширования паролей"""
        mock_repository = MagicMock()
        service = AuthService(mock_repository)

        password = "test_password_123"
        hashed = service.get_password_hash(password)

        assert hashed != password
        assert len(hashed) > 20
        assert service.verify_password(password, hashed) == True
        assert service.verify_password("wrong_password", hashed) == False

    def test_login_request_validation(self):
        """Тест валидации LoginRequest"""
        # Валидный запрос логина
        login_request = LoginRequest(
            email="test@example.com",
            password="SecurePass123!"
        )

        assert login_request.email == "test@example.com"
        assert login_request.password == "SecurePass123!"

    def test_register_request_validation(self):
        """Тест валидации RegisterRequest"""
        # Валидный запрос регистрации
        register_request = RegisterRequest(
            email="newuser@example.com",
            password="SecurePass123!"
        )

        assert register_request.email == "newuser@example.com"
        assert register_request.password == "SecurePass123!"

    def test_user_response_creation(self):
        """Тест создания UserResponse из User модели"""
        # Создаем мок User объект
        mock_user = MagicMock()
        mock_user.id = 1
        mock_user.email = "test@example.com"
        mock_user.role = UserRole.USER
        mock_user.totalTasksSolved = 5
        mock_user.lastActivityDate = None
        mock_user.createdAt = "2024-01-01T00:00:00Z"
        mock_user.updatedAt = "2024-01-01T00:00:00Z"

        # Мокаем hasattr для дополнительных полей
        def mock_hasattr(obj, attr):
            return attr in ['username', 'first_name', 'last_name', 'full_name', 
                          'display_name', 'is_active', 'is_verified', 'updatedAt']
        
        # Мокаем значения дополнительных полей
        mock_user.username = None
        mock_user.first_name = None
        mock_user.last_name = None
        mock_user.full_name = None
        mock_user.display_name = "test"
        mock_user.is_active = True
        mock_user.is_verified = True

        # Патчим hasattr
        import builtins
        original_hasattr = builtins.hasattr
        builtins.hasattr = mock_hasattr

        try:
            user_response = UserResponse.from_user(mock_user)
            
            assert user_response.id == 1
            assert user_response.email == "test@example.com"
            assert user_response.role == UserRole.USER
            assert user_response.totalTasksSolved == 5
            assert user_response.display_name == "test"
        finally:
            # Восстанавливаем оригинальный hasattr
            builtins.hasattr = original_hasattr

    def test_session_operations(self):
        """Тест операций с сессиями"""
        mock_repository = MagicMock()
        service = AuthService(mock_repository)

        # Тест создания сессии
        try:
            service.create_session(user_id=123, session_id="test-session-id")
            # Не должно выбрасывать исключение при graceful degradation
        except Exception as e:
            # Ожидаем только Redis-related ошибки при тестах
            assert "redis" in str(e).lower()

        # Тест получения user_id из сессии
        user_id = service.get_session_user_id("nonexistent-session")
        # При graceful degradation должен вернуть None
        assert user_id is None

        # Тест удаления сессии
        try:
            service.delete_session("test-session-id")
            # Не должно выбрасывать исключение при graceful degradation
        except Exception as e:
            # Ожидаем только Redis-related ошибки при тестах
            assert "redis" in str(e).lower()


if __name__ == "__main__":
    # Простой запуск тестов
    test = TestAuthIntegration()

    print("🧪 Running auth integration tests...")

    try:
        test.test_auth_service_creation()
        print("✅ Auth service creation")

        test.test_user_repository_creation()
        print("✅ User repository creation")

        test.test_password_hashing()
        print("✅ Password hashing")

        test.test_login_request_validation()
        print("✅ Login request validation")

        test.test_register_request_validation()
        print("✅ Register request validation")

        test.test_user_response_creation()
        print("✅ User response creation")

        test.test_session_operations()
        print("✅ Session operations")

        print("\n🎉 All auth tests passed!")

    except Exception as e:
        print(f"\n❌ Test failed: {e}")
        import traceback
        traceback.print_exc()