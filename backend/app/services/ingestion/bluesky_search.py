# backend/app/services/ingestion/bluesky_search.py
from __future__ import annotations

import os
from dataclasses import dataclass, asdict
from typing import List

from dotenv import load_dotenv
from atproto import Client

load_dotenv()  # backend/.env içindeki değişkenleri yükler


@dataclass
class PostItem:
    id: str
    url: str
    date: str
    username: str
    displayname: str
    content: str
    likeCount: int
    repostCount: int


def fetch_posts(query: str, limit: int = 50) -> List[PostItem]:
    if not query or not query.strip():
        raise ValueError("query cannot be empty")
    if limit < 1 or limit > 2000:
        raise ValueError("limit must be between 1 and 2000")

    handle = os.getenv("BSKY_HANDLE")
    app_password = os.getenv("BSKY_APP_PASSWORD")
    if not handle or not app_password:
        raise RuntimeError(
            "Missing env vars. Please set BSKY_HANDLE and BSKY_APP_PASSWORD in backend/.env"
        )

    client = Client()
    client.login(handle, app_password)

    response = client.app.bsky.feed.search_posts(params={"q": query, "limit": limit})

    out: List[PostItem] = []
    for post in response.posts:
        # Bluesky post URL formatı
        post_id = post.uri.split("/")[-1]
        post_url = f"https://bsky.app/profile/{post.author.handle}/post/{post_id}"

        out.append(
            PostItem(
                id=post.uri,
                url=post_url,
                date=str(getattr(post, "indexed_at", "")),
                username=post.author.handle,
                displayname=getattr(post.author, "display_name", None) or post.author.handle,
                content=getattr(post.record, "text", "") or "",
                likeCount=int(getattr(post, "like_count", 0) or 0),
                repostCount=int(getattr(post, "repost_count", 0) or 0),
            )
        )

    return out


def fetch_posts_dict(query: str, limit: int = 50) -> List[dict]:
    return [asdict(x) for x in fetch_posts(query, limit)]


if __name__ == "__main__":
    print("Bluesky'dan veriler çekiliyor...")
    try:
        results = fetch_posts_dict("teknoloji", limit=5)
        if not results:
            print("Hiç post bulunamadı.")
        for idx, post in enumerate(results, 1):
            preview = post["content"].replace("\n", " ")[:80]
            print(f"{idx}. [{post['username']}]: {preview}...")
    except Exception as e:
        print(f"Hata: {e}")
