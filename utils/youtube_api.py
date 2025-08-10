from googleapiclient.discovery import build
import pandas as pd

def youtube_service(api_key):
    return build("youtube", "v3", developerKey=api_key)

def search_videos(api_key, query, max_results=10):
    youtube = youtube_service(api_key)
    request = youtube.search().list(
        q=query,
        part="snippet",
        type="video",
        maxResults=max_results
    )
    response = request.execute()
    videos = []
    for item in response["items"]:
        videos.append({
            "videoId": item["id"]["videoId"],
            "title": item["snippet"]["title"],
            "channel": item["snippet"]["channelTitle"],
            "publishedAt": item["snippet"]["publishedAt"],
            "url": f"https://www.youtube.com/watch?v={item['id']['videoId']}"
        })
    return pd.DataFrame(videos)
