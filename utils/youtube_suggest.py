# utils/youtube_suggest.py

import requests
import streamlit as st

SUGGEST_URL = "https://suggestqueries.google.com/complete/search"

def get_suggestions(query: str):
    """Fetch YouTube search suggestions with detailed debug logging in Streamlit."""
    
    st.write(f"🔍 Debug: Fetching suggestions for `{query}`")

    try:
        params = {
            "client": "firefox",
            "ds": "yt",  # Restrict suggestions to YouTube
            "q": query
        }

        # Log request details
        st.write(f"🌐 Debug: Requesting {SUGGEST_URL} with params {params}")

        # Perform GET request
        resp = requests.get(SUGGEST_URL, params=params, timeout=5)
        st.write(f"📡 Debug: HTTP Status Code {resp.status_code}")

        resp.raise_for_status()  # Trigger error for non-200 codes

        # Parse JSON
        data = resp.json()
        st.write(f"📦 Debug: Raw API response: {data}")

        # Validate and extract suggestions
        if isinstance(data, list) and len(data) > 1 and isinstance(data[1], list):
            suggestions = data[1]
            st.write(f"✅ Debug: Parsed suggestions: {suggestions}")
            return suggestions
        else:
            st.warning("⚠️ Debug: Unexpected API response format.")
            return []

    except Exception as e:
        st.error(f"❌ Error in get_suggestions: {e}")
        return []
