from flask import Flask, request, jsonify

app = Flask(__name__)

# База данных в памяти (простая имитация БД)
profiles = {
    1: {"id": 1, "username": "alice", "avatar": "alice.jpg", "bio": "Hello! I like cats"},
    2: {"id": 2, "username": "bob", "avatar": "bob.jpg", "bio": "World! I like dogs"},
    3: {"id": 3, "username": "charlie", "avatar": "charlie.jpg", "bio": "Just chilling"}
}

@app.route('/profile/<int:user_id>', methods=['GET'])
def get_profile(user_id):
    """Получить профиль пользователя по ID"""
    if user_id in profiles:
        return jsonify(profiles[user_id]), 200
    return jsonify({"error": "User not found"}), 404

@app.route('/profile/<int:user_id>', methods=['PUT'])
def update_profile(user_id):
    """Обновить данные профиля"""
    if user_id not in profiles:
        return jsonify({"error": "User not found"}), 404
    
    data = request.get_json()
    profile = profiles[user_id]
    
    if 'bio' in data:
        profile['bio'] = data['bio']
    if 'avatar' in data:
        profile['avatar'] = data['avatar']
    
    return jsonify(profile), 200

@app.route('/profiles', methods=['GET'])
def list_profiles():
    """Получить список всех профилей"""
    return jsonify(list(profiles.values())), 200

@app.route('/profile/check/<int:user_id>', methods=['GET'])
def check_user_exists(user_id):
    """Проверить, существует ли пользователь (для других сервисов)"""
    exists = user_id in profiles
    return jsonify({"exists": exists, "user_id": user_id}), 200

if __name__ == '__main__':
    print("Profile Service запущен на http://localhost:5001")
    app.run(host='0.0.0.0', port=5001, debug=True) 
