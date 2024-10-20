import time
from atproto import Client
from atproto_client.models import AppBskyGraphGetFollows
from datetime import datetime, timedelta
from Log import log
from postChecker import PostChecker

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
            # 여기서 알림을 보낼 수 있음 (예: 이메일, Slack 등)

    # 새로운 포스트로 저장 목록 업데이트
    post_checker.update_recent_posts(new_posts)

    time.sleep(5)  # 5초마다 확인
