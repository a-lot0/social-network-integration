import pytest
import requests
import time
import json

class TestFullScenario:
    """E2E тесты полных сценариев пользователя"""
    
    def setup_method(self):
        self.profile_url = "http://localhost:5001"
        self.post_url = "http://localhost:5002"
        self.feed_url = "http://localhost:5003"
        
        # Уникальные имена для тестовых данных
        self.test_id = int(time.time())
        self.user_alice = {
            "username": f"alice_{self.test_id}",
            "email": f"alice_{self.test_id}@test.com",
            "bio": "Alice bio"
        }
        self.user_bob = {
            "username": f"bob_{self.test_id}",
            "email": f"bob_{self.test_id}@test.com",
            "bio": "Bob bio"
        }
    
    def wait_for_services(self):
        """Ожидание готовности всех сервисов"""
        services = [
            (self.profile_url, "Profile"),
            (self.post_url, "Post"),
            (self.feed_url, "Feed")
        ]
        
        for url, name in services:
            for i in range(10):
                try:
                    resp = requests.get(f"{url}/profiles", timeout=2)
                    if resp.status_code == 200:
                        print(f"✅ {name} Service готов")
                        break
                except:
                    pass
                time.sleep(2)
            else:
                pytest.skip(f"{name} Service не запущен")
    
    def create_user(self, user_data):
        """Создание пользователя"""
        response = requests.post(
            f"{self.profile_url}/profile",
            json=user_data
        )
        assert response.status_code == 201
        return response.json()["id"]
    
    def create_post(self, user_id, content):
        """Создание поста"""
        response = requests.post(
            f"{self.post_url}/posts",
            json={"user_id": user_id, "content": content}
        )
        assert response.status_code == 201
        return response.json()["id"]
    
    def subscribe(self, follower_id, following_id):
        """Подписка"""
        response = requests.post(
            f"{self.feed_url}/subscribe",
            json={"follower_id": follower_id, "following_id": following_id}
        )
        return response.status_code
    
    def get_feed(self, user_id):
        """Получение ленты"""
        response = requests.get(f"{self.feed_url}/feed/{user_id}")
        assert response.status_code == 200
        return response.json()
    
    def test_e2e_full_cycle(self):
        """
        Полный E2E сценарий:
        1. Создание пользователя Alice
        2. Создание пользователя Bob
        3. Bob подписывается на Alice
        4. Alice создаёт пост
        5. Проверяем, что пост появился в ленте Bob
        """
        
        self.wait_for_services()
        
        # Шаг 1: Создаём Alice
        print("\n=== ШАГ 1: Создание пользователя Alice ===")
        alice_id = self.create_user(self.user_alice)
        print(f"✅ Alice создана: ID={alice_id}")
        
        # Шаг 2: Создаём Bob
        print("\n=== ШАГ 2: Создание пользователя Bob ===")
        bob_id = self.create_user(self.user_bob)
        print(f"✅ Bob создан: ID={bob_id}")
        
        # Шаг 3: Bob подписывается на Alice
        print("\n=== ШАГ 3: Bob подписывается на Alice ===")
        result = self.subscribe(bob_id, alice_id)
        assert result == 201
        print(f"✅ Подписка: Bob({bob_id}) -> Alice({alice_id})")
        
        # Шаг 4: Alice создаёт пост
        print("\n=== ШАГ 4: Alice создаёт пост ===")
        post_content = f"Hello from Alice! (test #{self.test_id})"
        post_id = self.create_post(alice_id, post_content)
        print(f"✅ Пост создан: ID={post_id}, content='{post_content}'")
        
        # Шаг 5: Проверяем ленту Bob
        print("\n=== ШАГ 5: Проверка ленты Bob ===")
        feed = self.get_feed(bob_id)
        
        # Ждём, пока пост появится в ленте (асинхронное обновление)
        max_wait = 10
        for i in range(max_wait):
            feed = self.get_feed(bob_id)
            if feed.get('count', 0) > 0:
                break
            time.sleep(1)
        
        assert feed.get('count', 0) > 0, "В ленте Bob нет постов"
        
        # Проверяем, что нужный пост есть в ленте
        posts_in_feed = feed.get('feed', [])
        found = any(p.get('id') == post_id for p in posts_in_feed)
        
        if found:
            print(f"✅ Пост {post_id} найден в ленте Bob!")
        else:
            print(f"⚠️ Пост {post_id} не найден в ленте. Содержимое ленты: {posts_in_feed}")
        
        assert found, f"Пост {post_id} должен быть в ленте Bob"
        
        print("\n" + "="*50)
        print("🎉 E2E ТЕСТ УСПЕШНО ЗАВЕРШЁН! 🎉")
        print("="*50)
        
        # Вывод результатов
        print(f"\n📊 РЕЗУЛЬТАТЫ:")
        print(f"   - Пользователи: Alice(ID={alice_id}), Bob(ID={bob_id})")
        print(f"   - Подписка: {bob_id} -> {alice_id}")
        print(f"   - Пост: ID={post_id}")
        print(f"   - Лента Bob содержит {feed.get('count')} постов")
    
    def test_e2e_like_flow(self):
        """
        E2E сценарий лайков:
        1. Создание пользователя
        2. Создание поста
        3. Лайк поста
        4. Проверка счётчика лайков
        """
        
        self.wait_for_services()
        
        print("\n=== E2E ТЕСТ ЛАЙКОВ ===")
        
        # Создаём пользователя
        user_id = self.create_user({
            "username": f"liker_{self.test_id}",
            "email": f"liker_{self.test_id}@test.com",
            "bio": "Liker"
        })
        print(f"✅ Пользователь создан: ID={user_id}")
        
        # Создаём пост
        post_id = self.create_post(user_id, "Post for likes!")
        print(f"✅ Пост создан: ID={post_id}")
        
        # Ставим лайк
        response = requests.post(f"{self.post_url}/posts/{post_id}/like")
        assert response.status_code == 200
        likes = response.json().get("likes", 0)
        print(f"✅ Лайк поставлен. Всего лайков: {likes}")
        
        # Проверяем, что лайк сохранился
        response = requests.get(f"{self.post_url}/posts/user/{user_id}")
        posts = response.json()
        assert posts[0]["likes_count"] == 1
        print("✅ Счётчик лайков обновлён")
        
        print("\n🎉 ТЕСТ ЛАЙКОВ УСПЕШНО ЗАВЕРШЁН!")

if __name__ == '__main__':
    pytest.main([__file__, '-v', '-s'])