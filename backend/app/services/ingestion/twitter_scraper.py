# backend/app/services/ingestion/twitter_scraper.py
from __future__ import annotations

from dataclasses import dataclass, asdict
from datetime import datetime, timezone
from typing import List, Optional

import snscrape.modules.twitter as sntwitter


@dataclass
class TweetItem:
    id: int
    url: str
    date: str
    username: str
    displayname: str
    content: str
    likeCount: int
    retweetCount: int
    replyCount: int
    quoteCount: int
    lang: Optional[str]


def _to_iso(dt: datetime) -> str:
    if dt.tzinfo is None:
        dt = dt.replace(tzinfo=timezone.utc)
    return dt.astimezone(timezone.utc).isoformat()


def fetch_tweets(query: str, limit: int = 50) -> List[TweetItem]:
    """
    Fetch tweets using snscrape.
    query examples:
      - "#somehashtag lang:tr"
      - "from:someuser"
      - "url:example.com"
      - "\"exact phrase\" since:2025-01-01 until:2025-01-07"
    """
    if not query or not query.strip():
        raise ValueError("query cannot be empty")
    if limit < 1 or limit > 2000:
        raise ValueError("limit must be between 1 and 2000")

    scraper = sntwitter.TwitterSearchScraper(query)
    out: List[TweetItem] = []

    for i, tweet in enumerate(scraper.get_items()):
        if i >= limit:
            break

        user = tweet.user
        out.append(
            TweetItem(
                id=int(tweet.id),
                url=str(tweet.url),
                date=_to_iso(tweet.date),
                username=str(user.username) if user else "",
                displayname=str(user.displayname) if user else "",
                content=str(tweet.rawContent or ""),
                likeCount=int(tweet.likeCount or 0),
                retweetCount=int(tweet.retweetCount or 0),
                replyCount=int(tweet.replyCount or 0),
                quoteCount=int(tweet.quoteCount or 0),
                lang=getattr(tweet, "lang", None),
            )
        )

    return out


def fetch_tweets_dict(query: str, limit: int = 50) -> List[dict]:
    return [asdict(x) for x in fetch_tweets(query, limit)]