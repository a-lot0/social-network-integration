from flask import Flask, jsonify, request
from flask_cors import CORS
from sqlalchemy import create_engine, Column, Integer, DateTime
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from datetime import datetime
import os
import requests
from loguru import logger
import sys
from time import sleep

# Настройка логирования
logger.remove()
logger.add(sys.stdout, format="{time:HH:mm:ss} | {level} | {message}", level="INFO")
logger.add("logs/feed_service.log", rotation="1 day", compression="zip", level="DEBUG")
logger.add("logs/errors.log", level="ERROR", rotation="1 week")

app = Flask(__name__)
CORS(app)

DATABASE_URL = os.getenv('DATABASE_URL', 'postgresql://postgres:mysecretpassword@localhost:5432/social_network')
engine = create_engine(DATABASE_URL)
Base = declarative_base()
SessionLocal = sessionmaker(bind=engine)

class Subscription(Base):
    __tablename__ = 'subscriptions'
    id = Column(Integer, primary_key=True, autoincrement=True)
    follower_id = Column(Integer, nullable=False)
    following_id = Column(Integer, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)

Base.metadata.create_all(engine)

PROFILE_URL = os.getenv('PROFILE_SERVICE_URL', 'http://localhost:5001')
POST_URL = os.getenv('POST_SERVICE_URL', 'http://localhost:5002')

def call_with_retry(url, max_retries=3, delay=1):
    for attempt in range(max_retries):
        try:
            response = requests.get(url, timeout=5)
            if response.status_code == 200:
                return response
        except Exception as e:
            logger.error(f"Попытка {attempt + 1} не удалась: {str(e)}")
        
        if attempt < max_retries - 1:
            wait_time = delay * (2 ** attempt)
            sleep(wait_time)
    return None

@app.route('/subscribe', methods=['POST'])
def subscribe():
    data = request.get_json()
    follower_id = data.get('follower_id')
    following_id = data.get('following_id')
    
    logger.info(f"=== ПОДПИСКА ===")
    logger.info(f"Пользователь {follower_id} подписывается на {following_id}")
    
    if not follower_id or not following_id:
        logger.warning("Отсутствуют follower_id или following_id")
        return jsonify({"error": "follower_id and following_id required"}), 400
    
    if follower_id == following_id:
        logger.warning("Попытка подписаться на себя")
        return jsonify({"error": "Cannot subscribe to yourself"}), 400
    
    # Проверка существования пользователей с Retry
    resp1 = call_with_retry(f"{PROFILE_URL}/profile/check/{follower_id}")
    resp2 = call_with_retry(f"{PROFILE_URL}/profile/check/{following_id}")
    
    if not resp1 or not resp2:
        logger.error("Сервис профилей недоступен")
        return jsonify({"error": "Profile service unavailable"}), 503
    
    if not resp1.json().get('exists') or not resp2.json().get('exists'):
        logger.warning(f"Пользователь не найден: follower={follower_id}, following={following_id}")
        return jsonify({"error": "User not found"}), 404
    
    try:
        session = SessionLocal()
        existing = session.query(Subscription).filter(
            Subscription.follower_id == follower_id,
            Subscription.following_id == following_id
        ).first()
        
        if existing:
            session.close()
            logger.info(f"Подписка уже существует: {follower_id} -> {following_id}")
            return jsonify({"message": "Already subscribed"}), 200
        
        sub = Subscription(follower_id=follower_id, following_id=following_id)
        session.add(sub)
        session.commit()
        session.close()
        
        logger.success(f"Подписка успешна: {follower_id} -> {following_id}")
        return jsonify({"message": "Subscribed successfully"}), 201
    except Exception as e:
        logger.error(f"Ошибка сохранения подписки: {str(e)}")
        return jsonify({"error": str(e)}), 500

@app.route('/subscribers/<int:user_id>', methods=['GET'])
def get_subscribers(user_id):
    logger.debug(f"Запрос подписчиков пользователя {user_id}")
    try:
        session = SessionLocal()
        subscribers = session.query(Subscription).filter(Subscription.following_id == user_id).all()
        session.close()
        subscriber_ids = [s.follower_id for s in subscribers]
        logger.debug(f"У пользователя {user_id} {len(subscriber_ids)} подписчиков")
        return jsonify({"user_id": user_id, "subscribers": subscriber_ids}), 200
    except Exception as e:
        logger.error(f"Ошибка получения подписчиков: {str(e)}")
        return jsonify({"error": str(e)}), 500

@app.route('/following/<int:user_id>', methods=['GET'])
def get_following(user_id):
    logger.debug(f"Запрос подписок пользователя {user_id}")
    try:
        session = SessionLocal()
        following = session.query(Subscription).filter(Subscription.follower_id == user_id).all()
        session.close()
        following_ids = [s.following_id for s in following]
        logger.debug(f"Пользователь {user_id} подписан на {len(following_ids)} человек")
        return jsonify({"user_id": user_id, "following": following_ids}), 200
    except Exception as e:
        logger.error(f"Ошибка получения подписок: {str(e)}")
        return jsonify({"error": str(e)}), 500

@app.route('/feed/<int:user_id>', methods=['GET'])
def get_feed(user_id):
    logger.info(f"=== ЗАПРОС ЛЕНТЫ ===")
    logger.info(f"Пользователь: {user_id}")
    
    # Проверка существования пользователя
    resp = call_with_retry(f"{PROFILE_URL}/profile/check/{user_id}")
    if not resp or not resp.json().get('exists'):
        logger.error(f"Пользователь {user_id} не найден")
        return jsonify({"error": "User not found"}), 404
    
    try:
        session = SessionLocal()
        subscriptions = session.query(Subscription).filter(Subscription.follower_id == user_id).all()
        following_ids = [s.following_id for s in subscriptions]
        session.close()
        
        if not following_ids:
            logger.info(f"У пользователя {user_id} нет подписок")
            return jsonify({"user_id": user_id, "feed": [], "message": "No subscriptions"}), 200
        
        logger.debug(f"Подписки пользователя {user_id}: {following_ids}")
        
        feed_posts = []
        for followed_id in following_ids:
            resp = call_with_retry(f"{POST_URL}/posts/user/{followed_id}")
            if resp and resp.status_code == 200:
                posts = resp.json()
                author_resp = call_with_retry(f"{PROFILE_URL}/profile/{followed_id}")
                author_name = author_resp.json().get('username', 'unknown') if author_resp else 'unknown'
                for post in posts:
                    post['author_username'] = author_name
                feed_posts.extend(posts)
        
        feed_posts.sort(key=lambda x: x.get('created_at', ''), reverse=True)
        logger.success(f"Лента пользователя {user_id}: {len(feed_posts)} постов")
        return jsonify({"user_id": user_id, "feed": feed_posts, "count": len(feed_posts)}), 200
    except Exception as e:
        logger.error(f"Ошибка получения ленты: {str(e)}")
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    logger.info("=== Feed Service запущен на порту 5003 ===")
    app.run(host='0.0.0.0', port=5003, debug=True)