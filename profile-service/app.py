from flask import Flask, jsonify

app = Flask(__name__)

profiles = {
    1: {"id": 1, "username": "alice", "bio": "Hello!"},
    2: {"id": 2, "username": "bob", "bio": "World!"},
    3: {"id": 3, "username": "charlie", "bio": "Hi!"},
}


@app.route("/profile/<int:user_id>", methods=["GET"])
def get_profile(user_id):
    if user_id in profiles:
        return jsonify(profiles[user_id]), 200
    return jsonify({"error": "User not found"}), 404


@app.route("/profiles", methods=["GET"])
def list_profiles():
    return jsonify(list(profiles.values())), 200


@app.route("/profile/check/<int:user_id>", methods=["GET"])
def check_user(user_id):
    return jsonify({"exists": user_id in profiles}), 200


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5001, debug=True)
