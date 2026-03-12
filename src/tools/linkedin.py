import requests
from config.settings import settings
from rich import print as rprint

LINKEDIN_API_URL = "https://api.linkedin.com/v2/ugcPosts"

def post_to_linkedin(text: str) -> dict:
    """Post text content to LinkedIn as the authenticated user"""
    
    headers = {
        "Authorization": f"Bearer {settings.LINKEDIN_ACCESS_TOKEN}",
        "Content-Type": "application/json",
        "X-Restli-Protocol-Version": "2.0.0"
    }

    payload = {
        "author": settings.LINKEDIN_PERSON_URN,
        "lifecycleState": "PUBLISHED",
        "specificContent": {
            "com.linkedin.ugc.ShareContent": {
                "shareCommentary": {
                    "text": text
                },
                "shareMediaCategory": "NONE"
            }
        },
        "visibility": {
            "com.linkedin.ugc.MemberNetworkVisibility": "PUBLIC"
        }
    }

    try:
        response = requests.post(LINKEDIN_API_URL, json=payload, headers=headers, timeout=15)
        response.raise_for_status()
        data = response.json()
        post_id = data.get("id", "unknown")
        rprint(f"[green]🚀 Posted to LinkedIn! Post ID: {post_id}[/green]")
        return {"success": True, "post_id": post_id}

    except requests.exceptions.HTTPError as e:
        rprint(f"[red]❌ LinkedIn post failed: {e.response.status_code} {e.response.text}[/red]")
        return {"success": False, "error": str(e)}
    except Exception as e:
        rprint(f"[red]❌ LinkedIn error: {e}[/red]")
        return {"success": False, "error": str(e)}


def validate_token() -> bool:
    """Check if the LinkedIn access token is still valid"""
    headers = {"Authorization": f"Bearer {settings.LINKEDIN_ACCESS_TOKEN}"}
    try:
        r = requests.get("https://api.linkedin.com/v2/userinfo", headers=headers, timeout=10)
        if r.status_code == 200:
            data = r.json()
            rprint(f"[green]✅ LinkedIn token valid for: {data.get('name', 'Unknown')}[/green]")
            return True
        else:
            rprint(f"[red]❌ LinkedIn token invalid: {r.status_code}[/red]")
            return False
    except Exception as e:
        rprint(f"[red]❌ LinkedIn token check failed: {e}[/red]")
        return False