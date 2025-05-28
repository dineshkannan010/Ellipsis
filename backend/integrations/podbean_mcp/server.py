import os
import httpx
from typing import Optional, Dict, List, Any
from urllib.parse import urlencode
from dotenv import load_dotenv
from pydantic import BaseModel
from mcp.server.fastmcp import FastMCP, Context, Image

# Load environment variables
load_dotenv()

# Podbean API configuration
CLIENT_ID = os.getenv("PODBEAN_CLIENT_ID")
CLIENT_SECRET = os.getenv("PODBEAN_CLIENT_SECRET")

# Podbean API endpoints
API_BASE_URL = "https://api.podbean.com"
TOKEN_URL = "https://api.podbean.com/v1/oauth/token"
AUTH_URL = "https://api.podbean.com/v1/dialog/oauth"

# Create MCP server
mcp = FastMCP("Podbean MCP")

# Models for API responses
class PodcastEpisode(BaseModel):
    id: str
    title: str
    content: str
    status: str
    published_at: Optional[str] = None
    duration: Optional[int] = None
    audio_url: Optional[str] = None
    logo_url: Optional[str] = None

class Podcast(BaseModel):
    id: str
    title: str
    description: str
    logo_url: Optional[str] = None
    website: Optional[str] = None
    category: Optional[str] = None

# Authentication helpers
async def get_client_credentials_token(podcast_id: str = None) -> Dict[str, Any]:
    """Get access token using client credentials flow (for managing your own podcast)"""
    try:
        if not CLIENT_ID or not CLIENT_SECRET:
            return {"error": "Podbean API credentials are not set. Please check your .env file."}
        
        # Basic auth with client_id as username and client_secret as password
        auth = httpx.BasicAuth(CLIENT_ID, CLIENT_SECRET)
        
        data = {
            "grant_type": "client_credentials"
        }
        
        if podcast_id:
            data["podcast_id"] = podcast_id
        
        async with httpx.AsyncClient() as client:
            try:
                response = await client.post(TOKEN_URL, data=data, auth=auth)
                response.raise_for_status()
                token_data = response.json()
                
                # Validate the response contains an access token
                if "access_token" not in token_data:
                    return {"error": "Invalid response from Podbean API: missing access token"}
                    
                return token_data
            except httpx.HTTPStatusError as e:
                # Handle specific HTTP errors
                status_code = e.response.status_code
                if status_code == 401:
                    return {"error": "Authentication failed. Check your Podbean API credentials."}
                elif status_code == 403:
                    return {"error": "Access forbidden. Your API credentials may not have sufficient permissions."}
                elif status_code == 429:
                    return {"error": "Rate limit exceeded. Please wait before making more requests."}
                else:
                    return {"error": f"HTTP error {status_code}: {str(e)}"}
            except httpx.RequestError as e:
                return {"error": f"Request failed: {str(e)}"}
    except Exception as e:
        return {"error": f"Unexpected error: {str(e)}"}
        
    return {"error": "Failed to get access token"}

async def get_multiple_podcasts_token() -> Dict[str, Any]:
    """Get access tokens for all podcasts owned by the user"""
    try:
        if not CLIENT_ID or not CLIENT_SECRET:
            return {"error": "Podbean API credentials are not set. Please check your .env file."}
        
        # Basic auth with client_id as username and client_secret as password
        auth = httpx.BasicAuth(CLIENT_ID, CLIENT_SECRET)
        
        data = {
            "grant_type": "client_credentials"
        }
        
        async with httpx.AsyncClient() as client:
            try:
                response = await client.post(
                    "https://api.podbean.com/v1/oauth/multiplePodcastsToken", 
                    data=data, 
                    auth=auth
                )
                response.raise_for_status()
                token_data = response.json()
                
                # Validate the response contains an access token
                if "access_token" not in token_data:
                    return {"error": "Invalid response from Podbean API: missing access token"}
                    
                return token_data
            except httpx.HTTPStatusError as e:
                # Handle specific HTTP errors
                status_code = e.response.status_code
                if status_code == 401:
                    return {"error": "Authentication failed. Check your Podbean API credentials."}
                elif status_code == 403:
                    return {"error": "Access forbidden. Your API credentials may not have sufficient permissions."}
                elif status_code == 429:
                    return {"error": "Rate limit exceeded. Please wait before making more requests."}
                else:
                    return {"error": f"HTTP error {status_code}: {str(e)}"}
            except httpx.RequestError as e:
                return {"error": f"Request failed: {str(e)}"}
    except Exception as e:
        return {"error": f"Unexpected error: {str(e)}"}
        
    return {"error": "Failed to get access token"}

# API helpers
async def fetch_podcasts(access_token: str) -> Dict[str, Any]:
    """Fetch podcasts from Podbean API"""
    try:
        if not access_token:
            return {"error": "No access token provided"}
            
        async with httpx.AsyncClient() as client:
            try:
                response = await client.get(
                    f"{API_BASE_URL}/podcast",
                    params={
                        "access_token": access_token
                    }
                )
                response.raise_for_status()
                data = response.json()
                
                # Extract podcast data
                podcast_data = data.get("podcast", {})
                if not podcast_data:
                    return {"error": "No podcast data found in the response"}
                
                # Create Podcast object
                podcast = Podcast(
                    id="default",  # Podbean doesn't return an ID for the podcast
                    title=podcast_data.get("title", "Unknown"),
                    description=podcast_data.get("desc", ""),
                    logo_url=podcast_data.get("logo"),
                    website=podcast_data.get("website"),
                    category=podcast_data.get("category_name")
                )
                
                return {"podcasts": [podcast]}
            except httpx.HTTPStatusError as e:
                # Handle specific HTTP errors
                status_code = e.response.status_code
                if status_code == 401:
                    return {"error": "Authentication failed. Your access token may be invalid or expired."}
                elif status_code == 403:
                    return {"error": "Access forbidden. You may not have permission to access this podcast."}
                elif status_code == 404:
                    return {"error": "Podcast not found."}
                elif status_code == 429:
                    return {"error": "Rate limit exceeded. Please wait before making more requests."}
                else:
                    return {"error": f"HTTP error {status_code}: {str(e)}"}
            except httpx.RequestError as e:
                return {"error": f"Request failed: {str(e)}"}
    except Exception as e:
        return {"error": f"Unexpected error: {str(e)}"}
        
    return {"error": "Failed to fetch podcasts"}

async def fetch_episodes(access_token: str, podcast_id: str = None, limit: int = 10, offset: int = 0) -> Dict[str, Any]:
    """Fetch episodes from Podbean API"""
    try:
        if not access_token:
            return {"error": "No access token provided"}
            
        async with httpx.AsyncClient() as client:
            try:
                params = {
                    "access_token": access_token,
                    "limit": limit,
                    "offset": offset
                }
                
                if podcast_id:
                    params["podcast_id"] = podcast_id
                
                response = await client.get(
                    f"{API_BASE_URL}/episodes",
                    params=params
                )
                response.raise_for_status()
                data = response.json()
                
                episodes = []
                for episode in data.get("episodes", []):
                    episodes.append(PodcastEpisode(
                        id=episode.get("id"),
                        title=episode.get("title"),
                        content=episode.get("content", ""),
                        status=episode.get("status"),
                        published_at=episode.get("publish_time"),
                        duration=episode.get("duration"),
                        audio_url=episode.get("media_url"),
                        logo_url=episode.get("logo")
                    ))
                
                return {
                    "episodes": episodes,
                    "total": data.get("count", 0),
                    "has_more": data.get("has_more", False),
                    "offset": data.get("offset", offset),
                    "limit": data.get("limit", limit)
                }
            except httpx.HTTPStatusError as e:
                # Handle specific HTTP errors
                status_code = e.response.status_code
                if status_code == 401:
                    return {"error": "Authentication failed. Your access token may be invalid or expired."}
                elif status_code == 403:
                    return {"error": "Access forbidden. You may not have permission to access these episodes."}
                elif status_code == 404:
                    return {"error": "Episodes not found."}
                elif status_code == 429:
                    return {"error": "Rate limit exceeded. Please wait before making more requests."}
                else:
                    return {"error": f"HTTP error {status_code}: {str(e)}"}
            except httpx.RequestError as e:
                return {"error": f"Request failed: {str(e)}"}
    except Exception as e:
        return {"error": f"Unexpected error: {str(e)}"}
        
    return {"error": "Failed to fetch episodes"}

async def fetch_episode_details(access_token: str, episode_id: str) -> Dict[str, Any]:
    """Fetch details for a specific episode"""
    try:
        if not access_token:
            return {"error": "No access token provided"}
            
        if not episode_id:
            return {"error": "No episode ID provided"}
            
        async with httpx.AsyncClient() as client:
            try:
                response = await client.get(
                    f"{API_BASE_URL}/episodes/{episode_id}",
                    params={
                        "access_token": access_token
                    }
                )
                response.raise_for_status()
                data = response.json()
                
                # Extract episode data
                episode_data = data.get("episode", {})
                if not episode_data:
                    return {"error": "No episode data found in the response"}
                
                # Create PodcastEpisode object
                episode = PodcastEpisode(
                    id=episode_data.get("id"),
                    title=episode_data.get("title"),
                    content=episode_data.get("content", ""),
                    status=episode_data.get("status"),
                    published_at=episode_data.get("publish_time"),
                    duration=episode_data.get("duration"),
                    audio_url=episode_data.get("media_url"),
                    logo_url=episode_data.get("logo")
                )
                
                return {"episode": episode}
            except httpx.HTTPStatusError as e:
                # Handle specific HTTP errors
                status_code = e.response.status_code
                if status_code == 401:
                    return {"error": "Authentication failed. Your access token may be invalid or expired."}
                elif status_code == 403:
                    return {"error": "Access forbidden. You may not have permission to access this episode."}
                elif status_code == 404:
                    return {"error": f"Episode with ID '{episode_id}' not found."}
                elif status_code == 429:
                    return {"error": "Rate limit exceeded. Please wait before making more requests."}
                else:
                    return {"error": f"HTTP error {status_code}: {str(e)}"}
            except httpx.RequestError as e:
                return {"error": f"Request failed: {str(e)}"}
    except Exception as e:
        return {"error": f"Unexpected error: {str(e)}"}
        
    return {"error": "Failed to fetch episode details"}

@mcp.resource("podbean://auth")
async def get_auth_resource() -> str:
    """Get authentication information for Podbean"""
    try:
        # Get tokens for all podcasts
        token_data = await get_multiple_podcasts_token()
        
        result = "# Podbean Authentication\n\n"
        
        if "error" in token_data:
            result += f"Error: {token_data['error']}\n"
            result += "\nPlease check that:\n"
            result += "1. Your Podbean API credentials are correctly set in the .env file\n"
            result += "2. Your API credentials have the necessary permissions\n"
            result += "3. The Podbean API service is available\n"
            return result
        
        # Extract main token
        access_token = token_data.get("access_token")
        token_type = token_data.get("token_type")
        expires_in = token_data.get("expires_in")
        scope = token_data.get("scope")
        
        result += "## Main Token\n"
        result += f"Access Token: {access_token}\n"
        result += f"Token Type: {token_type}\n"
        result += f"Expires In: {expires_in} seconds\n"
        result += f"Scope: {scope}\n\n"
        
        # Extract podcast tokens
        podcasts = token_data.get("podcasts", [])
        
        if podcasts:
            result += "## Podcast Tokens\n\n"
            
            for podcast in podcasts:
                result += f"### {podcast.get('title', 'Unknown')}\n"
                result += f"Podcast ID: {podcast.get('podcast_id', 'Unknown')}\n"
                result += f"Access Token: {podcast.get('access_token', 'Unknown')}\n"
                result += f"Token Type: {podcast.get('token_type', 'Unknown')}\n"
                result += f"Expires In: {podcast.get('expires_in', 'Unknown')} seconds\n"
                result += f"Scope: {podcast.get('scope', 'Unknown')}\n\n"
        else:
            result += "\n**No podcasts found.** This could mean:\n"
            result += "1. You don't have any podcasts in your Podbean account\n"
            result += "2. Your API credentials don't have access to your podcasts\n"
            result += "3. There was an issue retrieving podcast information\n"
        
        return result
    except Exception as e:
        error_message = f"Error getting authentication information: {str(e)}"
        return f"# Authentication Error\n\n{error_message}\n\nPlease check your API credentials and try again."

@mcp.resource("podbean://podcast/{podcast_id}")
async def get_podcast_episodes(podcast_id: str) -> str:
    """Get episodes for a specific podcast"""
    try:
        # Get token for the specific podcast
        token_data = await get_client_credentials_token(podcast_id)
        access_token = token_data.get("access_token")
        
        if not access_token:
            return "Failed to get access token for this podcast."
        
        # Fetch episodes using the token
        async with httpx.AsyncClient() as client:
            response = await client.get(
                f"{API_BASE_URL}/episodes",
                params={"limit": 20},
                headers={"Authorization": f"Bearer {access_token}"}
            )
            response.raise_for_status()
            data = response.json()
            
            result = f"# Episodes for Podcast {podcast_id}\n\n"
            
            if "episodes" not in data or not data["episodes"]:
                return f"{result}No episodes found for this podcast."
            
            for episode in data["episodes"]:
                result += f"## {episode.get('title', 'Untitled Episode')}\n"
                result += f"ID: {episode.get('id')}\n"
                result += f"Status: {episode.get('status', 'Unknown')}\n"
                
                if episode.get('publish_time'):
                    from datetime import datetime
                    publish_time = datetime.fromtimestamp(episode['publish_time']).strftime('%Y-%m-%d %H:%M:%S')
                    result += f"Published: {publish_time}\n"
                
                if episode.get('media_url'):
                    result += f"Audio: {episode['media_url']}\n"
                
                if episode.get('permalink_url'):
                    result += f"Link: {episode['permalink_url']}\n"
                    
                result += "\n"
            
            return result
    except Exception as e:
        return f"Error fetching episodes: {str(e)}"

@mcp.resource("podbean://episode/{episode_id}")
async def get_episode_details(episode_id: str) -> str:
    """Get details for a specific episode"""
    try:
        # First get all podcasts to find which one contains this episode
        token_data = await get_multiple_podcasts_token()
        main_token = token_data.get("access_token")
        
        if not main_token:
            return "Failed to get access token."
        
        # Use the main token to fetch the episode details
        async with httpx.AsyncClient() as client:
            response = await client.get(
                f"{API_BASE_URL}/episodes/{episode_id}",
                headers={"Authorization": f"Bearer {main_token}"}
            )
            response.raise_for_status()
            episode = response.json().get("episode", {})
            
            if not episode:
                return f"No details found for episode {episode_id}."
            
            result = f"# {episode.get('title', 'Untitled Episode')}\n\n"
            
            if episode.get('content'):
                result += f"{episode['content']}\n\n"
                
            result += f"Status: {episode.get('status', 'Unknown')}\n"
            
            if episode.get('publish_time'):
                from datetime import datetime
                publish_time = datetime.fromtimestamp(episode['publish_time']).strftime('%Y-%m-%d %H:%M:%S')
                result += f"Published: {publish_time}\n"
            
            if episode.get('media_url'):
                result += f"Audio: {episode['media_url']}\n"
                
            if episode.get('permalink_url'):
                result += f"Link: {episode['permalink_url']}\n"
                
            if episode.get('player_url'):
                result += f"Player: {episode['player_url']}\n"
                
            return result
    except Exception as e:
        return f"Error fetching episode details: {str(e)}"

@mcp.tool()
async def get_episode_details_tool(episode_id: str) -> Dict[str, Any]:
    """Get detailed information about a specific podcast episode
    
    Args:
        episode_id: The ID of the episode to get details for
    """
    try:
        # Call the episode details resource
        episode_text = await get_episode_details(episode_id)
        
        # Get token to fetch raw episode data
        token_data = await get_multiple_podcasts_token()
        main_token = token_data.get("access_token")
        
        if not main_token:
            return {
                "formatted_text": episode_text,
                "episode": {},
                "message": "Could not get raw episode data (authentication failed)"
            }
        
        # Get raw episode data
        async with httpx.AsyncClient() as client:
            response = await client.get(
                f"{API_BASE_URL}/episodes/{episode_id}",
                headers={"Authorization": f"Bearer {main_token}"}
            )
            response.raise_for_status()
            episode_data = response.json()
            
        return {
            "formatted_text": episode_text,
            "episode": episode_data.get("episode", {}),
            "message": "Successfully retrieved episode details"
        }
    except Exception as e:
        return {"error": str(e)}

# MCP Tools
@mcp.tool()
async def authenticate_with_podbean() -> Dict[str, Any]:
    """Authenticate with Podbean and get authentication information"""
    try:
        # Call the auth resource
        auth_info = await get_auth_resource()
        
        # Get tokens for all podcasts
        token_data = await get_multiple_podcasts_token()
        
        return {
            "formatted_text": auth_info,
            "main_token": token_data.get("access_token"),
            "token_type": token_data.get("token_type"),
            "expires_in": token_data.get("expires_in"),
            "scope": token_data.get("scope"),
            "podcasts": token_data.get("podcasts", []),
            "message": "Successfully authenticated with Podbean"
        }
    except Exception as e:
        return {"error": str(e)}

@mcp.tool()
async def list_podcasts_tool() -> Dict[str, Any]:
    """List all podcasts from your Podbean account"""
    try:
        # Call the podcasts resource
        podcasts_text = await list_podcasts()
        
        # Get tokens for all podcasts to get raw data
        token_data = await get_multiple_podcasts_token()
        
        return {
            "formatted_text": podcasts_text,
            "podcasts": token_data.get("podcasts", []),
            "message": "Successfully retrieved podcasts list"
        }
    except Exception as e:
        return {"error": str(e)}

@mcp.tool()
async def get_podcast_tokens() -> Dict[str, Any]:
    """Get access tokens for all podcasts in your Podbean account"""
    try:
        token_data = await get_multiple_podcasts_token()
        return {
            "main_token": token_data.get("access_token"),
            "token_type": token_data.get("token_type"),
            "expires_in": token_data.get("expires_in"),
            "scope": token_data.get("scope"),
            "podcasts": token_data.get("podcasts", []),
            "message": "Successfully retrieved tokens"
        }
    except Exception as e:
        return {"error": str(e)}

@mcp.tool()
async def get_podcast_token(podcast_id: str) -> Dict[str, Any]:
    """Get access token for a specific podcast"""
    try:
        token_data = await get_client_credentials_token(podcast_id)
        return {
            "access_token": token_data.get("access_token"),
            "token_type": token_data.get("token_type"),
            "expires_in": token_data.get("expires_in"),
            "scope": token_data.get("scope"),
            "message": f"Successfully retrieved token for podcast {podcast_id}"
        }
    except Exception as e:
        return {"error": str(e)}

@mcp.tool()
async def fetch_podcast_cover(podcast_id: str) -> Image:
    """Fetch the cover image for a podcast"""
    try:
        # Get token for this podcast
        token_data = await get_client_credentials_token(podcast_id)
        access_token = token_data.get("access_token")
        
        if not access_token:
            raise ValueError("Failed to get access token for this podcast.")
        
        # Get podcast info
        async with httpx.AsyncClient() as client:
            response = await client.get(
                f"{API_BASE_URL}/podcast",
                headers={"Authorization": f"Bearer {access_token}"}
            )
            response.raise_for_status()
            podcast_data = response.json().get("podcast", {})
            
            if not podcast_data:
                raise ValueError(f"No podcast data found for podcast {podcast_id}")
            
            logo_url = podcast_data.get("logo")
            if not logo_url:
                raise ValueError(f"No logo found for podcast {podcast_id}")
            
            # Fetch the image
            img_response = await client.get(logo_url)
            img_response.raise_for_status()
            return Image(data=img_response.content, format="jpeg")
    except Exception as e:
        raise ValueError(f"Error fetching podcast cover: {str(e)}")

@mcp.tool()
async def get_podcast_stats(podcast_id: str, start_date: str, end_date: str = None, period: str = "d", episode_id: str = None) -> Dict[str, Any]:
    """Get download statistics for a podcast or specific episode
    
    Args:
        podcast_id: The ID of the podcast
        start_date: Start date for statistics (YYYY-MM-DD format)
        end_date: End date for statistics (YYYY-MM-DD format, optional)
        period: Statistics period ('d' for daily, 'm' for monthly)
        episode_id: Optional episode ID to get stats for just that episode
    """
    try:
        # Get token for this podcast
        token_data = await get_client_credentials_token(podcast_id)
        access_token = token_data.get("access_token")
        
        if not access_token:
            return {"error": "Failed to get access token for this podcast."}
        
        # Prepare parameters
        params = {
            "start": start_date,  # Format: YYYY-MM-DD
            "access_token": access_token
        }
        
        if end_date:
            params["end"] = end_date  # Format: YYYY-MM-DD
            
        if period in ["d", "m"]:
            params["period"] = period  # d for daily, m for monthly
            
        if episode_id:
            params["episode_id"] = episode_id
        
        # Get stats
        async with httpx.AsyncClient() as client:
            response = await client.get(
                "https://api.podbean.com/v1/podcastStats/stats",
                params=params
            )
            response.raise_for_status()
            stats_data = response.json()
            
            return {
                "stats": stats_data,
                "message": "Successfully retrieved podcast statistics"
            }
    except Exception as e:
        return {"error": str(e)}

@mcp.tool()
async def get_podcast_info() -> Dict[str, Any]:
    """Get information about your podcast"""
    try:
        # Get token for all podcasts
        token_data = await get_multiple_podcasts_token()
        access_token = token_data.get("access_token")
        
        if not access_token:
            return {"error": "Failed to get access token."}
        
        # Get podcast info
        async with httpx.AsyncClient() as client:
            response = await client.get(
                f"{API_BASE_URL}/podcast",
                params={"access_token": access_token}
            )
            response.raise_for_status()
            podcast_data = response.json()
            
            return {
                "podcast": podcast_data.get("podcast", {}),
                "message": "Successfully retrieved podcast information"
            }
    except Exception as e:
        return {"error": str(e)}

@mcp.tool()
async def publish_episode(
    podcast_id: str, 
    title: str, 
    content: str, 
    status: str = "publish", 
    episode_type: str = "public", 
    media_key: str = None,
    media_url: str = None,
    logo_key: str = None,
    logo_url: str = None,
    season_number: str = None,
    episode_number: str = None,
    publish_timestamp: str = None,
    content_explicit: str = "clean"
) -> Dict[str, Any]:
    """Publish a new episode to your podcast
    
    Args:
        podcast_id: The ID of the podcast
        title: Episode title (5-200 characters)
        content: Episode description/content (HTML supported)
        status: Episode status (publish, draft, or future)
        episode_type: Episode type (public, premium, or private)
        media_key: File key for uploaded audio file (from authorize_file_upload)
        media_url: Remote URL for the episode audio file
        logo_key: File key for uploaded logo image (from authorize_file_upload)
        logo_url: Remote URL for the episode logo image
        season_number: Season number if applicable
        episode_number: Episode number if applicable
        publish_timestamp: Publishing timestamp (Unix timestamp)
        content_explicit: Whether content is explicit ("clean" or "explicit")
    """
    try:
        # Get token for this podcast
        token_data = await get_client_credentials_token(podcast_id)
        access_token = token_data.get("access_token")
        
        if not access_token:
            return {"error": "Failed to get access token for this podcast."}
        
        # Prepare data for publishing
        data = {
            "access_token": access_token,
            "title": title,
            "content": content,
            "status": status,
            "type": episode_type
        }
        
        # Add optional parameters if provided
        # For media file, prefer media_key (uploaded file) over media_url (remote file)
        if media_key:
            data["media_key"] = media_key
        elif media_url:
            data["remote_media_url"] = media_url
            
        # For logo image, prefer logo_key (uploaded file) over logo_url (remote file)
        if logo_key:
            data["logo_key"] = logo_key
        elif logo_url:
            data["remote_logo_url"] = logo_url
            
        if season_number:
            data["season_number"] = season_number
            
        if episode_number:
            data["episode_number"] = episode_number
            
        if publish_timestamp:
            data["publish_timestamp"] = publish_timestamp
            
        if content_explicit in ["clean", "explicit"]:
            data["content_explicit"] = content_explicit
        
        # Publish the episode
        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"{API_BASE_URL}/episodes",
                data=data
            )
            response.raise_for_status()
            result = response.json()
            
            return {
                "episode": result.get("episode", {}),
                "message": "Successfully published episode"
            }
    except Exception as e:
        return {"error": str(e)}

@mcp.tool()
async def update_episode(
    episode_id: str,
    podcast_id: str,
    title: str = None, 
    content: str = None, 
    status: str = None, 
    episode_type: str = None, 
    media_key: str = None,
    media_url: str = None,
    logo_key: str = None,
    logo_url: str = None,
    season_number: str = None,
    episode_number: str = None,
    publish_timestamp: str = None,
    content_explicit: str = None
) -> Dict[str, Any]:
    """Update an existing episode
    
    Args:
        episode_id: The ID of the episode to update
        podcast_id: The ID of the podcast
        title: Episode title (5-200 characters)
        content: Episode description/content (HTML supported)
        status: Episode status (publish, draft, or future)
        episode_type: Episode type (public, premium, or private)
        media_key: File key for uploaded audio file (from authorize_file_upload)
        media_url: Remote URL for the episode audio file
        logo_key: File key for uploaded logo image (from authorize_file_upload)
        logo_url: Remote URL for the episode logo image
        season_number: Season number if applicable
        episode_number: Episode number if applicable
        publish_timestamp: Publishing timestamp (Unix timestamp)
        content_explicit: Whether content is explicit ("clean" or "explicit")
    """
    try:
        # Get token for this podcast
        token_data = await get_client_credentials_token(podcast_id)
        access_token = token_data.get("access_token")
        
        if not access_token:
            return {"error": "Failed to get access token for this podcast."}
        
        # Prepare data for updating
        data = {"access_token": access_token}
        
        # Add optional parameters if provided
        if title:
            data["title"] = title
            
        if content:
            data["content"] = content
            
        if status:
            data["status"] = status
            
        if episode_type:
            data["type"] = episode_type
            
        # For media file, prefer media_key (uploaded file) over media_url (remote file)
        if media_key:
            data["media_key"] = media_key
        elif media_url:
            data["remote_media_url"] = media_url
            
        # For logo image, prefer logo_key (uploaded file) over logo_url (remote file)
        if logo_key:
            data["logo_key"] = logo_key
        elif logo_url:
            data["remote_logo_url"] = logo_url
            
        if season_number:
            data["season_number"] = season_number
            
        if episode_number:
            data["episode_number"] = episode_number
            
        if publish_timestamp:
            data["publish_timestamp"] = publish_timestamp
            
        if content_explicit:
            data["content_explicit"] = content_explicit
        
        # Update the episode
        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"{API_BASE_URL}/episodes/{episode_id}",
                data=data
            )
            response.raise_for_status()
            result = response.json()
            
            return {
                "episode": result.get("episode", {}),
                "message": "Successfully updated episode"
            }
    except Exception as e:
        return {"error": str(e)}

@mcp.tool()
async def delete_episode(episode_id: str, podcast_id: str, delete_media: bool = False) -> Dict[str, Any]:
    """Delete an episode from your podcast
    
    Args:
        episode_id: The ID of the episode to delete
        podcast_id: The ID of the podcast
        delete_media: Whether to delete the media file as well
    """
    try:
        # Get token for this podcast
        token_data = await get_client_credentials_token(podcast_id)
        access_token = token_data.get("access_token")
        
        if not access_token:
            return {"error": "Failed to get access token for this podcast."}
        
        # Prepare data for deleting
        data = {
            "access_token": access_token,
            "delete_media_file": "yes" if delete_media else "no"
        }
        
        # Delete the episode
        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"{API_BASE_URL}/episodes/{episode_id}/delete",
                data=data
            )
            response.raise_for_status()
            result = response.json()
            
            return {
                "message": result.get("msg", "Episode deleted successfully")
            }
    except Exception as e:
        return {"error": str(e)}

@mcp.tool()
async def get_podcast_episodes_tool(podcast_id: str) -> Dict[str, Any]:
    """Get episodes for a specific podcast
    
    Args:
        podcast_id: The ID of the podcast to get episodes for
    """
    try:
        # Call the resource function to get the episodes
        episodes_text = await get_podcast_episodes(podcast_id)
        
        # Get token for this podcast to get raw data as well
        token_data = await get_client_credentials_token(podcast_id)
        access_token = token_data.get("access_token")
        
        if not access_token:
            return {
                "formatted_text": episodes_text,
                "episodes": [],
                "message": "Could not get raw episode data (authentication failed)"
            }
        
        # Get raw episode data for structured access
        async with httpx.AsyncClient() as client:
            response = await client.get(
                f"{API_BASE_URL}/episodes",
                params={"limit": 20},
                headers={"Authorization": f"Bearer {access_token}"}
            )
            response.raise_for_status()
            data = response.json()
        
        return {
            "formatted_text": episodes_text,
            "episodes": data.get("episodes", []),
            "count": data.get("count", 0),
            "message": "Successfully retrieved podcast episodes"
        }
    except Exception as e:
        return {"error": str(e)}

@mcp.tool()
async def get_daily_listeners(podcast_id: str, month: str) -> Dict[str, Any]:
    """Get daily listener reports for a podcast
    
    Args:
        podcast_id: The ID of the podcast
        month: Month in YYYYMM format (e.g., 202405 for May 2024)
    """
    try:
        # Get token for this podcast
        token_data = await get_client_credentials_token(podcast_id)
        access_token = token_data.get("access_token")
        
        if not access_token:
            return {"error": "Failed to get access token for this podcast."}
        
        # Prepare parameters
        params = {
            "access_token": access_token,
            "month": month
        }
        
        # Get daily listener data
        async with httpx.AsyncClient() as client:
            response = await client.get(
                "https://api.podbean.com/v1/analytics/podcastDailyListener",
                params=params
            )
            response.raise_for_status()
            listener_data = response.json()
            
            return {
                "daily_listeners": listener_data,
                "message": "Successfully retrieved daily listener data"
            }
    except Exception as e:
        return {"error": str(e)}

# Public Podcast Access
@mcp.resource("podbean://public/oembed/{url}")
async def get_oembed_resource(url: str) -> str:
    """Get oEmbed information for any Podbean URL"""
    try:
        # Use the oEmbed endpoint to get embeddable content
        async with httpx.AsyncClient() as client:
            response = await client.get(
                f"{API_BASE_URL}/oembed",
                params={
                    "format": "json",
                    "url": url
                }
            )
            response.raise_for_status()
            oembed_data = response.json()
            
            result = f"# Podbean oEmbed for {url}\n\n"
            result += f"Type: {oembed_data.get('type', 'Unknown')}\n"
            result += f"Version: {oembed_data.get('version', 'Unknown')}\n"
            result += f"Provider: {oembed_data.get('provider_name', 'Unknown')}\n"
            result += f"Width: {oembed_data.get('width', 'Unknown')}\n"
            result += f"Height: {oembed_data.get('height', 'Unknown')}\n\n"
            
            if 'html' in oembed_data:
                result += "Embed HTML:\n```html\n"
                result += oembed_data['html']
                result += "\n```\n"
            
            return result
    except Exception as e:
        return f"Error fetching oEmbed data: {str(e)}"

@mcp.tool()
async def get_oembed_data(url: str) -> Dict[str, Any]:
    """Get embeddable content for any Podbean URL
    
    Args:
        url: The Podbean URL to get embeddable content for (e.g., episode or podcast URL)
    """
    try:
        # Call the resource
        oembed_text = await get_oembed_resource(url)
        
        # Get the raw data
        async with httpx.AsyncClient() as client:
            response = await client.get(
                f"{API_BASE_URL}/oembed",
                params={
                    "format": "json",
                    "url": url
                }
            )
            response.raise_for_status()
            oembed_data = response.json()
        
        return {
            "formatted_text": oembed_text,
            "oembed_data": oembed_data,
            "message": "Successfully retrieved oEmbed data"
        }
    except Exception as e:
        return {"error": str(e)}


@mcp.tool()
async def get_public_episode_info(episode_url: str) -> Dict[str, Any]:
    """Get information about a public episode using oEmbed and other public data
    
    Args:
        episode_url: The URL of the public episode on Podbean
    """
    try:
        # Use oEmbed to get basic info
        oembed_data = await get_oembed_data(episode_url)
        
        # Extract additional info from the oEmbed response
        # In a real implementation, you might parse more data from the response
        
        return {
            "formatted_text": oembed_data.get("formatted_text", ""),
            "episode_info": {
                "title": oembed_data.get("oembed_data", {}).get("title", "Unknown"),
                "embed_html": oembed_data.get("oembed_data", {}).get("html", ""),
                "provider": oembed_data.get("oembed_data", {}).get("provider_name", "Podbean"),
            },
            "message": "Successfully retrieved public episode information"
        }
    except Exception as e:
        return {"error": str(e)}

# MCP Prompts
@mcp.prompt()
def podcast_summary(podcast_id: str) -> str:
    """Generate a prompt to summarize a podcast"""
    return f"Please summarize the podcast with ID {podcast_id}. Include key topics and themes."

@mcp.prompt()
def episode_transcript(episode_id: str) -> str:
    """Generate a prompt to create a transcript for an episode"""
    return f"Please create a transcript for the podcast episode with ID {episode_id}."


# File Upload Functionality
@mcp.resource("podbean://upload/authorize/{podcast_id}/{filename}/{filesize}/{content_type}")
async def get_upload_authorization(podcast_id: str, filename: str, filesize: int, content_type: str) -> str:
    """Get authorization for file upload to Podbean"""
    try:
        # Get token for this podcast
        token_data = await get_client_credentials_token(podcast_id)
        access_token = token_data.get("access_token")
        
        if not access_token:
            return "Failed to get access token for this podcast."
        
        # Prepare parameters for upload authorization
        params = {
            "access_token": access_token,
            "filename": filename,
            "filesize": filesize,
            "content_type": content_type
        }
        
        # Get upload authorization
        async with httpx.AsyncClient() as client:
            response = await client.get(
                f"{API_BASE_URL}/files/uploadAuthorize",
                params=params
            )
            response.raise_for_status()
            upload_data = response.json()
            
            result = f"# File Upload Authorization\n\n"
            result += f"Filename: {filename}\n"
            result += f"Size: {filesize} bytes\n"
            result += f"Content Type: {content_type}\n\n"
            
            if "presigned_url" in upload_data:
                result += f"Presigned URL: {upload_data['presigned_url']}\n"
                result += f"Expires in: {upload_data.get('expire_in', 'Unknown')} seconds\n"
                result += f"File Key: {upload_data.get('file_key', 'Unknown')}\n"
                result += "\n"
                result += "To upload the file, use an HTTP PUT request to the presigned URL with the file content.\n"
            else:
                result += "Failed to get presigned URL for upload.\n"
            
            return result
    except Exception as e:
        return f"Error getting upload authorization: {str(e)}"

@mcp.tool()
async def authorize_file_upload(podcast_id: str, filename: str, filesize: int, content_type: str) -> Dict[str, Any]:
    """Get authorization for uploading a file to Podbean
    
    Args:
        podcast_id: The ID of the podcast
        filename: Name of the file to upload
        filesize: Size of the file in bytes
        content_type: MIME type of the file (e.g., 'audio/mpeg', 'image/jpeg')
    """
    try:
        # Call the resource
        auth_text = await get_upload_authorization(podcast_id, filename, filesize, content_type)
        
        # Get token for this podcast
        token_data = await get_client_credentials_token(podcast_id)
        access_token = token_data.get("access_token")
        
        if not access_token:
            return {
                "formatted_text": auth_text,
                "upload_info": {},
                "message": "Failed to get access token for this podcast"
            }
        
        # Get upload authorization directly
        async with httpx.AsyncClient() as client:
            response = await client.get(
                f"{API_BASE_URL}/files/uploadAuthorize",
                params={
                    "access_token": access_token,
                    "filename": filename,
                    "filesize": filesize,
                    "content_type": content_type
                }
            )
            response.raise_for_status()
            upload_data = response.json()
        
        return {
            "formatted_text": auth_text,
            "upload_info": upload_data,
            "message": "Successfully obtained upload authorization"
        }
    except Exception as e:
        return {"error": str(e)}

@mcp.tool()
async def upload_file_to_podbean(presigned_url: str, file_path: str, content_type: str, file_key: str) -> Dict[str, Any]:
    """Upload a file to Podbean using a presigned URL
    
    Args:
        presigned_url: The presigned URL obtained from authorize_file_upload
        file_path: Path to the local file to upload
        content_type: MIME type of the file (e.g., 'audio/mpeg', 'image/jpeg')
        file_key: The file_key obtained from authorize_file_upload (needed for episode publishing)
    """
    try:
        # This is a placeholder for actual file upload functionality
        # In a real implementation, you would read the file and upload it
        # using the presigned URL
        
        result = "# File Upload\n\n"
        result += f"Presigned URL: {presigned_url}\n"
        result += f"File Path: {file_path}\n"
        result += f"Content Type: {content_type}\n"
        result += f"File Key: {file_key}\n\n"
        result += "Note: This is a placeholder for actual file upload functionality.\n"
        result += "In a real implementation, you would:\n"
        result += "1. Read the file from the specified path\n"
        result += "2. Upload it using an HTTP PUT request to the presigned URL\n"
        result += "3. Return the upload status\n\n"
        result += "For security reasons, direct file access is not implemented in this MCP server.\n\n"
        result += "To use this uploaded file in an episode, use the file_key:\n"
        result += "- For audio files: Call publish_episode() with media_key={file_key}\n"
        result += "- For image files: Call publish_episode() with logo_key={file_key}\n"
        
        return {
            "formatted_text": result,
            "file_key": file_key,
            "message": "File upload simulation complete"
        }
    except Exception as e:
        return {"error": str(e)}

# Category Browsing
@mcp.resource("podbean://categories")
async def get_podcast_categories() -> str:
    """Get list of podcast categories from Podbean"""
    # Podbean doesn't have a public API for categories, so we'll provide a static list
    # based on common podcast categories
    categories = [
        {"id": "arts", "name": "Arts", "subcategories": ["Design", "Fashion & Beauty", "Food", "Literature", "Performing Arts", "Visual Arts"]},
        {"id": "business", "name": "Business", "subcategories": ["Careers", "Entrepreneurship", "Investing", "Management", "Marketing", "Non-Profit"]},
        {"id": "comedy", "name": "Comedy", "subcategories": ["Comedy Interviews", "Improv", "Stand-Up"]},
        {"id": "education", "name": "Education", "subcategories": ["Courses", "How To", "Language Learning", "Self-Improvement"]},
        {"id": "fiction", "name": "Fiction", "subcategories": ["Comedy Fiction", "Drama", "Science Fiction"]},
        {"id": "health", "name": "Health & Fitness", "subcategories": ["Alternative Health", "Fitness", "Medicine", "Mental Health", "Nutrition", "Sexuality"]},
        {"id": "history", "name": "History", "subcategories": []},
        {"id": "kids", "name": "Kids & Family", "subcategories": ["Education for Kids", "Parenting", "Stories for Kids"]},
        {"id": "leisure", "name": "Leisure", "subcategories": ["Animation & Manga", "Automotive", "Aviation", "Crafts", "Games", "Hobbies", "Home & Garden", "Video Games"]},
        {"id": "music", "name": "Music", "subcategories": ["Music Commentary", "Music History", "Music Interviews"]},
        {"id": "news", "name": "News", "subcategories": ["Business News", "Daily News", "Entertainment News", "News Commentary", "Politics", "Sports News", "Tech News"]},
        {"id": "religion", "name": "Religion & Spirituality", "subcategories": ["Buddhism", "Christianity", "Hinduism", "Islam", "Judaism", "Spirituality"]},
        {"id": "science", "name": "Science", "subcategories": ["Astronomy", "Chemistry", "Earth Sciences", "Life Sciences", "Mathematics", "Natural Sciences", "Nature", "Physics", "Social Sciences"]},
        {"id": "society", "name": "Society & Culture", "subcategories": ["Documentary", "Personal Journals", "Philosophy", "Places & Travel", "Relationships"]},
        {"id": "sports", "name": "Sports", "subcategories": ["Baseball", "Basketball", "Cricket", "Fantasy Sports", "Football", "Golf", "Hockey", "Rugby", "Soccer", "Swimming", "Tennis", "Volleyball", "Wilderness", "Wrestling"]},
        {"id": "technology", "name": "Technology", "subcategories": []},
        {"id": "true_crime", "name": "True Crime", "subcategories": []},
        {"id": "tv_film", "name": "TV & Film", "subcategories": ["After Shows", "Film History", "Film Interviews", "Film Reviews", "TV Reviews"]}
    ]
    
    result = "# Podcast Categories\n\n"
    
    for category in categories:
        result += f"## {category['name']}\n"
        if category['subcategories']:
            result += "Subcategories: " + ", ".join(category['subcategories']) + "\n"
        result += "\n"
    
    return result

@mcp.tool()
async def browse_podcast_categories() -> Dict[str, Any]:
    """Browse podcast categories available on Podbean"""
    try:
        # Call the resource
        categories_text = await get_podcast_categories()
        
        # Create structured data for categories
        categories = [
            {"id": "arts", "name": "Arts", "subcategories": ["Design", "Fashion & Beauty", "Food", "Literature", "Performing Arts", "Visual Arts"]},
            {"id": "business", "name": "Business", "subcategories": ["Careers", "Entrepreneurship", "Investing", "Management", "Marketing", "Non-Profit"]},
            {"id": "comedy", "name": "Comedy", "subcategories": ["Comedy Interviews", "Improv", "Stand-Up"]},
            {"id": "education", "name": "Education", "subcategories": ["Courses", "How To", "Language Learning", "Self-Improvement"]},
            {"id": "fiction", "name": "Fiction", "subcategories": ["Comedy Fiction", "Drama", "Science Fiction"]},
            {"id": "health", "name": "Health & Fitness", "subcategories": ["Alternative Health", "Fitness", "Medicine", "Mental Health", "Nutrition", "Sexuality"]},
            {"id": "history", "name": "History", "subcategories": []},
            {"id": "kids", "name": "Kids & Family", "subcategories": ["Education for Kids", "Parenting", "Stories for Kids"]},
            {"id": "leisure", "name": "Leisure", "subcategories": ["Animation & Manga", "Automotive", "Aviation", "Crafts", "Games", "Hobbies", "Home & Garden", "Video Games"]},
            {"id": "music", "name": "Music", "subcategories": ["Music Commentary", "Music History", "Music Interviews"]},
            {"id": "news", "name": "News", "subcategories": ["Business News", "Daily News", "Entertainment News", "News Commentary", "Politics", "Sports News", "Tech News"]},
            {"id": "religion", "name": "Religion & Spirituality", "subcategories": ["Buddhism", "Christianity", "Hinduism", "Islam", "Judaism", "Spirituality"]},
            {"id": "science", "name": "Science", "subcategories": ["Astronomy", "Chemistry", "Earth Sciences", "Life Sciences", "Mathematics", "Natural Sciences", "Nature", "Physics", "Social Sciences"]},
            {"id": "society", "name": "Society & Culture", "subcategories": ["Documentary", "Personal Journals", "Philosophy", "Places & Travel", "Relationships"]},
            {"id": "sports", "name": "Sports", "subcategories": ["Baseball", "Basketball", "Cricket", "Fantasy Sports", "Football", "Golf", "Hockey", "Rugby", "Soccer", "Swimming", "Tennis", "Volleyball", "Wilderness", "Wrestling"]},
            {"id": "technology", "name": "Technology", "subcategories": []},
            {"id": "true_crime", "name": "True Crime", "subcategories": []},
            {"id": "tv_film", "name": "TV & Film", "subcategories": ["After Shows", "Film History", "Film Interviews", "Film Reviews", "TV Reviews"]}
        ]
        
        return {
            "formatted_text": categories_text,
            "categories": categories,
            "message": "Successfully retrieved podcast categories"
        }
    except Exception as e:
        return {"error": str(e)}

# OAuth Flow for Third-Party Access
@mcp.resource("podbean://oauth/authorize/{redirect_uri}/{scope}/{state}")
def get_oauth_url(redirect_uri: str, scope: str = "podcast_read episode_read", state: str = None) -> str:
    """Generate OAuth authorization URL for third-party access"""
    if not CLIENT_ID:
        return "ERROR: PODBEAN_CLIENT_ID environment variable is not set"
    
    params = {
        "client_id": CLIENT_ID,
        "redirect_uri": redirect_uri,
        "response_type": "code",
        "scope": scope
    }
    
    if state:
        params["state"] = state
    
    auth_url = f"{AUTH_URL}?{urlencode(params)}"
    
    result = "# Podbean OAuth Authorization\n\n"
    result += f"To authorize access to a Podbean account, direct the user to this URL:\n\n"
    result += f"{auth_url}\n\n"
    result += "After authorization, the user will be redirected to your redirect_uri with a code parameter.\n"
    result += "You can then exchange this code for an access token using the exchange_oauth_code tool.\n"
    
    return result

@mcp.tool()
async def generate_oauth_url(redirect_uri: str, scope: str = "podcast_read episode_read", state: str = None) -> Dict[str, Any]:
    """Generate an OAuth authorization URL for third-party Podbean access
    
    Args:
        redirect_uri: The URL to redirect to after authorization
        scope: Space-separated list of permissions to request
        state: Optional state parameter for CSRF protection
    """
    try:
        # Call the resource
        oauth_text = get_oauth_url(redirect_uri, scope, state)
        
        # Generate the URL directly
        if not CLIENT_ID:
            return {
                "formatted_text": oauth_text,
                "auth_url": "",
                "message": "ERROR: PODBEAN_CLIENT_ID environment variable is not set"
            }
        
        params = {
            "client_id": CLIENT_ID,
            "redirect_uri": redirect_uri,
            "response_type": "code",
            "scope": scope
        }
        
        if state:
            params["state"] = state
        
        auth_url = f"{AUTH_URL}?{urlencode(params)}"
        
        return {
            "formatted_text": oauth_text,
            "auth_url": auth_url,
            "message": "Successfully generated OAuth authorization URL"
        }
    except Exception as e:
        return {"error": str(e)}

@mcp.tool()
async def exchange_oauth_code(code: str, redirect_uri: str) -> Dict[str, Any]:
    """Exchange an OAuth authorization code for an access token
    
    Args:
        code: The authorization code received from the redirect
        redirect_uri: The same redirect URI used in the authorization request
    """
    try:
        if not CLIENT_ID or not CLIENT_SECRET:
            return {"error": "Podbean API credentials are not set"}
        
        # Basic auth with client_id as username and client_secret as password
        auth = httpx.BasicAuth(CLIENT_ID, CLIENT_SECRET)
        
        data = {
            "grant_type": "authorization_code",
            "code": code,
            "redirect_uri": redirect_uri
        }
        
        async with httpx.AsyncClient() as client:
            response = await client.post(TOKEN_URL, data=data, auth=auth)
            response.raise_for_status()
            token_data = response.json()
        
        result = "# OAuth Token Exchange\n\n"
        result += "Successfully exchanged authorization code for access token.\n\n"
        result += f"Access Token: {token_data.get('access_token')}\n"
        result += f"Token Type: {token_data.get('token_type')}\n"
        result += f"Expires In: {token_data.get('expires_in')} seconds\n"
        result += f"Scope: {token_data.get('scope')}\n"
        
        if 'refresh_token' in token_data:
            result += f"Refresh Token: {token_data.get('refresh_token')}\n"
        
        return {
            "formatted_text": result,
            "token_data": token_data,
            "message": "Successfully exchanged authorization code for access token"
        }
    except Exception as e:
        return {"error": str(e)}

@mcp.tool()
async def refresh_oauth_token(refresh_token: str) -> Dict[str, Any]:
    """Refresh an OAuth access token using a refresh token
    
    Args:
        refresh_token: The refresh token received from the token exchange
    """
    try:
        if not CLIENT_ID or not CLIENT_SECRET:
            return {"error": "Podbean API credentials are not set"}
        
        # Basic auth with client_id as username and client_secret as password
        auth = httpx.BasicAuth(CLIENT_ID, CLIENT_SECRET)
        
        data = {
            "grant_type": "refresh_token",
            "refresh_token": refresh_token
        }
        
        async with httpx.AsyncClient() as client:
            response = await client.post(TOKEN_URL, data=data, auth=auth)
            response.raise_for_status()
            token_data = response.json()
        
        result = "# OAuth Token Refresh\n\n"
        result += "Successfully refreshed access token.\n\n"
        result += f"Access Token: {token_data.get('access_token')}\n"
        result += f"Token Type: {token_data.get('token_type')}\n"
        result += f"Expires In: {token_data.get('expires_in')} seconds\n"
        result += f"Scope: {token_data.get('scope')}\n"
        
        return {
            "formatted_text": result,
            "token_data": token_data,
            "message": "Successfully refreshed access token"
        }
    except Exception as e:
        return {"error": str(e)}


if __name__ == "__main__":
    mcp.run()
