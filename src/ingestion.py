import asyncio
# pyrefly: ignore [missing-import]
import aiohttp
import json
from typing import List, Dict, Any

from search_engine import fetch_global_dork

async def fetch_github(session: aiohttp.ClientSession, target_username: str) -> List[Dict[str, Any]]:
    """Fetch live data from GitHub API."""
    url = f"https://api.github.com/users/{target_username}"
    try:
        async with session.get(url) as response:
            if response.status == 200:
                data = await response.json()
                return [{
                    "source": "GitHub",
                    "username": data.get("login"),
                    "email": data.get("email"),
                    "location": data.get("location")
                }]
    except Exception as e:
        print(f"[!] Error fetching GitHub data for {target_username}: {e}")
    return []

async def fetch_reddit(session: aiohttp.ClientSession, target_username: str) -> List[Dict[str, Any]]:
    """Fetch live data from Reddit API."""
    url = f"https://www.reddit.com/user/{target_username}/about.json"
    try:
        async with session.get(url) as response:
            if response.status == 200:
                data = await response.json()
                user_data = data.get("data", {})
                return [{
                    "source": "Reddit",
                    "username": user_data.get("name"),
                    "email": None,
                    "location": None
                }]
    except Exception as e:
        print(f"[!] Error fetching Reddit data for {target_username}: {e}")
    return []

async def fetch_hackernews(session: aiohttp.ClientSession, target_username: str) -> List[Dict[str, Any]]:
    """Fetch live data from HackerNews API."""
    url = f"https://hacker-news.firebaseio.com/v0/user/{target_username}.json"
    try:
        async with session.get(url) as response:
            if response.status == 200:
                data = await response.json()
                if data and data.get("id"):
                    return [{
                        "source": "HackerNews",
                        "username": target_username,
                        "email": None,
                        "location": None
                    }]
    except Exception as e:
        print(f"[!] Error fetching HackerNews data for {target_username}: {e}")
    return []

async def fetch_chesscom(session: aiohttp.ClientSession, target_username: str) -> List[Dict[str, Any]]:
    """Fetch live data from Chess.com API."""
    url = f"https://api.chess.com/pub/player/{target_username}"
    try:
        async with session.get(url) as response:
            if response.status == 200:
                data = await response.json()
                return [{
                    "source": "Chess.com",
                    "username": data.get("username", target_username),
                    "email": None,
                    "location": data.get("location")
                }]
    except Exception as e:
        print(f"[!] Error fetching Chess.com data for {target_username}: {e}")
    return []

async def fetch_osint_data(target_username: str) -> List[Dict[str, Any]]:
    """
    Fetch OSINT data concurrently from multiple platforms including Google Custom Search API.
    """
    headers = {
        "User-Agent": "Zense-OSINT-Audit-Tool/1.0"
    }
    
    async with aiohttp.ClientSession(headers=headers) as session:
        results = await asyncio.gather(
            fetch_github(session, target_username),
            fetch_reddit(session, target_username),
            fetch_hackernews(session, target_username),
            fetch_chesscom(session, target_username),
            fetch_global_dork(session, target_username)
        )
        
        # Flatten the list of lists since all scrapers now return lists
        flattened_results = [item for sublist in results for item in sublist]
        return flattened_results

if __name__ == '__main__':
    target = input("Enter target username: ").strip()
    if target:
        print(f"[*] Fetching live OSINT footprints for '{target}'...")
        data = asyncio.run(fetch_osint_data(target))
        print(json.dumps(data, indent=4))
    else:
        print("Username cannot be empty.")
