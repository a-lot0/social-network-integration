from flask import Flask, jsonify, request
from datetime import datetime
import requests

app = Flask(__name__)

posts = []
next_id = 1
PROFILE_URL = "http://profile-service:5001"


@app.route("/posts", methods=["POST"])
def create_post():
    global next_id
    data = request.get_json()
    user_id = data.get("user_id")
    content = data.get("content")
    if not user_id or not content:
        return jsonify({"error": "user_id and content required"}), 400
    try:
        resp = requests.get(f"{PROFILE_URL}/profile/check/{user_id}")
        if not resp.json().get("exists"):
            return jsonify({"error": "User not found"}), 404
    except requests.exceptions.ConnectionError:
        return jsonify({"error": "Profile service unavailable"}), 503
    post = {
        "id": next_id,
        "user_id": user_id,
        "content": content[:280],
        "likes_count": 0,
        "created_at": datetime.now().isoformat(),
    }
    posts.append(post)
    next_id += 1
    return jsonify(post), 201


@app.route("/posts", methods=["GET"])
def get_posts():
    return jsonify(posts), 200


@app.route("/posts/user/<int:user_id>", methods=["GET"])
def get_user_posts(user_id):
    user_posts = [p for p in posts if p["user_id"] == user_id]
    return jsonify(user_posts), 200


@app.route("/posts/<int:post_id>/like", methods=["POST"])
def like_post(post_id):
    for post in posts:
        if post["id"] == post_id:
            post["likes_count"] += 1
            return jsonify({"likes": post["likes_count"]}), 200
    return jsonify({"error": "Post not found"}), 404


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5002, debug=True)
