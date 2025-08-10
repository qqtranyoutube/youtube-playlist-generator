import streamlit as st
import pandas as pd
import plotly.express as px
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from datetime import datetime, timedelta
import pytz

# ================= CONFIG =================
st.set_page_config(page_title="🧘 Meditation YouTube Analyzer PRO", layout="wide")
YOUTUBE_API_KEY = st.secrets.get("YOUTUBE_API_KEY", None)

if not YOUTUBE_API_KEY:
    st.error("❌ Missing YouTube API Key in `.streamlit/secrets.toml`")
    st.stop()

youtube = build("youtube", "v3", developerKey=YOUTUBE_API_KEY)

# ================= FUNCTIONS =================
def search_meditation_videos_today():
    """Search for meditation videos uploaded in last 24h."""
    try:
        now = datetime.now(pytz.UTC)
        yesterday = now - timedelta(days=1)

        search_response = youtube.search().list(
            q="meditation",
            part="snippet",
            type="video",
            order="date",
            publishedAfter=yesterday.isoformat(),
            maxResults=50
        ).execute()

        videos = []
        for item in search_response.get("items", []):
            video_id = item["id"]["videoId"]
            title = item["snippet"]["title"]
            channel_id = item["snippet"]["channelId"]
            channel_title = item["snippet"]["channelTitle"]
            published_at = item["snippet"]["publishedAt"]

            videos.append({
                "video_id": video_id,
                "title": title,
                "channel_id": channel_id,
                "channel_title": channel_title,
                "published_at": published_at
            })

        return pd.DataFrame(videos)

    except HttpError as e:
        st.error(f"API Error: {e}")
        return pd.DataFrame()


def get_video_stats(video_ids):
    """Get statistics for a list of video IDs."""
    try:
        stats = []
        for i in range(0, len(video_ids), 50):
            response = youtube.videos().list(
                part="statistics,contentDetails,liveStreamingDetails",
                id=",".join(video_ids[i:i+50])
            ).execute()

            for item in response.get("items", []):
                stats.append({
                    "video_id": item["id"],
                    "views": int(item["statistics"].get("viewCount", 0)),
                    "likes": int(item["statistics"].get("likeCount", 0)),
                    "comments": int(item["statistics"].get("commentCount", 0)),
                    "duration": item["contentDetails"]["duration"],
                    "live_status": "Live" if "liveStreamingDetails" in item else "Not Live"
                })

        return pd.DataFrame(stats)

    except HttpError as e:
        st.error(f"API Error: {e}")
        return pd.DataFrame()


def get_channel_stats(channel_ids):
    """Get statistics for a list of channel IDs."""
    try:
        channels = []
        for i in range(0, len(channel_ids), 50):
            response = youtube.channels().list(
                part="statistics,snippet,status",
                id=",".join(channel_ids[i:i+50])
            ).execute()

            for item in response.get("items", []):
                channels.append({
                    "channel_id": item["id"],
                    "channel_title": item["snippet"]["title"],
                    "subs": int(item["statistics"].get("subscriberCount", 0)),
                    "country": item["snippet"].get("country", "N/A"),
                    "monetization": item["status"].get("isMonetizationEnabled", False)
                })

        return pd.DataFrame(channels)

    except HttpError as e:
        st.error(f"API Error: {e}")
        return pd.DataFrame()

# ================= APP LOGIC =================
st.title("🧘 Meditation YouTube Analyzer — PRO")
st.markdown("Analyze **daily meditation video trends**, detect fastest growing videos, livestreams, and monetization status.")

with st.spinner("🔍 Fetching today's meditation videos..."):
    df_videos = search_meditation_videos_today()

if df_videos.empty:
    st.warning("No videos found in the last 24 hours.")
    st.stop()

with st.spinner("📊 Getting video statistics..."):
    df_stats = get_video_stats(df_videos["video_id"].tolist())

with st.spinner("📈 Getting channel statistics..."):
    df_channels = get_channel_stats(df_videos["channel_id"].tolist())

# Merge all data
df = df_videos.merge(df_stats, on="video_id", how="left")
df = df.merge(df_channels, on="channel_id", how="left")

# ================= ANALYSIS =================
df["published_at"] = pd.to_datetime(df["published_at"])
df["hours_since_upload"] = (datetime.now(pytz.UTC) - df["published_at"]).dt.total_seconds() / 3600
df["views_per_hour"] = df["views"] / df["hours_since_upload"]

# Ranking: Fastest to 1000 views
df_fast_1k = df[df["views"] >= 1000].sort_values("hours_since_upload", ascending=True)

# ================= DISPLAY =================
st.subheader("📊 Fastest to Reach 1,000 Views")
st.dataframe(df_fast_1k[["title", "channel_title", "views", "hours_since_upload", "live_status"]])

st.subheader("📺 All Today's Meditation Videos")
st.dataframe(df)

fig = px.bar(df.sort_values("views", ascending=False).head(10),
             x="title", y="views", color="live_status",
             title="Top 10 Videos by Views in Last 24h")
st.plotly_chart(fig, use_container_width=True)

# Export CSV
st.download_button("💾 Download Data as CSV", df.to_csv(index=False).encode("utf-8"), "meditation_videos.csv", "text/csv")
