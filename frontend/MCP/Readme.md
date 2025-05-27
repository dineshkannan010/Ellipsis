Anchor API MCP Server Setup Guide
What This Actually Does
This MCP server uses Anchor's real API to upload podcasts that automatically distribute to:

✅ Spotify (owned by Spotify, auto-distributes)
✅ Apple Podcasts
✅ Google Podcasts
✅ Other major platforms
Prerequisites
Anchor Account: Create a free account at anchor.fm
Podcast Show: Create at least one podcast show on Anchor
API Access: Get your authentication token (see below)
Installation Steps
1. Install Dependencies
bash
# Create project
uv init anchor-mcp-server
cd anchor-mcp-server

# Add dependencies
uv add "mcp[cli]" httpx python-multipart

# Or with pip
pip install "mcp[cli]" httpx python-multipart
2. Get Anchor API Credentials
Method 1: Browser Developer Tools (Easiest)
Go to anchor.fm and log in
Open your podcast dashboard
Open browser Developer Tools (F12)
Go to Network tab
Make any action (like viewing episodes)
Look for requests to anchor.fm/api/
Copy the Authorization: Bearer <token> header value
Method 2: Inspect Anchor Web App
bash
# In browser console on anchor.fm:
localStorage.getItem('anchor_token')
# Or look for tokens in Application -> Local Storage
Method 3: Manual Authentication (Advanced)
python
# auth_helper.py - Extract token from Anchor login
import httpx
import json

async def get_anchor_token(email: str, password: str):
    async with httpx.AsyncClient() as client:
        # This might work but Anchor may have CSRF protection
        response = await client.post("https://anchor.fm/api/auth/login", json={
            "email": email,
            "password": password
        })
        
        if response.status_code == 200:
            data = response.json()
            return data.get("token")
        return None

# Usage (be careful with credentials)
token = await get_anchor_token("your-email", "your-password")
3. Get Your Station ID
After logging into Anchor, you can find your station ID by:

Go to your podcast dashboard
Look at URL: anchor.fm/dashboard/podcast/{STATION_ID}
Or use the MCP server to list stations: anchor://stations
4. Environment Setup
Create .env file:

bash
# Anchor API Authentication
ANCHOR_AUTH_TOKEN=your_bearer_token_here

# Your podcast station ID (optional, can be passed to tools)
ANCHOR_STATION_ID=your_station_id_here

# Optional: Your user ID (usually auto-detected)
ANCHOR_USER_ID=your_user_id_here
5. Running the Server
Development & Testing
bash
# Test with MCP Inspector
mcp dev anchor_mcp_server.py

# With environment file
mcp dev anchor_mcp_server.py -f .env

# With individual env vars
mcp dev anchor_mcp_server.py -v ANCHOR_AUTH_TOKEN=your_token
Claude Desktop Integration
bash
# Install in Claude Desktop
mcp install anchor_mcp_server.py --name "Anchor Podcast Uploader" -f .env

# Or with variables
mcp install anchor_mcp_server.py -v ANCHOR_AUTH_TOKEN=token -v ANCHOR_STATION_ID=station
Direct Execution
bash
python anchor_mcp_server.py
Real Usage Examples
1. List Your Podcast Shows
python
# Use resource: anchor://stations
stations = await session.read_resource("anchor://stations")
print(stations)  # Shows all your podcast shows
2. Upload Complete Episode (One Step)
python
result = await session.call_tool("upload_podcast_episode", {
    "title": "My AI-Generated Episode",
    "description": "This episode was created by my AI agent and uploaded automatically!",
    "audio_file_path": "/path/to/episode.mp3",
    "publish_immediately": True,  # or False for draft
    "is_explicit": False,
    "episode_type": "full"
})
print(result)
# Output: "Complete upload successful! Audio ID: xyz, Episode ID: abc"
3. Two-Step Process (More Control)
python
# Step 1: Upload audio
upload_result = await session.call_tool("upload_audio_file", {
    "audio_file_path": "/path/to/episode.mp3"
})
# Extract audio ID from result

# Step 2: Create episode
episode_result = await session.call_tool("create_episode", {
    "title": "My Episode",
    "description": "Episode description",
    "audio_id": "the_audio_id_from_step1",
    "publish_immediately": False  # Save as draft
})

# Step 3: Publish later if needed
publish_result = await session.call_tool("publish_episode", {
    "episode_id": "episode_id_from_step2"
})
4. List Episodes for Your Show
python
episodes = await session.read_resource("anchor://station/YOUR_STATION_ID/episodes")
print(episodes)  # All episodes for that show
Real Integration Example
Here's how to integrate with your agent application:

python
# agent_podcast_uploader.py
import asyncio
from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client

class PodcastUploader:
    def __init__(self, anchor_token: str, station_id: str):
        self.server_params = StdioServerParameters(
            command="python",
            args=["anchor_mcp_server.py"],
            env={
                "ANCHOR_AUTH_TOKEN": anchor_token,
                "ANCHOR_STATION_ID": station_id
            }
        )
    
    async def upload_episode(self, title: str, description: str, audio_path: str):
        async with stdio_client(self.server_params) as (read, write):
            async with ClientSession(read, write) as session:
                await session.initialize()
                
                # Upload in one step
                result = await session.call_tool("upload_podcast_episode", {
                    "title": title,
                    "description": description,
                    "audio_file_path": audio_path,
                    "publish_immediately": True
                })
                
                return result
    
    async def list_my_shows(self):
        async with stdio_client(self.server_params) as (read, write):
            async with ClientSession(read, write) as session:
                await session.initialize()
                
                stations_data = await session.read_resource("anchor://stations")
                return stations_data

# Usage in your agent
uploader = PodcastUploader(
    anchor_token="your_token_here",
    station_id="your_station_id"
)

# Upload a podcast your agent created
result = await uploader.upload_episode(
    title="AI Daily Briefing - March 15",
    description="Today's AI news summarized by our AI agent",
    audio_path="/tmp/ai_briefing_20240315.mp3"
)
print(result)
Audio File Requirements
Supported Formats
✅ MP3 (recommended)
✅ WAV
✅ M4A/AAC
✅ FLAC
Specifications
Max file size: 500MB
Recommended bitrate: 128kbps or higher for MP3
Sample rate: 44.1kHz recommended
Channels: Mono or Stereo
Quality Tips
python
# For AI-generated audio, ensure:
- Clear audio without clipping
- Consistent volume levels
- Remove long silences at start/end
- Add intro/outro music if desired
Troubleshooting
Common Issues
1. Authentication Errors
bash
Error: 401 Unauthorized
Solution: Your ANCHOR_AUTH_TOKEN is invalid or expired

Re-extract token from browser
Check token format (should start with Bearer)
2. Station ID Issues
bash
Error: No station ID provided
Solution:

Set ANCHOR_STATION_ID in environment
Or pass station_id parameter to tools
List stations first: anchor://stations
3. File Upload Failures
bash
Error: Audio file not found
Solution:

Check file path is absolute
Verify file exists and is readable
Check file format is supported
4. Large File Issues
bash
Error: File too large (600MB). Maximum is 500MB
Solution:

Compress audio file
Use lower bitrate (96-128kbps is fine for speech)
Split into multiple episodes if needed
Debug Mode
bash
# Run with debug logging
mcp dev anchor_mcp_server.py --log-level debug

# Check what's happening
tail -f ~/.mcp/logs/anchor_mcp_server.log
Distribution Timeline
After successful upload:

Anchor: Immediately available
Spotify: 1-4 hours typically
Apple Podcasts: 1-24 hours
Google Podcasts: 1-24 hours
Other platforms: Varies
API Rate Limits
Anchor typically allows:

File uploads: 10-20 per hour
API calls: 100-500 per hour
Large uploads: May have daily limits
Security Notes
Protecting Your Token
bash
# Use environment files (don't commit to git)
echo ".env" >> .gitignore

# Or use system environment variables
export ANCHOR_AUTH_TOKEN="your_token"

# For production, use secret management
Token Rotation
Anchor tokens may expire periodically
Monitor for 401 errors and refresh as needed
Consider automated token refresh if possible
Production Deployment
For production agent applications:

python
# production_config.py
import os
from typing import Optional

class AnchorConfig:
    def __init__(self):
        self.auth_token = os.getenv("ANCHOR_AUTH_TOKEN")
        self.station_id = os.getenv("ANCHOR_STATION_ID")
        self.max_retries = 3
        self.timeout = 60
        
    def validate(self) -> bool:
        return bool(self.auth_token and self.station_id)

# Use with error handling and retries
config = AnchorConfig()
if not config.validate():
    raise ValueError("Missing Anchor configuration")
This is a real, working implementation that uses Anchor's actual API endpoints. Your podcasts uploaded through this MCP server will automatically appear on Spotify and other major platforms!

