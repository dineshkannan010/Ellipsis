# anchor_mcp_server.py
import asyncio
import httpx
import json
import os
import mimetypes
from typing import Optional, Dict, Any, List
from contextlib import asynccontextmanager
from collections.abc import AsyncIterator
from dataclasses import dataclass
from pathlib import Path

from mcp.server.fastmcp import FastMCP, Context


@dataclass
class AnchorContext:
    """Context for Anchor API credentials and client"""
    auth_token: Optional[str] = None
    user_id: Optional[str] = None
    http_client: Optional[httpx.AsyncClient] = None
    station_id: Optional[str] = None  # Your podcast show ID on Anchor


@asynccontextmanager
async def anchor_lifespan(server: FastMCP) -> AsyncIterator[AnchorContext]:
    """Manage Anchor API client lifecycle"""
    # Initialize HTTP client with proper headers
    http_client = httpx.AsyncClient(
        timeout=httpx.Timeout(60.0),  # Longer timeout for file uploads
        headers={
            "User-Agent": "Anchor-MCP-Server/1.0",
            "Accept": "application/json"
        }
    )
    
    context = AnchorContext(
        auth_token=os.getenv("ANCHOR_AUTH_TOKEN"),
        user_id=os.getenv("ANCHOR_USER_ID"),
        station_id=os.getenv("ANCHOR_STATION_ID"),
        http_client=http_client
    )
    
    try:
        yield context
    finally:
        await http_client.aclose()


# Create MCP server with Anchor context
mcp = FastMCP(
    "Anchor Podcast Uploader", 
    dependencies=["httpx", "python-multipart"],
    lifespan=anchor_lifespan
)


async def make_anchor_request(
    ctx: AnchorContext, 
    method: str, 
    endpoint: str,
    authenticated: bool = True,
    **kwargs
) -> httpx.Response:
    """Make authenticated request to Anchor API"""
    url = f"https://anchor.fm/api/{endpoint}"
    
    if authenticated and ctx.auth_token:
        headers = kwargs.get("headers", {})
        headers["Authorization"] = f"Bearer {ctx.auth_token}"
        kwargs["headers"] = headers
    
    try:
        response = await ctx.http_client.request(method, url, **kwargs)
        return response
    except Exception as e:
        print(f"Anchor API request failed: {e}")
        raise


@mcp.resource("anchor://profile")
async def get_profile(ctx: Context) -> str:
    """Get user profile information from Anchor"""
    anchor_ctx = ctx.request_context.lifespan_context
    
    try:
        response = await make_anchor_request(
            anchor_ctx,
            "GET",
            "profile"
        )
        
        if response.status_code == 200:
            profile_data = response.json()
            return json.dumps(profile_data, indent=2)
        else:
            return f"Error fetching profile: {response.status_code} - {response.text}"
    
    except Exception as e:
        return f"Error: {str(e)}"


@mcp.resource("anchor://stations")
async def list_stations(ctx: Context) -> str:
    """List all podcast stations (shows) for the authenticated user"""
    anchor_ctx = ctx.request_context.lifespan_context
    
    try:
        response = await make_anchor_request(
            anchor_ctx,
            "GET",
            "stations"
        )
        
        if response.status_code == 200:
            stations_data = response.json()
            stations_info = []
            
            # Handle both array and object responses
            stations = stations_data if isinstance(stations_data, list) else stations_data.get("stations", [])
            
            for station in stations:
                stations_info.append({
                    "stationId": station.get("stationId"),
                    "podcastName": station.get("podcastName"),
                    "description": station.get("description"),
                    "coverArtUrl": station.get("coverArtUrl"),
                    "episodeCount": station.get("episodeCount", 0),
                    "createdAt": station.get("createdAt")
                })
            return json.dumps(stations_info, indent=2)
        else:
            return f"Error fetching stations: {response.status_code} - {response.text}"
    
    except Exception as e:
        return f"Error: {str(e)}"


@mcp.resource("anchor://station/{station_id}/episodes")
async def list_episodes(station_id: str, ctx: Context) -> str:
    """List episodes for a specific podcast station"""
    anchor_ctx = ctx.request_context.lifespan_context
    
    try:
        response = await make_anchor_request(
            anchor_ctx,
            "GET",
            f"stations/{station_id}/episodes"
        )
        
        if response.status_code == 200:
            episodes_data = response.json()
            episodes_info = []
            
            episodes = episodes_data.get("episodes", []) if isinstance(episodes_data, dict) else episodes_data
            
            for episode in episodes:
                episodes_info.append({
                    "episodeId": episode.get("episodeId"),
                    "title": episode.get("title"),
                    "description": episode.get("description"),
                    "publishOn": episode.get("publishOn"),
                    "duration": episode.get("duration"),
                    "isPublished": episode.get("isPublished", False),
                    "playCount": episode.get("playCount", 0)
                })
            return json.dumps(episodes_info, indent=2)
        else:
            return f"Error fetching episodes: {response.status_code} - {response.text}"
    
    except Exception as e:
        return f"Error: {str(e)}"


@mcp.tool()
async def upload_audio_file(
    audio_file_path: str,
    ctx: Context
) -> str:
    """
    Upload an audio file to Anchor and get the audio ID for episode creation
    
    Args:
        audio_file_path: Path to the audio file (MP3, WAV, M4A, etc.)
    """
    anchor_ctx = ctx.request_context.lifespan_context
    
    try:
        # Check if file exists
        if not os.path.exists(audio_file_path):
            return f"Error: Audio file not found at {audio_file_path}"
        
        file_path = Path(audio_file_path)
        file_size = file_path.stat().st_size
        
        # Check file size (Anchor typically has limits)
        if file_size > 500 * 1024 * 1024:  # 500MB limit
            return f"Error: File too large ({file_size / 1024 / 1024:.1f}MB). Maximum is 500MB."
        
        # Determine MIME type
        mime_type, _ = mimetypes.guess_type(audio_file_path)
        if not mime_type or not mime_type.startswith('audio/'):
            mime_type = 'audio/mpeg'  # Default to MP3
        
        # Read the audio file
        with open(audio_file_path, "rb") as audio_file:
            files = {
                "file": (file_path.name, audio_file, mime_type)
            }
            
            # Upload to Anchor's audio upload endpoint
            response = await make_anchor_request(
                anchor_ctx,
                "POST",
                "audio",
                files=files
            )
        
        if response.status_code in [200, 201]:
            upload_result = response.json()
            audio_id = upload_result.get("audioId") or upload_result.get("id")
            return f"Audio uploaded successfully! Audio ID: {audio_id}"
        else:
            return f"Upload failed: {response.status_code} - {response.text}"
    
    except Exception as e:
        return f"Error uploading audio: {str(e)}"


@mcp.tool()
async def create_episode(
    title: str,
    description: str,
    audio_id: str,
    ctx: Context,
    station_id: Optional[str] = None,
    publish_immediately: bool = False,
    is_explicit: bool = False,
    episode_type: str = "full"
) -> str:
    """
    Create a new podcast episode on Anchor
    
    Args:
        title: Episode title
        description: Episode description  
        audio_id: Audio ID from previous upload (use upload_audio_file first)
        station_id: Station ID (uses default if not provided)
        publish_immediately: Whether to publish immediately or save as draft
        is_explicit: Whether episode contains explicit content
        episode_type: Episode type (full, trailer, bonus)
    """
    anchor_ctx = ctx.request_context.lifespan_context
    
    # Use provided station_id or default from environment
    target_station_id = station_id or anchor_ctx.station_id
    if not target_station_id:
        return "Error: No station ID provided. Set ANCHOR_STATION_ID or provide station_id parameter."
    
    try:
        episode_data = {
            "title": title,
            "description": description,
            "audioId": audio_id,
            "isPublished": publish_immediately,
            "isExplicit": is_explicit,
            "episodeType": episode_type
        }
        
        # Create episode
        response = await make_anchor_request(
            anchor_ctx,
            "POST",
            f"stations/{target_station_id}/episodes",
            json=episode_data
        )
        
        if response.status_code in [200, 201]:
            episode_result = response.json()
            episode_id = episode_result.get("episodeId") or episode_result.get("id")
            status = "published" if publish_immediately else "draft"
            return f"Episode created successfully! Episode ID: {episode_id} (Status: {status})"
        else:
            return f"Episode creation failed: {response.status_code} - {response.text}"
    
    except Exception as e:
        return f"Error creating episode: {str(e)}"


@mcp.tool()
async def upload_podcast_episode(
    title: str,
    description: str,
    audio_file_path: str,
    ctx: Context,
    station_id: Optional[str] = None,
    publish_immediately: bool = False,
    is_explicit: bool = False,
    episode_type: str = "full"
) -> str:
    """
    Complete workflow: Upload audio file and create episode in one step
    
    Args:
        title: Episode title
        description: Episode description
        audio_file_path: Path to the audio file
        station_id: Station ID (uses default if not provided)
        publish_immediately: Whether to publish immediately
        is_explicit: Whether episode contains explicit content
        episode_type: Episode type (full, trailer, bonus)
    """
    try:
        # Step 1: Upload audio file
        ctx.info(f"Uploading audio file: {audio_file_path}")
        upload_result = await upload_audio_file(audio_file_path, ctx)
        
        if "Audio uploaded successfully" not in upload_result:
            return f"Failed at upload step: {upload_result}"
        
        # Extract audio ID from upload result
        audio_id = upload_result.split("Audio ID: ")[1].strip()
        
        # Step 2: Create episode
        ctx.info(f"Creating episode with audio ID: {audio_id}")
        episode_result = await create_episode(
            title=title,
            description=description,
            audio_id=audio_id,
            station_id=station_id,
            publish_immediately=publish_immediately,
            is_explicit=is_explicit,
            episode_type=episode_type,
            ctx=ctx
        )
        
        return f"Complete upload successful!\n{upload_result}\n{episode_result}"
    
    except Exception as e:
        return f"Error in complete upload workflow: {str(e)}"


@mcp.tool()
async def publish_episode(
    episode_id: str,
    station_id: Optional[str] = None,
    ctx: Context = None
) -> str:
    """
    Publish a draft episode
    
    Args:
        episode_id: The episode ID to publish
        station_id: Station ID (uses default if not provided)
    """
    anchor_ctx = ctx.request_context.lifespan_context
    target_station_id = station_id or anchor_ctx.station_id
    
    if not target_station_id:
        return "Error: No station ID provided."
    
    try:
        response = await make_anchor_request(
            anchor_ctx,
            "POST",
            f"stations/{target_station_id}/episodes/{episode_id}/publish"
        )
        
        if response.status_code == 200:
            return f"Episode {episode_id} published successfully!"
        else:
            return f"Publish failed: {response.status_code} - {response.text}"
    
    except Exception as e:
        return f"Error publishing episode: {str(e)}"


@mcp.tool()
async def update_episode(
    episode_id: str,
    ctx: Context,
    station_id: Optional[str] = None,
    title: Optional[str] = None,
    description: Optional[str] = None,
    is_explicit: Optional[bool] = None
) -> str:
    """
    Update an existing episode's metadata
    
    Args:
        episode_id: The episode ID to update
        station_id: Station ID (uses default if not provided)
        title: New title (optional)
        description: New description (optional)
        is_explicit: Update explicit flag (optional)
    """
    anchor_ctx = ctx.request_context.lifespan_context
    target_station_id = station_id or anchor_ctx.station_id
    
    if not target_station_id:
        return "Error: No station ID provided."
    
    try:
        update_data = {}
        if title is not None:
            update_data["title"] = title
        if description is not None:
            update_data["description"] = description
        if is_explicit is not None:
            update_data["isExplicit"] = is_explicit
        
        if not update_data:
            return "No updates provided"
        
        response = await make_anchor_request(
            anchor_ctx,
            "PUT",
            f"stations/{target_station_id}/episodes/{episode_id}",
            json=update_data
        )
        
        if response.status_code == 200:
            return f"Episode {episode_id} updated successfully!"
        else:
            return f"Update failed: {response.status_code} - {response.text}"
    
    except Exception as e:
        return f"Error updating episode: {str(e)}"


@mcp.prompt()
def anchor_upload_workflow(
    title: str,
    description: str,
    audio_file_path: str,
    publish_now: bool = False
) -> str:
    """Generate a step-by-step workflow for uploading to Anchor"""
    
    workflow = f"""
# Anchor Podcast Upload Workflow

## Episode Details
- **Title**: {title}
- **Description**: {description}
- **Audio File**: {audio_file_path}
- **Publish Immediately**: {'Yes' if publish_now else 'No (save as draft)'}

## Automated Workflow Steps

### Option 1: One-Step Upload (Recommended)
Use the `upload_podcast_episode` tool to handle everything automatically:

```
upload_podcast_episode(
    title="{title}",
    description="{description}",
    audio_file_path="{audio_file_path}",
    publish_immediately={str(publish_now).lower()}
)
```

### Option 2: Manual Steps (More Control)
1. **Upload Audio**: Use `upload_audio_file` to upload the audio file
2. **Create Episode**: Use `create_episode` with the returned audio ID
3. **Publish** (if needed): Use `publish_episode` to make it live

## Pre-Upload Checklist
- ✅ Audio file exists and is readable
- ✅ File format is supported (MP3, WAV, M4A)
- ✅ File size is under 500MB
- ✅ Station ID is configured
- ✅ Anchor auth token is valid

## Post-Upload
- Episode will be distributed to Spotify, Apple Podcasts, Google Podcasts automatically
- Distribution typically takes 1-24 hours
- Check episode status with `list_episodes` tool

Ready to upload? Use the tools above to proceed!
"""
    
    return workflow


if __name__ == "__main__":
    # Run the server
    mcp.run()