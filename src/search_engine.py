import asyncio
from urllib.parse import urlparse
# pyrefly: ignore [missing-import]
from ddgs import DDGS

async def fetch_global_dork(username: str) -> list[dict]:
    """
    Run a global search across the entire web for a specific username
    using DuckDuckGo and parse the top 10 results dynamically.
    """
    results_list = []
    try:
        # Run the synchronous DuckDuckGo search without blocking the async event loop
        raw_results = await asyncio.to_thread(
            lambda: list(DDGS().text(f'"{username}"', max_results=10))
        )
        
        for item in raw_results:
            href = item.get("href", "")
            title = item.get("title", "")
            body = item.get("body", "")
            
            # Extract domain name and clean it up
            try:
                parsed_url = urlparse(href)
                domain_name = parsed_url.netloc
                if domain_name.startswith("www."):
                    domain_name = domain_name[4:]
            except Exception:
                domain_name = "Unknown Website"
                
            location_str = f"{title} {body}".strip()
            
            results_list.append({
                "source": domain_name,
                "username": username,
                "email": None,
                "location": location_str
            })
            
    except Exception as e:
        print(f"[!] Error fetching global dork for '{username}': {e}")
        
    return results_list
