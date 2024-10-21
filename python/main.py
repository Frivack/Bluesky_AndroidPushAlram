import time

import requests
import json
from atproto import Client
from atproto_client.models import AppBskyGraphGetFollows
from google.oauth2 import service_account
import google.auth.transport.requests
from datetime import datetime, timedelta
from Log import log
from postChecker import PostChecker

# 서비스 계정 키 파일 경로
SERVICE_ACCOUNT_FILE = 'bluesky-pushnotification-af356351067b.json'

# Scope 추가
SCOPES = ["https://www.googleapis.com/auth/firebase.messaging"]

# 서비스 계정으로 자격 증명 객체 생성 (Scope 추가)
credentials = service_account.Credentials.from_service_account_file(SERVICE_ACCOUNT_FILE, scopes=SCOPES)

# OAuth 인증 요청 객체 생성 및 갱신
auth_req = google.auth.transport.requests.Request()
credentials.refresh(auth_req)
token = credentials.token

# 요청 헤더 설정
headers = {
    'Authorization': f'Bearer {token}',
    'Content-Type': 'application/json',
}

# Firebase Cloud Messaging v1 URL
fcm_url = 'https://fcm.googleapis.com/v1/projects/bluesky-pushnotification/messages:send'

flask_url = 'http://127.0.0.1:5000/tokens'  # Flask 서버에서 토큰 가져오기

log.log_able = True

input("Press any key to start")

print("로그인 중...")
client = Client()
user_id = input("핸들 입력 (예 handle.bsky.social): ")
user_pw = input("비밀번호 입력: ")
profile = client.login(user_id, user_pw)
print("로그인 완료")
print('welcome', profile.display_name)


# 임시로 팔로우 검색하지 않고 고정
target_handle = 'frivack.bsky.social'
params = AppBskyGraphGetFollows.Params(actor=profile.handle)
follow = client.app.bsky.graph.get_follows(params=params)
#print(follow)

target_follow = next((f for f in follow.follows if f.handle == target_handle), None)


post_checker = PostChecker(client, target_handle)


if target_follow:
    log.message(f"Found: {target_follow.handle}")
else:
    log.message("User not found.", "ERROR")
    exit()


# 주기적으로 새로운 포스트 확인
while True:
    new_posts = post_checker.check_new_posts()

    if new_posts:
        for post in new_posts:
            log.message(f"New post by {post.post.author.handle}: {post.post.record['text']}")

            # Flask 서버에서 등록된 토큰 가져오기
            response = requests.get(flask_url)
            if response.status_code == 200:
                tokens = response.json().get('tokens', [])
                for device_token in tokens:
                    # FCM 푸시 알림 보내기
                    payload = {
                        "message": {
                            "token": device_token,
                            "notification": {
                                "title": "New Post Alert!",
                                "body": f"New post by {post.post.author.handle}: {post.post.record['text']}"
                            }
                        }
                    }
                    response = requests.post(fcm_url, headers=headers, data=json.dumps(payload))
                    if response.status_code == 200:
                        print("Push notification sent successfully.")
                    else:
                        print("Failed to send push notification:", response.status_code, response.text)

    # 새로운 포스트로 저장 목록 업데이트
    post_checker.update_recent_posts(new_posts)

    time.sleep(5)  # 5초마다 확인
