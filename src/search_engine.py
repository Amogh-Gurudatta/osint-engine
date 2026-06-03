import os
# pyrefly: ignore [missing-import]
import aiohttp
from urllib.parse import urlparse
# pyrefly: ignore [missing-import]
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

async def fetch_global_dork(session: aiohttp.ClientSession, username: str) -> list[dict]:
    """
    Query the Google Custom Search API for the exact username.
    Extracts the top 5 results and parses them into the graph schema.
    """
    api_key = os.getenv("GOOGLE_API_KEY")
    search_engine_id = os.getenv("GOOGLE_SEARCH_ENGINE_ID")
    
    if not api_key or not search_engine_id:
        print("[!] Google API credentials missing from .env. Skipping global dork.")
        return []
        
    url = "https://www.googleapis.com/customsearch/v1"
    params = {
        "key": api_key,
        "cx": search_engine_id,
        "q": f'"{username}"',
        "num": 5
    }
    
    results = []
    try:
        async with session.get(url, params=params) as response:
            if response.status == 200:
                data = await response.json()
                items = data.get("items", [])
                
                for item in items:
                    link = item.get("link", "")
                    title = item.get("title", "")
                    snippet = item.get("snippet", "")
                    
                    # Parse the domain name from the URL
                    try:
                        parsed_url = urlparse(link)
                        source_name = parsed_url.netloc
                        if source_name.startswith("www."):
                            source_name = source_name[4:]
                    except Exception:
                        source_name = "Unknown Website"
                    
                    # Combine title and snippet for the 'location' field
                    title_and_snippet = f"{title} - {snippet}"
                    
                    results.append({
                        "source": source_name,
                        "username": username,
                        "email": None,
                        "location": title_and_snippet
                    })
            else:
                print(f"[!] Google Custom Search API returned status {response.status}")
    except Exception as e:
        print(f"[!] Error fetching global dork for '{username}': {e}")
        
    return results
