
# utils/youtube_suggest.py

import requests

def get_suggestions(query: str) -> list:
    """
    Fetch YouTube search suggestions for a given query using YouTube's autocomplete API.
    Returns a list of suggestion strings.
    """
    if not query.strip():
        return []

    url = "http://suggestqueries.google.com/complete/search"
    params = {
        "client": "firefox",  # returns JSON
        "ds": "yt",           # restrict to YouTube
        "q": query
    }

    try:
        resp = requests.get(url, params=params, timeout=5)
        resp.raise_for_status()
        data = resp.json()
        # data[1] contains the list of suggestion strings
        return data[1] if len(data) > 1 else []
    except Exception as e:
        print(f"Error fetching suggestions: {e}")
        return []
