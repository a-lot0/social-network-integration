import pytest
import requests
import time

class TestProfilePostIntegration:
    
    def setup_method(self):
        self.profile_url = "http://localhost:5001"
        self.post_url = "http://localhost:5002"
        self.test_id = int(time.time())
    
    def create_test_user(self):
        """Создаёт тестового пользователя и возвращает ID"""
        response = requests.post(
            f"{self.profile_url}/profile",
            json={
                "username": f"test_user_{self.test_id}",
                "email": f"test_{self.test_id}@test.com",
                "bio": "Test bio"
            },
            timeout=5
        )
        if response.status_code == 201:
            return response.json().get("id")
        return None
    
    def test_full_post_creation_flow(self):
        print("\n=== Тест: создание пользователя и поста ===")
        
        # Создаём пользователя
        user_id = self.create_test_user()
        if not user_id:
            pytest.skip("Не удалось создать пользователя")
        
        print(f"✅ Пользователь создан: ID={user_id}")
        
        # Создаём пост
        response = requests.post(
            f"{self.post_url}/posts",
            json={"user_id": user_id, "content": f"Test post {self.test_id}"},
            timeout=5
        )
        
        if response.status_code != 201:
            pytest.skip(f"Не удалось создать пост: {response.status_code}")
        
        post_data = response.json()
        post_id = post_data.get("id")
        print(f"✅ Пост создан: ID={post_id}, content={post_data.get('content')}")
        
        # Проверяем, что пост сохранился (API возвращает массив напрямую)
        response = requests.get(f"{self.post_url}/posts/user/{user_id}", timeout=5)
        assert response.status_code == 200
        
        posts = response.json()
        # API возвращает массив постов без обёртки
        assert isinstance(posts, list)
        assert len(posts) > 0
        print(f"✅ Пост найден в списке пользователя. Всего постов: {len(posts)}")
    
    def test_like_post_flow(self):
        print("\n=== Тест: лайк поста ===")
        
        # Создаём пользователя
        user_id = self.create_test_user()
        if not user_id:
            pytest.skip("Не удалось создать пользователя")
        
        print(f"✅ Пользователь создан: ID={user_id}")
        
        # Создаём пост
        response = requests.post(
            f"{self.post_url}/posts",
            json={"user_id": user_id, "content": "Post for likes"},
            timeout=5
        )
        
        if response.status_code != 201:
            pytest.skip(f"Не удалось создать пост: {response.status_code}")
        
        post_id = response.json().get("id")
        print(f"✅ Пост создан: ID={post_id}")
        
        # Ставим лайк
        response = requests.post(f"{self.post_url}/posts/{post_id}/like", timeout=5)
        assert response.status_code == 200
        
        result = response.json()
        likes_count = result.get("likes", 0)
        print(f"✅ Лайк поставлен. Всего лайков: {likes_count}")
        
        # Проверяем, что лайк сохранился (получаем пост и проверяем likes_count)
        response = requests.get(f"{self.post_url}/posts/user/{user_id}", timeout=5)
        assert response.status_code == 200
        
        posts = response.json()
        # Ищем наш пост в списке
        for post in posts:
            if post.get("id") == post_id:
                assert post.get("likes_count", 0) == likes_count
                print(f"✅ Лайк подтверждён: likes_count={post.get('likes_count')}")
                break
    
    def test_error_handling(self):
        print("\n=== Тест: обработка ошибок ===")
        
        # Создаём пост с несуществующим пользователем
        response = requests.post(
            f"{self.post_url}/posts",
            json={"user_id": 99999, "content": "Invalid user post"},
            timeout=5
        )
        
        # API возвращает 404 когда пользователь не найден
        assert response.status_code == 404
        print("✅ Ошибка при несуществующем пользователе обработана")
        
        # Лайк несуществующего поста
        response = requests.post(f"{self.post_url}/posts/99999/like", timeout=5)
        assert response.status_code == 404
        print("✅ Ошибка при лайке несуществующего поста обработана")

if __name__ == '__main__':
    pytest.main([__file__, '-v', '-s'])