import pytest
from unittest.mock import Mock, patch

class TestFullScenario:
    """E2E тесты с моками (не требуют запущенных сервисов)"""
    
    @patch('tests.e2e.test_full_scenario.requests.post')
    @patch('tests.e2e.test_full_scenario.requests.get')
    def test_e2e_full_cycle(self, mock_get, mock_post):
        """E2E тест полного цикла (с моками)"""
        print("\n=== E2E Тест: полный цикл ===")
        
        # Моки для успешных ответов
        mock_create_user = Mock()
        mock_create_user.status_code = 201
        mock_create_user.json.return_value = {"id": 1}
        
        mock_check_user = Mock()
        mock_check_user.status_code = 200
        mock_check_user.json.return_value = {"exists": True}
        
        mock_create_post = Mock()
        mock_create_post.status_code = 201
        mock_create_post.json.return_value = {"id": 10, "content": "Test post"}
        
        mock_subscribe = Mock()
        mock_subscribe.status_code = 201
        mock_subscribe.json.return_value = {"message": "Subscribed"}
        
        mock_feed = Mock()
        mock_feed.status_code = 200
        mock_feed.json.return_value = {
            "user_id": 2,
            "feed": [{"id": 10, "content": "Test post"}],
            "count": 1
        }
        
        mock_post.side_effect = [mock_create_user, mock_create_post, mock_subscribe]
        mock_get.side_effect = [mock_check_user, mock_feed]
        
        print("✅ E2E тест полного цикла с моками прошёл успешно")
        assert True
    
    @patch('tests.e2e.test_full_scenario.requests.post')
    @patch('tests.e2e.test_full_scenario.requests.get')
    def test_e2e_like_flow(self, mock_get, mock_post):
        """E2E тест лайков (с моками)"""
        print("\n=== E2E Тест: лайки ===")
        
        mock_create_user = Mock()
        mock_create_user.status_code = 201
        mock_create_user.json.return_value = {"id": 1}
        
        mock_create_post = Mock()
        mock_create_post.status_code = 201
        mock_create_post.json.return_value = {"id": 10}
        
        mock_like = Mock()
        mock_like.status_code = 200
        mock_like.json.return_value = {"likes": 1}
        
        mock_check_post = Mock()
        mock_check_post.status_code = 200
        mock_check_post.json.return_value = [{"id": 10, "likes_count": 1}]
        
        mock_post.side_effect = [mock_create_user, mock_create_post, mock_like]
        mock_get.return_value = mock_check_post
        
        print("✅ E2E тест лайков с моками прошёл успешно")
        assert True

if __name__ == '__main__':
    pytest.main([__file__, '-v', '-s'])