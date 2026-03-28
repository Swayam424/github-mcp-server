from mcp.server.fastmcp import FastMCP
import httpx
import os
from dotenv import load_dotenv

load_dotenv()

mcp = FastMCP("github-mcp", stateless_http=True, host="0.0.0.0")
GITHUB_TOKEN = os.getenv("GITHUB_TOKEN")
HEADERS = {
    "Authorization": f"Bearer {GITHUB_TOKEN}",
    "Accept": "application/vnd.github+json"
}

@mcp.tool()
async def search_repos(query: str) -> str:
    """Search GitHub repositories by keyword."""
    async with httpx.AsyncClient() as client:
        r = await client.get(
            "https://api.github.com/search/repositories",
            headers=HEADERS,
            params={"q": query, "per_page": 5}
        )
        data = r.json()
        results = []
        for repo in data.get("items", []):
            results.append(f"{repo['full_name']} — {repo['description']} ★{repo['stargazers_count']}")
        return "\n".join(results) if results else "No repos found."

@mcp.tool()
async def list_issues(repo: str) -> str:
    """List open issues for a GitHub repo. Format: owner/repo"""
    async with httpx.AsyncClient() as client:
        r = await client.get(
            f"https://api.github.com/repos/{repo}/issues",
            headers=HEADERS,
            params={"state": "open", "per_page": 5}
        )
        data = r.json()
        results = []
        for issue in data:
            results.append(f"#{issue['number']} {issue['title']}")
        return "\n".join(results) if results else "No open issues."

@mcp.tool()
async def get_profile(username: str) -> str:
    """Get a GitHub user's profile info."""
    async with httpx.AsyncClient() as client:
        r = await client.get(
            f"https://api.github.com/users/{username}",
            headers=HEADERS
        )
        data = r.json()
        return f"Name: {data.get('name')}\nBio: {data.get('bio')}\nPublic repos: {data.get('public_repos')}\nFollowers: {data.get('followers')}"

app = mcp.streamable_http_app()

if __name__ == "__main__":
    import uvicorn
    port = int(os.environ.get("PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=port, forwarded_allow_ips="*", proxy_headers=True)