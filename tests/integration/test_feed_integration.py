import pytest
import requests
import time

class TestFeedIntegration:
    
    def setup_method(self):
        self.profile_url = "http://localhost:5001"
        self.post_url = "http://localhost:5002"
        self.feed_url = "http://localhost:5003"
        self.test_id = int(time.time())
    
    def create_test_user(self, username, email):
        response = requests.post(
            f"{self.profile_url}/profile",
            json={"username": username, "email": email, "bio": "Test user"},
            timeout=5
        )
        if response.status_code == 201:
            return response.json().get("id")
        return None
    
    def test_subscription_and_feed(self):
        print("\n=== Тест: подписка и лента ===")
        
        # Создаём пользователей
        user1 = self.create_test_user(f"feed_user1_{self.test_id}", f"feed1_{self.test_id}@test.com")
        user2 = self.create_test_user(f"feed_user2_{self.test_id}", f"feed2_{self.test_id}@test.com")
        
        if not user1 or not user2:
            pytest.skip("Не удалось создать тестовых пользователей")
        
        print(f"✅ Пользователи: {user1}, {user2}")
        
        # Создаём пост от user2
        response = requests.post(
            f"{self.post_url}/posts",
            json={"user_id": user2, "content": f"Post for feed test {self.test_id}"},
            timeout=5
        )
        
        if response.status_code == 201:
            print(f"✅ Пост создан от user {user2}")
        
        # Подписываем user1 на user2
        response = requests.post(
            f"{self.feed_url}/subscribe",
            json={"follower_id": user1, "following_id": user2},
            timeout=5
        )
        
        assert response.status_code in [200, 201]
        print(f"✅ Подписка: {user1} -> {user2}")
        
        # Проверяем ленту user1
        response = requests.get(f"{self.feed_url}/feed/{user1}", timeout=5)
        assert response.status_code == 200
        print("✅ Лента получена")
    
    def test_subscribe_to_self(self):
        print("\n=== Тест: подписка на себя ===")
        
        user = self.create_test_user(f"self_user_{self.test_id}", f"self_{self.test_id}@test.com")
        if not user:
            pytest.skip("Не удалось создать пользователя")
        
        response = requests.post(
            f"{self.feed_url}/subscribe",
            json={"follower_id": user, "following_id": user},
            timeout=5
        )
        
        assert response.status_code == 400
        print("✅ Попытка подписаться на себя отклонена")
    
    def test_subscribe_to_nonexistent_user(self):
        print("\n=== Тест: подписка на несуществующего пользователя ===")
        
        user = self.create_test_user(f"nonexistent_user_{self.test_id}", f"nonexistent_{self.test_id}@test.com")
        if not user:
            pytest.skip("Не удалось создать пользователя")
        
        response = requests.post(
            f"{self.feed_url}/subscribe",
            json={"follower_id": user, "following_id": 99999},
            timeout=5
        )
        
        assert response.status_code in [400, 404]
        print("✅ Подписка на несуществующего пользователя отклонена")

if __name__ == '__main__':
    pytest.main([__file__, '-v', '-s'])