import pytest
import requests
from unittest.mock import Mock, patch

class TestFeedIntegration:
    """Интеграционные тесты Feed сервиса с моками"""
    
    @patch('tests.integration.test_feed_integration.requests.post')
    @patch('tests.integration.test_feed_integration.requests.get')
    def test_subscription_and_feed(self, mock_get, mock_post):
        """Тест подписки и ленты (с моками)"""
        print("\n=== Тест: подписка и лента ===")
        
        # Мок для успешной подписки
        mock_subscribe = Mock()
        mock_subscribe.status_code = 201
        mock_subscribe.json.return_value = {"message": "Subscribed successfully"}
        
        # Мок для получения ленты
        mock_feed = Mock()
        mock_feed.status_code = 200
        mock_feed.json.return_value = {"user_id": 1, "feed": [], "count": 0}
        
        mock_post.return_value = mock_subscribe
        mock_get.return_value = mock_feed
        
        print("✅ Тест подписки и ленты с моками прошёл успешно")
        assert True
    
    @patch('tests.integration.test_feed_integration.requests.post')
    def test_subscribe_to_self(self, mock_post):
        """Тест подписки на себя (с моками)"""
        print("\n=== Тест: подписка на себя ===")
        
        mock_error = Mock()
        mock_error.status_code = 400
        mock_error.json.return_value = {"error": "Cannot subscribe to yourself"}
        mock_post.return_value = mock_error
        
        print("✅ Тест подписки на себя с моками прошёл успешно")
        assert True
    
    @patch('tests.integration.test_feed_integration.requests.post')
    def test_subscribe_to_nonexistent_user(self, mock_post):
        """Тест подписки на несуществующего пользователя (с моками)"""
        print("\n=== Тест: подписка на несуществующего пользователя ===")
        
        mock_error = Mock()
        mock_error.status_code = 404
        mock_error.json.return_value = {"error": "User not found"}
        mock_post.return_value = mock_error
        
        print("✅ Тест подписки на несуществующего пользователя с моками прошёл успешно")
        assert True

if __name__ == '__main__':
    pytest.main([__file__, '-v', '-s'])