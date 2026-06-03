from flask import Flask, request, jsonify
from datetime import datetime
import requests

app = Flask(__name__)

# База данных постов
posts = []
next_id = 1

# URL Profile Service (для проверки авторов)
PROFILE_SERVICE_URL = "http://localhost:5001"

@app.route('/posts', methods=['POST'])
def create_post():
    """Создать новый пост"""
    global next_id
    data = request.get_json()
    
    # Проверка обязательных полей
    if not data:
        return jsonify({"error": "No JSON data provided"}), 400
    
    user_id = data.get('user_id')
    content = data.get('content')
    
    if not user_id:
        return jsonify({"error": "user_id is required"}), 400
    if not content:
        return jsonify({"error": "content is required"}), 400
    if len(content) > 280:
        return jsonify({"error": "Content too long (max 280 chars)"}), 400
    
    # Проверка, существует ли пользователь
    try:
        resp = requests.get(f"{PROFILE_SERVICE_URL}/profile/check/{user_id}")
        if resp.status_code != 200 or not resp.json().get('exists'):
            return jsonify({"error": f"User {user_id} not found"}), 404
    except requests.exceptions.ConnectionError:
        return jsonify({"error": "Profile Service unavailable"}), 503
    
    # Создание поста
    post = {
        "id": next_id,
        "user_id": user_id,
        "content": content,
        "image_url": data.get('image_url'),
        "likes_count": 0,
        "comments_count": 0,
        "created_at": datetime.now().isoformat()
    }
    posts.append(post)
    next_id += 1
    
    return jsonify(post), 201

@app.route('/posts/<int:post_id>', methods=['GET'])
def get_post(post_id):
    """Получить пост по ID"""
    for post in posts:
        if post['id'] == post_id:
            return jsonify(post), 200
    return jsonify({"error": "Post not found"}), 404

@app.route('/posts/user/<int:user_id>', methods=['GET'])
def get_user_posts(user_id):
    """Получить все посты пользователя"""
    user_posts = [p for p in posts if p['user_id'] == user_id]
    # Сортируем от новых к старым
    user_posts.sort(key=lambda x: x['created_at'], reverse=True)
    return jsonify(user_posts), 200

@app.route('/posts/<int:post_id>/like', methods=['POST'])
def like_post(post_id):
    """Лайкнуть пост"""
    for post in posts:
        if post['id'] == post_id:
            post['likes_count'] += 1
            return jsonify({
                "post_id": post_id,
                "likes_count": post['likes_count']
            }), 200
    return jsonify({"error": "Post not found"}), 404

@app.route('/posts', methods=['GET'])
def get_all_posts():
    """Получить все посты (для отладки)"""
    limit = request.args.get('limit', default=50, type=int)
    return jsonify(posts[-limit:]), 200

if __name__ == '__main__':
    print("Post Service запущен на http://localhost:5002")
    app.run(host='0.0.0.0', port=5002, debug=True) 
