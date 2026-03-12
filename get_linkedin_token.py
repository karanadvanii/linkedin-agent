import requests
import webbrowser
import threading
from http.server import HTTPServer, BaseHTTPRequestHandler
from urllib.parse import urlparse, parse_qs
from dotenv import load_dotenv
import os

load_dotenv("config/.env")

CLIENT_ID = os.getenv("LINKEDIN_CLIENT_ID")
CLIENT_SECRET = os.getenv("LINKEDIN_CLIENT_SECRET")
REDIRECT_URI = "http://localhost:8000/callback"
SCOPES = "openid profile w_member_social"

auth_code = None

class CallbackHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        global auth_code
        params = parse_qs(urlparse(self.path).query)
        auth_code = params.get("code", [None])[0]
        self.send_response(200)
        self.end_headers()
        self.wfile.write(b"<h1>Auth complete! You can close this tab.</h1>")
        threading.Thread(target=self.server.shutdown).start()

    def log_message(self, format, *args):
        pass

auth_url = (
    f"https://www.linkedin.com/oauth/v2/authorization"
    f"?response_type=code"
    f"&client_id={CLIENT_ID}"
    f"&redirect_uri={REDIRECT_URI}"
    f"&scope={SCOPES.replace(' ', '%20')}"
)

print("\n🔗 Opening LinkedIn auth in browser...")
print(f"If browser doesn't open, go to:\n{auth_url}\n")
webbrowser.open(auth_url)

server = HTTPServer(("localhost", 8000), CallbackHandler)
print("⏳ Waiting for LinkedIn callback...")
server.serve_forever()

# Exchange code for token
print("\n🔄 Exchanging code for token...")
response = requests.post(
    "https://www.linkedin.com/oauth/v2/accessToken",
    data={
        "grant_type": "authorization_code",
        "code": auth_code,
        "redirect_uri": REDIRECT_URI,
        "client_id": CLIENT_ID,
        "client_secret": CLIENT_SECRET,
    }
)

data = response.json()

if "access_token" in data:
    print(f"\n✅ Access Token:\n{data['access_token']}")
    print(f"\n⏰ Expires in: {data.get('expires_in', 'unknown')} seconds (~60 days)")

    # Also get Person URN
    token = data["access_token"]
    profile = requests.get(
        "https://api.linkedin.com/v2/userinfo",
        headers={"Authorization": f"Bearer {token}"}
    )
    profile_data = profile.json()
    person_id = profile_data.get("sub")
    person_urn = f"urn:li:person:{person_id}"
    print(f"\n✅ Your LinkedIn Person URN:\n{person_urn}")
    print(f"\n👤 Logged in as: {profile_data.get('name')}")
    print("\n📋 Copy both values above into config/.env")
else:
    print(f"\n❌ Error: {data}")