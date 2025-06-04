import os
import requests
import pandas as pd
from datetime import datetime
import matplotlib.pyplot as plt

ACCESS_TOKEN = os.getenv('FB_ACCESS_TOKEN')
PAGE_ID = '654600201070324'
POST_LIMIT = 1000


def get_facebook_posts(page_id, access_token, limit=POST_LIMIT):
    url = f"https://graph.facebook.com/v19.0/{page_id}/posts"
    params = {
        'access_token': access_token,
        'fields': 'id,message,created_time,permalink_url',
        'limit': limit
    }
    posts = []
    while url:
        res = requests.get(url, params=params).json()
        posts.extend(res.get('data', []))
        url = res.get('paging', {}).get('next')
        params = None
    return posts


def get_comments(post_id, access_token):
    url = f"https://graph.facebook.com/v19.0/{post_id}/comments"
    params = {
        'access_token': access_token,
        'fields': 'id,message,created_time',
        'limit': 100
    }
    comments = []
    while url:
        res = requests.get(url, params=params).json()
        comments.extend(res.get('data', []))
        url = res.get('paging', {}).get('next')
        params = None
    return comments


def collect_data(page_id, access_token, keyword):
    keyword_lower = keyword.lower()
    posts = get_facebook_posts(page_id, access_token)
    results = []

    for post in posts:
        month = datetime.fromisoformat(post['created_time'].replace('Z', '+00:00')).strftime('%Y-%m')
        post_match = keyword_lower in (post.get('message') or '').lower()
        comments = get_comments(post['id'], access_token)
        comment_matches = [keyword_lower in (c.get('message') or '').lower() for c in comments]
        total_matches = post_match + sum(comment_matches)
        results.append({'month': month, 'matches': total_matches})

    df = pd.DataFrame(results)
    monthly_counts = df.groupby('month')['matches'].sum().sort_index()
    return monthly_counts


def plot_counts(counts, keyword):
    diff = counts.diff()
    fig, ax = plt.subplots(figsize=(8, 4))
    counts.plot(kind='bar', ax=ax)
    ax.set_title(f"Monthly frequency of '{keyword}'")
    ax.set_xlabel('Month')
    ax.set_ylabel('Occurrences')
    plt.tight_layout()
    plt.show()
    print('\nMonth-over-month difference:')
    print(diff)


if __name__ == '__main__':
    if not ACCESS_TOKEN:
        raise RuntimeError('Set FB_ACCESS_TOKEN environment variable with your API token.')
    keyword = input('검색할 키워드 입력: ').strip()
    counts = collect_data(PAGE_ID, ACCESS_TOKEN, keyword)
    print(counts)
    plot_counts(counts, keyword)
