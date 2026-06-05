import pytest
import requests
import time

def is_service_ready(url, max_retries=15, delay=2):
    """Проверка, что сервис готов к работе"""
    for i in range(max_retries):
        try:
            # Пробуем разные эндпоинты для проверки
            endpoints = ["/profiles", "/posts", "/feed/1"]
            for endpoint in endpoints:
                try:
                    response = requests.get(f"{url}{endpoint}", timeout=3)
                    if response.status_code in [200, 404]:
                        print(f"✅ {url} готов (ответ {response.status_code})")
                        return True
                except:
                    pass
        except requests.exceptions.ConnectionError:
            print(f"⏳ Ожидание {url}... попытка {i+1}/{max_retries}")
        except Exception as e:
            print(f"⚠️ Ошибка при проверке {url}: {e}")
        time.sleep(delay)
    print(f"❌ {url} не отвечает после {max_retries} попыток")
    return False

@pytest.fixture(scope="session")
def services_ready():
    """Фикстура для проверки готовности сервисов"""
    services = {
        "Profile Service": "http://localhost:5001",
        "Post Service": "http://localhost:5002",
        "Feed Service": "http://localhost:5003"
    }
    
    ready = True
    for name, url in services.items():
        if not is_service_ready(url):
            print(f"\n❌ {name} не запущен на {url}")
            ready = False
    
    if not ready:
        pytest.skip("Сервисы не запущены. Запустите все 3 сервиса в разных терминалах")
    
    return ready