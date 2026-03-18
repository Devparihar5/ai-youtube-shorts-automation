"""
Analytics Engine
Tracks video performance and generates AI feedback for optimization.
Stores data in local JSON (no database needed).
"""

import json
import os
from datetime import datetime, timedelta
from pathlib import Path
from typing import List, Optional
from config.settings import OUTPUT_DIR, LOGS_DIR
from utils import get_logger

log = get_logger("analytics")

ANALYTICS_FILE = str(LOGS_DIR / "video_analytics.json")
PERFORMANCE_FILE = str(LOGS_DIR / "performance_history.json")


def load_analytics() -> list:
    """Load analytics data from file."""
    try:
        if os.path.exists(ANALYTICS_FILE):
            with open(ANALYTICS_FILE, "r") as f:
                return json.load(f)
    except Exception:
        pass
    return []


def save_analytics(data: list):
    """Save analytics data."""
    try:
        with open(ANALYTICS_FILE, "w") as f:
            json.dump(data, f, indent=2, default=str)
    except Exception as e:
        log.error(f"Failed to save analytics: {e}")


def record_video(
    video_id: str,
    title: str,
    idea: str,
    niche: str,
    script: str,
    seo_data: dict,
) -> dict:
    """Record a new video in analytics."""
    entry = {
        "video_id": video_id,
        "title": title,
        "idea": idea,
        "niche": niche,
        "script_preview": script[:200],
        "seo": seo_data,
        "created_at": datetime.now().isoformat(),
        "views": 0,
        "likes": 0,
        "comments": 0,
        "watch_time_hours": 0,
        "ctr": 0,
        "last_checked": None,
    }

    data = load_analytics()
    data.append(entry)
    save_analytics(data)

    log.info(f"Recorded video: {video_id} - {title}")
    return entry


def update_video_stats(video_id: str, stats: dict):
    """Update stats for a specific video."""
    data = load_analytics()
    for entry in data:
        if entry.get("video_id") == video_id:
            entry.update({
                "views": stats.get("views", entry.get("views", 0)),
                "likes": stats.get("likes", entry.get("likes", 0)),
                "comments": stats.get("comments", entry.get("comments", 0)),
                "watch_time_hours": stats.get("watch_time_hours", 0),
                "ctr": stats.get("ctr", 0),
                "last_checked": datetime.now().isoformat(),
            })
            break
    save_analytics(data)


def fetch_youtube_stats(video_ids: list) -> dict:
    """Fetch latest stats from YouTube API."""
    try:
        from modules.youtube_upload import get_authenticated_service
        youtube = get_authenticated_service()
        if not youtube:
            return {}

        stats = {}
        # YouTube API allows up to 50 IDs per request
        for i in range(0, len(video_ids), 50):
            batch = video_ids[i:i+50]
            response = youtube.videos().list(
                part="statistics",
                id=",".join(batch),
            ).execute()

            for item in response.get("items", []):
                vid = item["id"]
                s = item.get("statistics", {})
                stats[vid] = {
                    "views": int(s.get("viewCount", 0)),
                    "likes": int(s.get("likeCount", 0)),
                    "comments": int(s.get("commentCount", 0)),
                }

        return stats
    except Exception as e:
        log.warning(f"Stats fetch failed: {e}")
        return {}


def refresh_all_stats():
    """Refresh stats for all recorded videos."""
    data = load_analytics()
    if not data:
        log.info("No videos to refresh")
        return

    video_ids = [e["video_id"] for e in data if e.get("video_id")]
    if not video_ids:
        return

    stats = fetch_youtube_stats(video_ids)
    for vid, s in stats.items():
        update_video_stats(vid, s)

    log.info(f"Refreshed stats for {len(stats)} videos")


def get_performance_summary() -> dict:
    """Get summary of all video performance."""
    data = load_analytics()
    if not data:
        return {"total_videos": 0}

    total_views = sum(e.get("views", 0) for e in data)
    total_likes = sum(e.get("likes", 0) for e in data)
    avg_views = total_views / len(data) if data else 0

    # Find best performing videos
    sorted_by_views = sorted(data, key=lambda x: x.get("views", 0), reverse=True)

    # Find best niche
    niche_views = {}
    for e in data:
        niche = e.get("niche", "unknown")
        niche_views[niche] = niche_views.get(niche, 0) + e.get("views", 0)

    best_niche = max(niche_views, key=niche_views.get) if niche_views else "unknown"

    return {
        "total_videos": len(data),
        "total_views": total_views,
        "total_likes": total_likes,
        "avg_views_per_video": round(avg_views),
        "best_niche": best_niche,
        "top_videos": sorted_by_views[:5],
        "niche_performance": niche_views,
    }


def generate_ai_feedback() -> str:
    """Generate AI-powered optimization feedback."""
    from modules.ai_engine import ask_gemini

    summary = get_performance_summary()
    if summary["total_videos"] == 0:
        return "No videos yet. Start creating to get feedback!"

    data = load_analytics()
    recent = data[-10:]  # Last 10 videos

    video_info = "\n".join([
        f"- {v.get('title', 'N/A')}: {v.get('views', 0)} views, niche: {v.get('niche', 'N/A')}"
        for v in recent
    ])

    prompt = f"""You are a YouTube Shorts analytics expert.

CHANNEL PERFORMANCE:
Total videos: {summary['total_videos']}
Total views: {summary['total_views']}
Average views/video: {summary['avg_views_per_video']}
Best niche: {summary['best_niche']}

RECENT VIDEOS:
{video_info}

NICHE PERFORMANCE:
{json.dumps(summary.get('niche_performance', {}), indent=2)}

Analyze this data and provide:
1. Which niche is working best and why
2. What type of hooks are getting most views
3. 3 specific recommendations to increase views
4. 5 new video ideas based on what's working

Be specific and actionable. Keep it concise."""

    feedback = ask_gemini(prompt)
    
    # Save feedback
    feedback_data = {
        "timestamp": datetime.now().isoformat(),
        "summary": summary,
        "feedback": feedback,
    }
    
    try:
        history = []
        if os.path.exists(PERFORMANCE_FILE):
            with open(PERFORMANCE_FILE, "r") as f:
                history = json.load(f)
        history.append(feedback_data)
        # Keep last 30 entries
        history = history[-30:]
        with open(PERFORMANCE_FILE, "w") as f:
            json.dump(history, f, indent=2, default=str)
    except Exception:
        pass

    log.info("AI feedback generated")
    return feedback


if __name__ == "__main__":
    summary = get_performance_summary()
    print(json.dumps(summary, indent=2, default=str))
