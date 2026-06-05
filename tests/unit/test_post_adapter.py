import pytest
import requests
from unittest.mock import Mock, patch

class PostAdapter:
    def __init__(self, base_url):
        self.base_url = base_url
    
    def create_post(self, user_id, content):
        try:
            response = requests.post(
                f"{self.base_url}/posts",
                json={"user_id": user_id, "content": content}
            )
            if response.status_code == 201:
                return response.json()
            return None
        except:
            return None
    
    def get_posts_by_user(self, user_id):
        try:
            response = requests.get(f"{self.base_url}/posts/user/{user_id}")
            if response.status_code == 200:
                return response.json()
            return []
        except:
            return []
    
    def like_post(self, post_id):
        try:
            response = requests.post(f"{self.base_url}/posts/{post_id}/like")
            return response.status_code == 200
        except:
            return False

class TestPostAdapter:
    """Unit-тесты для Post Adapter"""
    
    def setup_method(self):
        self.adapter = PostAdapter("http://localhost:5002")
    
    @patch('tests.unit.test_post_adapter.requests.post')
    def test_create_post_success(self, mock_post):
        """Тест: успешное создание поста"""
        expected_post = {
            "id": 10,
            "user_id": 1,
            "content": "Test post",
            "likes_count": 0
        }
        mock_response = Mock()
        mock_response.status_code = 201
        mock_response.json.return_value = expected_post
        mock_post.return_value = mock_response
        
        result = self.adapter.create_post(1, "Test post")
        
        assert result == expected_post
        assert result["id"] == 10
        assert result["content"] == "Test post"
    
    @patch('tests.unit.test_post_adapter.requests.post')
    def test_create_post_validation_error(self, mock_post):
        """Тест: ошибка валидации при создании поста"""
        mock_response = Mock()
        mock_response.status_code = 400
        mock_post.return_value = mock_response
        
        result = self.adapter.create_post(None, "")
        
        assert result is None
    
    @patch('tests.unit.test_post_adapter.requests.get')
    def test_get_posts_by_user_success(self, mock_get):
        """Тест: успешное получение постов пользователя"""
        expected_posts = [
            {"id": 1, "user_id": 1, "content": "Post 1"},
            {"id": 2, "user_id": 1, "content": "Post 2"}
        ]
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = expected_posts
        mock_get.return_value = mock_response
        
        result = self.adapter.get_posts_by_user(1)
        
        assert len(result) == 2
        assert result[0]["content"] == "Post 1"
    
    @patch('tests.unit.test_post_adapter.requests.get')
    def test_get_posts_by_user_empty(self, mock_get):
        """Тест: у пользователя нет постов"""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = []
        mock_get.return_value = mock_response
        
        result = self.adapter.get_posts_by_user(5)
        
        assert result == []
    
    @patch('tests.unit.test_post_adapter.requests.post')
    def test_like_post_success(self, mock_post):
        """Тест: успешный лайк поста"""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_post.return_value = mock_response
        
        result = self.adapter.like_post(1)
        
        assert result == True
    
    @patch('tests.unit.test_post_adapter.requests.post')
    def test_like_post_not_found(self, mock_post):
        """Тест: лайк несуществующего поста"""
        mock_response = Mock()
        mock_response.status_code = 404
        mock_post.return_value = mock_response
        
        result = self.adapter.like_post(999)
        
        assert result == False

if __name__ == '__main__':
    pytest.main([__file__, '-v'])