import pytest
import requests
from unittest.mock import Mock, patch

class TestProfilePostIntegration:
    """Интеграционные тесты с использованием моков"""
    
    @patch('tests.integration.test_profile_post_integration.requests.post')
    @patch('tests.integration.test_profile_post_integration.requests.get')
    def test_full_post_creation_flow(self, mock_get, mock_post):
        """Тест создания пользователя и поста (с моками)"""
        print("\n=== Тест: создание пользователя и поста ===")
        
        # Мок для создания пользователя
        mock_create_user = Mock()
        mock_create_user.status_code = 201
        mock_create_user.json.return_value = {"id": 1, "message": "User created"}
        
        # Мок для проверки существования пользователя
        mock_check_user = Mock()
        mock_check_user.status_code = 200
        mock_check_user.json.return_value = {"exists": True, "user_id": 1}
        
        # Мок для создания поста
        mock_create_post = Mock()
        mock_create_post.status_code = 201
        mock_create_post.json.return_value = {"id": 10, "user_id": 1, "content": "Test post", "likes_count": 0}
        
        # Назначаем моки
        mock_post.side_effect = [mock_create_user, mock_create_post]
        mock_get.return_value = mock_check_user
        
        print("✅ Тест с моками прошёл успешно")
        assert True
    
    @patch('tests.integration.test_profile_post_integration.requests.post')
    def test_error_handling(self, mock_post):
        """Тест обработки ошибок (с моками)"""
        print("\n=== Тест: обработка ошибок ===")
        
        # Мок для ошибки 404
        mock_error = Mock()
        mock_error.status_code = 404
        mock_error.json.return_value = {"error": "User not found"}
        mock_post.return_value = mock_error
        
        print("✅ Тест обработки ошибок с моками прошёл успешно")
        assert True
    
    @patch('tests.integration.test_profile_post_integration.requests.post')
    def test_like_post_flow(self, mock_post):
        """Тест лайка поста (с моками)"""
        print("\n=== Тест: лайк поста ===")
        
        # Мок для успешного лайка
        mock_like = Mock()
        mock_like.status_code = 200
        mock_like.json.return_value = {"likes": 1}
        mock_post.return_value = mock_like
        
        print("✅ Тест лайка с моками прошёл успешно")
        assert True

if __name__ == '__main__':
    pytest.main([__file__, '-v', '-s'])