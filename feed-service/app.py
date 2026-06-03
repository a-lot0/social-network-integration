from flask import Flask, jsonify, request
import requests

app = Flask(__name__)

subscriptions = {}
PROFILE_URL = "http://profile-service:5001"
POST_URL = "http://post-service:5002"


@app.route("/subscribe", methods=["POST"])
def subscribe():
    data = request.get_json()
    follower = data.get("follower_id")
    following = data.get("following_id")
    if follower == following:
        return jsonify({"error": "Cannot subscribe to self"}), 400
    if follower not in subscriptions:
        subscriptions[follower] = []
    if following not in subscriptions[follower]:
        subscriptions[follower].append(following)
    return jsonify({"message": "Subscribed", "following": subscriptions[follower]}), 201


@app.route("/feed/<int:user_id>", methods=["GET"])
def get_feed(user_id):
    following = subscriptions.get(user_id, [])
    feed_posts = []
    for followed in following:
        try:
            resp = requests.get(f"{POST_URL}/posts/user/{followed}")
            if resp.status_code == 200:
                feed_posts.extend(resp.json())
        except requests.exceptions.ConnectionError:
            pass
    feed_posts.sort(key=lambda x: x["created_at"], reverse=True)
    return (
        jsonify({"user_id": user_id, "feed": feed_posts, "count": len(feed_posts)}),
        200,
    )


@app.route("/subscriptions/<int:user_id>", methods=["GET"])
def get_subscriptions(user_id):
    return (
        jsonify({"user_id": user_id, "following": subscriptions.get(user_id, [])}),
        200,
    )


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5003, debug=True)
