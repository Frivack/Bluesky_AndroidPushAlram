import time
from atproto import Client
from atproto_client.models import AppBskyGraphGetFollows
from datetime import datetime, timedelta

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
print(follow)

target_follow = next((f for f in follow.follows if f.handle == target_handle), None)

#if target_follow:
#    print(f"Found: {target_follow.handle}")
#else:
#    print("User not found.")
#    exit()

# 최근 5개의 포스트 URI 저장 리스트
recent_post_uris = []

def check_new_posts(client, target_did):
    params = {'actor': target_did, 'limit': 5}  # 최신 5개의 포스트 확인
    user_feed = client.app.bsky.feed.get_author_feed(params=params)

    new_posts = []
    if user_feed.feed:
        for post in user_feed.feed:
            post_uri = post.post.uri
            # 1분 이내의 최신 포스트만 확인
            post_time = datetime.fromisoformat(post.post.record['created_at'][:-1])  # 포스트 작성 시간
            current_time = datetime.utcnow()  # 현재 시간 (UTC 기준)
            if post_uri not in recent_post_uris and current_time - post_time <= timedelta(minutes=1):
                new_posts.append(post)

    return new_posts


def update_recent_posts(posts):
    global recent_post_uris
    # 새로운 포스트에서 uri만 추출하여 저장
    new_uris = [post.post.uri for post in posts if hasattr(post, 'post')]
    # 기존 recent_post_uris에 새로운 포스트 추가, 중복 없이 최대 5개 유지
    recent_post_uris = (new_uris + recent_post_uris)[:5]

# 주기적으로 새로운 포스트 확인
while True:
    new_posts = check_new_posts(client, target_follow.did)

    if new_posts:
        for post in new_posts:
            print(f"New post by {post.post.author.handle}: {post.post.record['text']}")
            # 여기서 알림을 보낼 수 있음 (예: 이메일, Slack, 메시지 등)

    # 새로운 포스트로 저장 목록 업데이트
    update_recent_posts(new_posts)

    time.sleep(1)  # 1초마다 확인
