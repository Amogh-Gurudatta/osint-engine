import asyncio
import json
from typing import List, Dict, Any

async def fetch_github_data() -> List[Dict[str, Any]]:
    """Simulate fetching data from a Mock GitHub API."""
    await asyncio.sleep(1)
    return [
        {
            "source": "Mock GitHub",
            "username": "CodeNinja_gh",
            "email": "target.person@example.com",
            "location": "San Francisco, CA"
        },
        {
            "source": "Mock GitHub",
            "username": "AliceDev",
            "email": "alice@work.com",
            "location": "New York, NY"
        },
        {
            "source": "Mock GitHub",
            "username": "BobBuilder",
            "email": "bob@construct.com",
            "location": "Austin, TX"
        }
    ]

async def fetch_twitter_data() -> List[Dict[str, Any]]:
    """Simulate fetching data from a Mock Twitter API."""
    await asyncio.sleep(1)
    return [
        {
            "source": "Mock Twitter",
            "username": "TweetMaster99",
            "email": "target.person@example.com",
            "location": "San Francisco"
        },
        {
            "source": "Mock Twitter",
            "username": "AliceTweets",
            "email": "alice@work.com",
            "location": "NYC"
        }
    ]

async def fetch_reddit_data() -> List[Dict[str, Any]]:
    """Simulate fetching data from a Mock Reddit API."""
    await asyncio.sleep(1)
    return [
        {
            "source": "Mock Reddit",
            "username": "throwaway_anon22",
            "email": None,
            "location": "SF, California"
        },
        {
            "source": "Mock Reddit",
            "username": "builder_bob",
            "email": "bob@construct.com",
            "location": "Texas"
        }
    ]

async def fetch_linkedin_data() -> List[Dict[str, Any]]:
    """Simulate fetching data from a Mock LinkedIn API."""
    await asyncio.sleep(1)
    return [
        {
            "source": "Mock LinkedIn",
            "username": "AliceProfessional",
            "email": "alice@work.com",
            "location": "New York City"
        }
    ]

async def fetch_mock_data() -> List[Dict[str, Any]]:
    """
    Simulate hitting multiple platform APIs concurrently.
    """
    results = await asyncio.gather(
        fetch_github_data(),
        fetch_twitter_data(),
        fetch_reddit_data(),
        fetch_linkedin_data()
    )
    # Flatten the list of lists into a single list
    flat_list = [item for sublist in results for item in sublist]
    return flat_list

if __name__ == '__main__':
    data = asyncio.run(fetch_mock_data())
    print(json.dumps(data, indent=4))
