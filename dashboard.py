"""
Dashboard - View automation status and analytics.
Run: python dashboard.py
"""

import json
import os
import sys
from datetime import datetime
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from config.settings import LOGS_DIR, NICHES, OUTPUT_DIR, BASE_DIR
from modules.analytics_engine import load_analytics, get_performance_summary


def print_header():
    print()
    print("╔══════════════════════════════════════════════════════════════╗")
    print("║          YouTube Shorts Automation Dashboard                ║")
    print("╚══════════════════════════════════════════════════════════════╝")
    print()


def print_section(title):
    print(f"\n┌─── {title} {'─' * (50 - len(title))}┐")


def print_system_status():
    """Check if all required tools are available."""
    print_section("System Status")

    checks = {
        "Python": True,
        "FFmpeg": False,
        "Gemini API key": False,
        "edge-tts": False,
        "YouTube API libs": False,
    }

    # Check FFmpeg
    import subprocess
    try:
        result = subprocess.run(["ffmpeg", "-version"], capture_output=True, timeout=5)
        checks["FFmpeg"] = result.returncode == 0
    except Exception:
        pass

    # Check Gemini config
    try:
        from config.settings import GEMINI_API_KEY
        checks["Gemini API key"] = bool(GEMINI_API_KEY)
    except Exception:
        pass

    # Check edge-tts
    try:
        import edge_tts
        checks["edge-tts"] = True
    except ImportError:
        pass

    # Check YouTube libs
    try:
        from googleapiclient.discovery import build
        from google_auth_oauthlib.flow import InstalledAppFlow
        checks["YouTube API libs"] = True
    except ImportError:
        pass

    for tool, ok in checks.items():
        status = "✓ Ready" if ok else "✗ Not found"
        icon = "🟢" if ok else "🔴"
        print(f"  {icon} {tool}: {status}")


def print_config_status():
    """Check API keys and config."""
    from config.settings import PEXELS_API_KEY, YOUTUBE_CLIENT_SECRET_FILE

    print_section("Configuration")

    configs = {
        "Pexels API Key": PEXELS_API_KEY != "YOUR_PEXELS_KEY",
        "YouTube client_secret.json": os.path.exists(YOUTUBE_CLIENT_SECRET_FILE),
        "Output directory": os.path.exists(str(OUTPUT_DIR)),
        "Logs directory": os.path.exists(str(LOGS_DIR)),
    }

    for name, ok in configs.items():
        icon = "🟢" if ok else "🔴"
        status = "Configured" if ok else "MISSING"
        print(f"  {icon} {name}: {status}")


def print_niches():
    print_section("Active Niches")
    for i, niche in enumerate(NICHES):
        print(f"  {i+1}. {niche['name']}")
        print(f"     Keywords: {', '.join(niche['keywords'][:4])}")


def print_analytics():
    """Print video performance summary."""
    print_section("Video Performance")

    summary = get_performance_summary()
    if summary["total_videos"] == 0:
        print("  No videos recorded yet. Run the automation first!")
        return

    print(f"  Total videos: {summary['total_videos']}")
    print(f"  Total views:  {summary['total_views']:,}")
    print(f"  Avg views:    {summary['avg_views_per_video']:,}")
    print(f"  Best niche:   {summary['best_niche']}")

    if summary.get("top_videos"):
        print("\n  Top Videos:")
        for v in summary["top_videos"][:5]:
            print(f"    - {v.get('title', 'N/A')[:50]}: {v.get('views', 0):,} views")

    if summary.get("niche_performance"):
        print("\n  Niche Performance:")
        for niche, views in summary["niche_performance"].items():
            print(f"    - {niche}: {views:,} views")


def print_recent_logs():
    """Print recent log entries."""
    print_section("Recent Activity")

    log_file = str(LOGS_DIR / "automation.log")
    if not os.path.exists(log_file):
        print("  No logs yet.")
        return

    try:
        with open(log_file, "r") as f:
            lines = f.readlines()
        recent = lines[-15:]
        for line in recent:
            print(f"  {line.rstrip()}")
    except Exception:
        print("  Could not read log file.")


def print_quick_start():
    print_section("Quick Start Commands")
    print("  Test (no upload):       python main.py --mode test")
    print("  Create 1 video:        python main.py --mode single --dry-run")
    print("  Create & upload:       python main.py --mode single")
    print("  Batch (4 videos):      python main.py --mode batch --count 4")
    print("  Start scheduler:       python scheduler.py")
    print("  Multi-channel batch:   python scheduler.py --multi-channel --once")
    print("  Multi-channel auto:    python scheduler.py --multi-channel")
    print("  List channels:         python -m modules.multi_channel --list")
    print("  Init channels config:  python -m modules.multi_channel --init")
    print("  View dashboard:        python dashboard.py")
    print("  Run analytics:         python main.py --mode analytics")


def print_multi_channel_status():
    """Show multi-channel configuration status."""
    print_section("Multi-Channel Status")

    try:
        from modules.multi_channel import load_channels_config
        channels = load_channels_config()
        for ch in channels:
            status = "ENABLED" if ch.get("enabled") else "disabled"
            niche = NICHES[ch["niche_index"] % len(NICHES)]["name"]
            cred_path = os.path.join(str(BASE_DIR), ch.get("client_secret", ""))
            has_creds = os.path.exists(cred_path)
            cred_icon = "🟢" if has_creds else "🔴"
            status_icon = "🟢" if ch.get("enabled") else "⚪"
            print(f"  {status_icon} {ch['name']} [{status}] → {niche} {cred_icon}")
    except Exception:
        print("  No channels configured. Run: python -m modules.multi_channel --init")


if __name__ == "__main__":
    print_header()
    print_system_status()
    print_config_status()
    print_niches()
    print_multi_channel_status()
    print_analytics()
    print_recent_logs()
    print_quick_start()
    print()
