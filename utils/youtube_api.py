import requests

def get_suggestions(query: str) -> list:
    """
    Fetch YouTube search suggestions for a given query using YouTube's autocomplete API.
    """
    if not query.strip():
        return []
    
    url = "http://suggestqueries.google.com/complete/search"
    params = {
        "client": "firefox",   # returns JSON
        "ds": "yt",            # restrict to YouTube
        "q": query
    }
    try:
        resp = requests.get(url, params=params, timeout=5)
        resp.raise_for_status()
        suggestions = resp.json()[1]  # second item is list of suggestions
        return suggestions
    except Exception:
        return []
