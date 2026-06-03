from flask import Flask, request, jsonify
import requests

app = Flask(__name__)

# Хранилище подписок
# Формат: { follower_id: [following_id1, following_id2, ...] }
subscriptions = {}

# Кэш ленты (чтобы не пересчитывать каждый раз)
feed_cache = {}

# URL других сервисов
POST_SERVICE_URL = "http://localhost:5002"
PROFILE_SERVICE_URL = "http://localhost:5001"

@app.route('/subscribe', methods=['POST'])
def subscribe():
    """Подписаться на пользователя"""
    data = request.get_json()
    
    if not data:
        return jsonify({"error": "No JSON data"}), 400
    
    follower_id = data.get('follower_id')
    following_id = data.get('following_id')
    
    if not follower_id or not following_id:
        return jsonify({"error": "follower_id and following_id required"}), 400
    
    if follower_id == following_id:
        return jsonify({"error": "Cannot subscribe to yourself"}), 400
    
    # Проверяем, что оба пользователя существуют
    try:
        resp1 = requests.get(f"{PROFILE_SERVICE_URL}/profile/check/{follower_id}")
        resp2 = requests.get(f"{PROFILE_SERVICE_URL}/profile/check/{following_id}")
        
        if not resp1.json().get('exists') or not resp2.json().get('exists'):
            return jsonify({"error": "User not found"}), 404
    except requests.exceptions.ConnectionError:
        return jsonify({"error": "Profile Service unavailable"}), 503
    
    # Создаём подписку
    if follower_id not in subscriptions:
        subscriptions[follower_id] = []
    
    if following_id not in subscriptions[follower_id]:
        subscriptions[follower_id].append(following_id)
    
    # Очищаем кэш ленты для этого пользователя
    if follower_id in feed_cache:
        del feed_cache[follower_id]
    
    return jsonify({
        "message": "Subscribed successfully",
        "follower_id": follower_id,
        "following": subscriptions[follower_id]
    }), 201

@app.route('/unsubscribe', methods=['POST'])
def unsubscribe():
    """Отписаться от пользователя"""
    data = request.get_json()
    
    follower_id = data.get('follower_id')
    following_id = data.get('following_id')
    
    if follower_id in subscriptions and following_id in subscriptions[follower_id]:
        subscriptions[follower_id].remove(following_id)
        if follower_id in feed_cache:
            del feed_cache[follower_id]
        return jsonify({"message": "Unsubscribed successfully"}), 200
    
    return jsonify({"error": "Subscription not found"}), 404

@app.route('/feed/<int:user_id>', methods=['GET'])
def get_feed(user_id):
    """Получить ленту новостей пользователя"""
    
    # Проверяем, существует ли пользователь
    try:
        resp = requests.get(f"{PROFILE_SERVICE_URL}/profile/check/{user_id}")
        if not resp.json().get('exists'):
            return jsonify({"error": f"User {user_id} not found"}), 404
    except requests.exceptions.ConnectionError:
        return jsonify({"error": "Profile Service unavailable"}), 503
    
    # Проверяем кэш
    if user_id in feed_cache:
        return jsonify({
            "user_id": user_id,
            "feed": feed_cache[user_id],
            "cached": True,
            "count": len(feed_cache[user_id])
        }), 200
    
    # Получаем список подписок
    following = subscriptions.get(user_id, [])
    
    if not following:
        return jsonify({
            "user_id": user_id,
            "feed": [],
            "cached": False,
            "message": "You are not following anyone"
        }), 200
    
    # Собираем посты от всех, на кого подписан
    feed_posts = []
    
    for followed_id in following:
        try:
            resp = requests.get(f"{POST_SERVICE_URL}/posts/user/{followed_id}")
            if resp.status_code == 200:
                user_posts = resp.json()
                # Добавляем имя автора к каждому посту
                author_resp = requests.get(f"{PROFILE_SERVICE_URL}/profile/{followed_id}")
                author_name = author_resp.json().get('username', 'unknown') if author_resp.status_code == 200 else 'unknown'
                
                for post in user_posts:
                    post['author_username'] = author_name
                feed_posts.extend(user_posts)
        except requests.exceptions.ConnectionError:
            print(f"Warning: Post Service unavailable for user {followed_id}")
            continue
    
    # Сортируем по дате (новые сверху)
    feed_posts.sort(key=lambda x: x['created_at'], reverse=True)
    
    # Сохраняем в кэш
    feed_cache[user_id] = feed_posts
    
    return jsonify({
        "user_id": user_id,
        "feed": feed_posts,
        "cached": False,
        "count": len(feed_posts)
    }), 200

@app.route('/subscriptions/<int:user_id>', methods=['GET'])
def get_subscriptions(user_id):
    """Получить список подписок пользователя"""
    following = subscriptions.get(user_id, [])
    return jsonify({
        "user_id": user_id,
        "following": following,
        "count": len(following)
    }), 200

if __name__ == '__main__':
    print("Feed Service запущен на http://localhost:5003")
    app.run(host='0.0.0.0', port=5003, debug=True) 
