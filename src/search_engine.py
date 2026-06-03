import asyncio
from urllib.parse import urlparse
# pyrefly: ignore [missing-import]
from duckduckgo_search import DDGS

async def run_ddg_query(query: str, username: str) -> list[dict]:
    """
    Execute a single DuckDuckGo query in a background thread and parse the results.
    """
    results_list = []
    try:
        # Run the synchronous DuckDuckGo search without blocking the async event loop
        raw_results = await asyncio.to_thread(
            lambda: list(DDGS().text(query, max_results=5))
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
        print(f"[!] Error executing DDG query '{query}': {e}")
        
    return results_list

async def fetch_global_dork(username: str) -> list[dict]:
    """
    Perform Sniper Dorking by running multiple strict walled-garden queries concurrently.
    """
    queries = [
        # Batch 1: Mainstream Social
        f'"{username}" site:linkedin.com/in OR site:x.com OR site:twitter.com OR site:instagram.com OR site:facebook.com',
        # Batch 2: Extended Social & Media
        f'"{username}" site:tiktok.com OR site:youtube.com OR site:pinterest.com OR site:reddit.com/user',
        # Batch 3: Competitive Programming
        f'"{username}" site:leetcode.com OR site:codeforces.com OR site:codechef.com OR site:hackerearth.com OR site:hackerrank.com',
        # Batch 4: Cybersecurity & Bug Bounty
        f'"{username}" site:tryhackme.com OR site:hackthebox.com OR site:hackthebox.eu OR site:keybase.io OR site:hackerone.com OR site:bugcrowd.com',
        # Batch 5: Developer Platforms
        f'"{username}" site:gitlab.com OR site:bitbucket.org OR site:stackoverflow.com OR site:github.com',
        # Batch 6: Blogs & Portfolios
        f'"{username}" site:dev.to OR site:medium.com OR site:hashnode.com OR site:behance.net OR site:dribbble.com'
    ]
    
    print(f"[*] Firing {len(queries)} concurrent Sniper Dorks for '{username}'...")
    
    # Run all platform-specific dorks concurrently
    results = await asyncio.gather(*(run_ddg_query(q, username) for q in queries))
    
    # Flatten the list of lists into a single payload
    flattened_results = [item for sublist in results for item in sublist]
    return flattened_results
