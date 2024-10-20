from datetime import datetime, timedelta

class PostChecker:
    def __init__(self, client, target_handle):
        self.client = client
        self.target_handle = target_handle
        self.recent_post_uris = []

    def check_new_posts(self):
        params = {'actor': self.target_handle, 'limit': 5}  # 최신 5개의 포스트 확인
        user_feed = self.client.app.bsky.feed.get_author_feed(params=params)

        new_posts = []
        if user_feed.feed:
            for post in user_feed.feed:
                post_uri = post.post.uri
                post_time = datetime.fromisoformat(post.post.record['created_at'][:-1])  # 포스트 작성 시간
                current_time = datetime.utcnow()  # 현재 시간 (UTC 기준)
                if post_uri not in self.recent_post_uris and current_time - post_time <= timedelta(minutes=1):
                    new_posts.append(post)

        return new_posts

    def update_recent_posts(self, posts):
        new_uris = [post.post.uri for post in posts if hasattr(post, 'post')]
        self.recent_post_uris = (new_uris + self.recent_post_uris)[:5]
