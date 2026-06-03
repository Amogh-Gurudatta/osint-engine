import asyncio
# pyrefly: ignore [missing-import]
import aiohttp
import json
from typing import List, Dict, Any

async def fetch_github(session: aiohttp.ClientSession, target_username: str) -> Dict[str, Any] | None:
    """Fetch live data from GitHub API."""
    url = f"https://api.github.com/users/{target_username}"
    try:
        async with session.get(url) as response:
            if response.status == 200:
                data = await response.json()
                return {
                    "source": "GitHub",
                    "username": data.get("login"),
                    "email": data.get("email"),
                    "location": data.get("location")
                }
            elif response.status == 404:
                return None
    except Exception as e:
        print(f"[!] Error fetching GitHub data for {target_username}: {e}")
    return None

async def fetch_reddit(session: aiohttp.ClientSession, target_username: str) -> Dict[str, Any] | None:
    """Fetch live data from Reddit API."""
    url = f"https://www.reddit.com/user/{target_username}/about.json"
    try:
        async with session.get(url) as response:
            if response.status == 200:
                data = await response.json()
                user_data = data.get("data", {})
                return {
                    "source": "Reddit",
                    "username": user_data.get("name"),
                    "email": None,  # Reddit API doesn't expose this publicly
                    "location": None
                }
            elif response.status == 404:
                return None
    except Exception as e:
        print(f"[!] Error fetching Reddit data for {target_username}: {e}")
    return None

async def fetch_osint_data(target_username: str) -> List[Dict[str, Any]]:
    """
    Fetch OSINT data concurrently from multiple platforms for a given target username.
    """
    headers = {
        "User-Agent": "Zense-OSINT-Audit-Tool/1.0"
    }
    
    async with aiohttp.ClientSession(headers=headers) as session:
        results = await asyncio.gather(
            fetch_github(session, target_username),
            fetch_reddit(session, target_username)
        )
        
        # Filter out 404s (None values)
        valid_results = [res for res in results if res is not None]
        return valid_results

if __name__ == '__main__':
    target = input("Enter target username: ").strip()
    if target:
        print(f"[*] Fetching live OSINT footprints for '{target}'...")
        data = asyncio.run(fetch_osint_data(target))
        print(json.dumps(data, indent=4))
    else:
        print("Username cannot be empty.")
