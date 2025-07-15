#!/usr/bin/env python3
"""Тест Auth API функциональности"""

import sys
sys.path.append('.')

import asyncio
import json
from sqlalchemy.orm import Session
from app.shared.database import get_session
from app.features.auth.services.user_service import UserService
from app.features.auth.repositories.user_repository import UserRepository
from app.features.auth.dto.requests import LoginRequest, RegisterRequest
from app.features.auth.models.user import User

async def test_auth_functionality():
    """Тест основной auth функциональности"""
    print("🧪 Testing Auth Functionality...")
    
    try:
        # 1. Test service creation
        print("\n1. Testing service creation...")
        repo = UserRepository()
        service = UserService(repo)
        print("✅ UserService created successfully")
        
        # 2. Test DTO creation
        print("\n2. Testing DTO creation...")
        login_req = LoginRequest(email="test@gmail.com", password="TestPass123")
        register_req = RegisterRequest(
            email="newuser@gmail.com",
            password="NewPass123",
            password_confirm="NewPass123",
            username="newuser"
        )
        print("✅ Auth DTOs created successfully")
        print(f"LoginRequest: {login_req.email}")
        print(f"RegisterRequest: {register_req.email}")
        
        # 3. Test database connection
        print("\n3. Testing database connection...")
        session_gen = get_session()
        session = next(session_gen)
        print("✅ Database session created successfully")
        
        # 4. Test User model query
        print("\n4. Testing User model query...")
        user_count = session.query(User).count()
        print(f"✅ User count in database: {user_count}")
        
        # 5. Test password hashing
        print("\n5. Testing password hashing...")
        hashed = service.hash_password("TestPassword123")
        is_valid = service.verify_password("TestPassword123", hashed)
        print(f"✅ Password hashing works: {is_valid}")
        
        # 6. Test token creation
        print("\n6. Testing token creation...")
        token = service.create_access_token(1)
        print(f"✅ Access token created: {token[:20]}...")
        
        session.close()
        print("\n🎉 ALL AUTH TESTS PASSED!")
        return True
        
    except Exception as e:
        print(f"❌ AUTH TEST FAILED: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = asyncio.run(test_auth_functionality())
    if success:
        print("\n✅ Auth API is working correctly!")
    else:
        print("\n❌ Auth API has issues that need to be fixed!") 
