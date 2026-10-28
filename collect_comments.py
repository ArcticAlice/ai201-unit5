#!/usr/bin/env python3
"""
Reddit Comment Collector for CodePath AI201 Unit 5 (TakeMeter).

Collects 200 comments from the specified Reddit thread:
https://www.reddit.com/r/degoogle/comments/1x8d0u2/i_think_this_is_a_wakeup_call_for_anyone_still_on/?sort=controversial

Rules & Guardrails:
- Prioritizes top-level comments.
- If the thread contains fewer than 200 top-level comments, includes direct replies
  with the constraint: strictly NEVER more than 1 reply for any specific comment.
- Excludes [deleted], [removed], empty, or bot comments.
- Preserves complete, untruncated post/comment text.
- Generates RFC 4180-compliant labels.csv (text,label,note) in unit5 directory.
"""

import csv
import os
import re
import sys
import time
import urllib.parse
import urllib.request
from html.parser import HTMLParser
from typing import Dict, List, Set, Tuple

DEFAULT_URL = "https://www.reddit.com/r/degoogle/comments/1x8d0u2/i_think_this_is_a_wakeup_call_for_anyone_still_on/?sort=controversial"
TARGET_OUTPUT = "/Users/jawadbhullar/documents/codepath/ai201/unit5/labels.csv"
REDLIB_HOST = "https://redlib.reallyaweso.me"


class RedlibThreadParser(HTMLParser):
    def __init__(self):
        super().__init__()
        self.quote_depth = 0
        self.in_comment_body = False
        self.current_top_id = None
        self.current_comment_id = None
        self.current_comment_depth = 0
        self.current_author = ""
        self.in_author = False
        self.current_text = []

        # Collected results
        # top_comments: dict of cid -> {text, author}
        self.top_comments: Dict[str, Dict[str, str]] = {}
        # direct_replies: dict of top_cid -> list of {id, text, author}
        self.direct_replies: Dict[str, List[Dict[str, str]]] = {}
        # Pagination links for depth 0
        self.more_top_links: List[str] = []

    def handle_starttag(self, tag, attrs):
        attr_dict = dict(attrs)

        if tag == "blockquote" and "replies" in attr_dict.get("class", ""):
            self.quote_depth += 1

        elif tag == "div" and attr_dict.get("class") == "comment":
            cid = attr_dict.get("data-comment-id")
            self.current_comment_id = cid
            self.current_comment_depth = self.quote_depth
            if self.quote_depth == 0:
                self.current_top_id = cid

        elif tag == "a" and "comment_author" in attr_dict.get("class", ""):
            self.in_author = True
            self.current_author = ""

        elif tag == "div" and "comment_body" in attr_dict.get("class", ""):
            self.in_comment_body = True
            self.current_text = []

        elif tag == "a":
            href = attr_dict.get("href", "")
            if "more_cursor=" in href and ":0:" in urllib.parse.unquote(href):
                self.more_top_links.append(href)

    def handle_endtag(self, tag):
        if tag == "blockquote":
            if self.quote_depth > 0:
                self.quote_depth -= 1

        elif tag == "a" and self.in_author:
            self.in_author = False

        elif tag == "div" and self.in_comment_body:
            self.in_comment_body = False
            raw_text = "".join(self.current_text).strip()

            # Clean and filter guardrails:
            # Skip empty, removed, deleted, and automated bot comments
            is_removed = any(x in raw_text.lower() for x in ["[removed]", "[deleted]", "view removed comment"])
            is_bot = "i am a bot" in raw_text.lower() or self.current_author.lower() in ("automoderator", "bot")

            if raw_text and not is_removed and not is_bot:
                comment_obj = {
                    "id": self.current_comment_id,
                    "text": raw_text,
                    "author": self.current_author,
                    "depth": self.current_comment_depth,
                }

                if self.current_comment_depth == 0:
                    # Top-level comment
                    if self.current_comment_id not in self.top_comments:
                        self.top_comments[self.current_comment_id] = comment_obj
                elif self.current_comment_depth == 1 and self.current_top_id:
                    # Direct reply (depth 1)
                    if self.current_top_id not in self.direct_replies:
                        self.direct_replies[self.current_top_id] = []
                    self.direct_replies[self.current_top_id].append(comment_obj)

    def handle_data(self, data):
        if self.in_author:
            self.current_author += data
        if self.in_comment_body:
            self.current_text.append(data)


def fetch_url(url: str, user_agent: str = "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7)") -> str:
    req = urllib.request.Request(url, headers={"User-Agent": user_agent})
    with urllib.request.urlopen(req, timeout=20) as resp:
        return resp.read().decode("utf-8")


def collect_comments(target_count: int = 200) -> List[Dict[str, str]]:
    print("Starting Reddit comments collection...")
    print(f"Target count: {target_count}")

    all_top_comments: Dict[str, Dict[str, str]] = {}
    all_direct_replies: Dict[str, List[Dict[str, str]]] = {}
    visited_urls: Set[str] = set()

    # Initial queries to cover main comment sorts
    query_paths = [
        "/r/degoogle/comments/1x8d0u2/i_think_this_is_a_wakeup_call_for_anyone_still_on/?sort=controversial",
        "/r/degoogle/comments/1x8d0u2/i_think_this_is_a_wakeup_call_for_anyone_still_on/?sort=confidence",
        "/r/degoogle/comments/1x8d0u2/i_think_this_is_a_wakeup_call_for_anyone_still_on/?sort=top",
        "/r/degoogle/comments/1x8d0u2/i_think_this_is_a_wakeup_call_for_anyone_still_on/?sort=new",
        "/r/degoogle/comments/1x8d0u2/i_think_this_is_a_wakeup_call_for_anyone_still_on/?sort=old",
    ]

    for path in query_paths:
        clean_path = path.replace("&#38;", "&")
        if clean_path in visited_urls:
            continue
        visited_urls.add(clean_path)

        url = REDLIB_HOST + clean_path
        print(f"Fetching: {clean_path[:65]}...")
        try:
            html = fetch_url(url)
            parser = RedlibThreadParser()
            parser.feed(html)

            # Store top comments
            for cid, cdata in parser.top_comments.items():
                if cid not in all_top_comments:
                    all_top_comments[cid] = cdata

            # Store direct replies
            for top_cid, replies in parser.direct_replies.items():
                if top_cid not in all_direct_replies:
                    all_direct_replies[top_cid] = []
                for rep in replies:
                    if not any(r["id"] == rep["id"] for r in all_direct_replies[top_cid]):
                        all_direct_replies[top_cid].append(rep)

            print(f"  Current unique top-level: {len(all_top_comments)}")

            # Also check more links
            for more_link in parser.more_top_links:
                clean_more = more_link.replace("&#38;", "&")
                if clean_more not in visited_urls and clean_more.startswith("/r/degoogle/comments/1x8d0u2"):
                    visited_urls.add(clean_more)
                    print(f"  Fetching cursor: {clean_more[:60]}...")
                    try:
                        cursor_html = fetch_url(REDLIB_HOST + clean_more)
                        cursor_parser = RedlibThreadParser()
                        cursor_parser.feed(cursor_html)
                        for cid, cdata in cursor_parser.top_comments.items():
                            all_top_comments[cid] = cdata
                        for top_cid, replies in cursor_parser.direct_replies.items():
                            if top_cid not in all_direct_replies:
                                all_direct_replies[top_cid] = []
                            for rep in replies:
                                if not any(r["id"] == rep["id"] for r in all_direct_replies[top_cid]):
                                    all_direct_replies[top_cid].append(rep)
                    except Exception as ex:
                        print(f"    Cursor error: {ex}")

            time.sleep(0.5)

        except Exception as e:
            print(f"  Fetch error: {e}")

    top_count = len(all_top_comments)
    print(f"\nTotal unique top-level comments found: {top_count}")

    final_selection: List[Dict[str, str]] = list(all_top_comments.values())

    # If we need more comments to reach target_count, backfill using at most 1 reply per top-level comment
    if len(final_selection) < target_count:
        needed = target_count - len(final_selection)
        print(f"Top-level comments ({len(final_selection)}) is less than target ({target_count}).")
        print(f"Backfilling {needed} comments with direct replies (maximum 1 reply per top comment)...")

        replies_added = 0
        for top_cid, replies in all_direct_replies.items():
            if replies:
                first_reply = replies[0]
                final_selection.append(first_reply)
                replies_added += 1
                if len(final_selection) >= target_count:
                    break

        print(f"Added {replies_added} direct replies. Total comments now: {len(final_selection)}")

    return final_selection[:target_count]


def write_csv(comments: List[Dict[str, str]], output_path: str):
    print(f"\nWriting {len(comments)} comments to {output_path}...")
    os.makedirs(os.path.dirname(os.path.abspath(output_path)), exist_ok=True)

    with open(output_path, mode="w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f, quoting=csv.QUOTE_MINIMAL)
        # Required format from labels_template.csv
        writer.writerow(["text", "label", "note"])

        for item in comments:
            text = item["text"]
            # Blank label for student manual labeling, 'cold' note
            writer.writerow([text, "", "cold"])

    print(f"Successfully generated {output_path}")


def main():
    comments = collect_comments(target_count=200)
    print(f"Final collected count: {len(comments)}")
    write_csv(comments, TARGET_OUTPUT)


if __name__ == "__main__":
    main()
