#!/usr/bin/env python3
"""Тест работоспособности сервера"""

import sys
sys.path.append('.')

try:
    from main import app
    print("✅ App imported successfully")
    
    print(f"App title: {app.title}")
    print(f"App version: {app.version}")
    print(f"Routes count: {len(app.routes)}")
    
    # List first few routes
    for i, route in enumerate(app.routes[:10]):
        if hasattr(route, 'path'):
            print(f"Route {i+1}: {route.path}")
    
    # Test auth components
    from app.features.auth.services.user_service import UserService
    from app.features.auth.repositories.user_repository import UserRepository
    from app.features.auth.dto.requests import LoginRequest
    
    print("✅ Auth components imported successfully")
    
    # Test dependencies
    from app.shared.dependencies import get_auth_service, get_db
    print("✅ Dependencies imported successfully")
    
    print("🎉 ALL TESTS PASSED!")
    
except Exception as e:
    print(f"❌ ERROR: {e}")
    import traceback
    traceback.print_exc() 
