import pytest
import requests
from unittest.mock import Mock, patch
import json

# Мокируем ProfileAdapter
class ProfileAdapter:
    def __init__(self, base_url):
        self.base_url = base_url
    
    def check_user_exists(self, user_id):
        try:
            response = requests.get(f"{self.base_url}/profile/check/{user_id}")
            if response.status_code == 200:
                return response.json().get('exists', False)
            return False
        except:
            return False
    
    def get_profile(self, user_id):
        try:
            response = requests.get(f"{self.base_url}/profile/{user_id}")
            if response.status_code == 200:
                return response.json()
            return None
        except:
            return None
    
    def create_profile(self, username, email, bio):
        try:
            response = requests.post(
                f"{self.base_url}/profile",
                json={"username": username, "email": email, "bio": bio}
            )
            if response.status_code == 201:
                return response.json()
            return None
        except:
            return None

class TestProfileAdapter:
    """Unit-тесты для Profile Adapter"""
    
    def setup_method(self):
        """Подготовка перед каждым тестом"""
        self.adapter = ProfileAdapter("http://localhost:5001")
    
    @patch('tests.unit.test_profile_adapter.requests.get')
    def test_check_user_exists_success(self, mock_get):
        """Тест: успешная проверка существования пользователя"""
        # Подготавливаем мок-ответ
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"exists": True, "user_id": 1}
        mock_get.return_value = mock_response
        
        # Выполняем тест
        result = self.adapter.check_user_exists(1)
        
        # Проверяем результат
        assert result == True
        mock_get.assert_called_once_with("http://localhost:5001/profile/check/1")
    
    @patch('tests.unit.test_profile_adapter.requests.get')
    def test_check_user_exists_not_found(self, mock_get):
        """Тест: пользователь не найден"""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"exists": False, "user_id": 999}
        mock_get.return_value = mock_response
        
        result = self.adapter.check_user_exists(999)
        
        assert result == False
    
    @patch('tests.unit.test_profile_adapter.requests.get')
    def test_check_user_exists_connection_error(self, mock_get):
        """Тест: ошибка соединения с сервером"""
        mock_get.side_effect = requests.exceptions.ConnectionError()
        
        result = self.adapter.check_user_exists(1)
        
        assert result == False
    
    @patch('tests.unit.test_profile_adapter.requests.get')
    def test_get_profile_success(self, mock_get):
        """Тест: успешное получение профиля"""
        expected_profile = {
            "id": 1,
            "username": "alice",
            "email": "alice@test.com",
            "bio": "Hello!"
        }
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = expected_profile
        mock_get.return_value = mock_response
        
        result = self.adapter.get_profile(1)
        
        assert result == expected_profile
        assert result["username"] == "alice"
    
    @patch('tests.unit.test_profile_adapter.requests.get')
    def test_get_profile_not_found(self, mock_get):
        """Тест: профиль не найден"""
        mock_response = Mock()
        mock_response.status_code = 404
        mock_get.return_value = mock_response
        
        result = self.adapter.get_profile(999)
        
        assert result is None
    
    @patch('tests.unit.test_profile_adapter.requests.post')
    def test_create_profile_success(self, mock_post):
        """Тест: успешное создание профиля"""
        expected_response = {"id": 5, "message": "User created"}
        mock_response = Mock()
        mock_response.status_code = 201
        mock_response.json.return_value = expected_response
        mock_post.return_value = mock_response
        
        result = self.adapter.create_profile("newuser", "new@test.com", "New bio")
        
        assert result == expected_response
        assert result["id"] == 5
        
        # Проверяем, что запрос был с правильными данными
        call_args = mock_post.call_args
        assert call_args[1]["json"]["username"] == "newuser"
        assert call_args[1]["json"]["email"] == "new@test.com"

if __name__ == '__main__':
    pytest.main([__file__, '-v'])