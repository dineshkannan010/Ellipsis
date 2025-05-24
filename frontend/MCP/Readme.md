# 🎙️ Podbean MCP Server 🎧

An MCP server for managing your podcast through the Podbean API.

## 🎉 Overview

This MCP server connects any MCP-compatible AI assistant to the Podbean API. Whether you're using Claude Desktop, or any other MCP client, you can now manage your podcasts, episodes, and analytics through natural conversation!

## ✨ Features

### 🔐 Authentication
- Client credentials authentication for managing your own podcasts
- OAuth flow for third-party access (when needed)
- Token management for multiple podcasts - juggle them all!

### 🎙️ Podcast Management
- List all your awesome podcasts in one place
- Get the nitty-gritty details about your shows
- Peek at your stats and analytics (who's listening?)
- Browse podcast categories to find your niche

### 📝 Episode Management
- See all episodes for your podcast at a glance
- Dig into the details of any episode
- Publish new episodes with ease (no more complex forms!)
- Update existing episodes when you need a tweak
- Delete episodes that didn't quite hit the mark

### 📁 File Management
- Get green lights for file uploads to Podbean
- Upload your audio masterpieces and eye-catching images
- Use those uploaded files when creating episodes

### 📊 Analytics
- Check out how many downloads your podcast is getting
- Track your daily listener counts (watching them grow!)
- See how users are interacting with your content

### 🌐 Public Podcast Access
- Access public podcast data through oEmbed
- Get the scoop on any public episode out there

## 🧰 Prerequisites

- Python 3.10 or higher (time to upgrade if you haven't already!)
- A Podbean account with API access (free or paid - they're all welcome)
- Podbean API credentials (Client ID and Secret - your magical keys to the kingdom)

## 🚀 Installation

1. Grab the code:
   ```bash
   git clone <repository-url>
   cd PodbeanMCP
   ```

2. Set up a virtual environment using the super-speedy `uv` tool:
   ```bash
   uv venv
   source .venv/bin/activate  # On Windows: .venv\Scripts\activate
   ```

3. Install the package and its dependencies:
   ```bash
   # Using uv (faster)
   uv pip install -e .
   ```

   Or if you prefer traditional pip:
   ```bash
   pip install -e .
   ```
   
   This will install all dependencies from the pyproject.toml file, including:
   - mcp[cli] (MCP SDK)
   - httpx (for API requests)
   - python-dotenv (for environment variables)
   - pydantic (for data validation)

4. Create a `.env` file with your secret Podbean powers:
   ```
   PODBEAN_CLIENT_ID=your_client_id
   PODBEAN_CLIENT_SECRET=your_client_secret
   ```

## 🏃‍♂️ Running the Server

Fire it up! It's as easy as:
```bash
python server.py
```

The server will spring to life on the default port. Magic! ✨

## 🔌 Connecting to Any MCP Client

1. Open your favorite MCP-compatible AI assistant (Claude, GPT, or any other)
2. Find the MCP server connection settings in your client
3. Add a new MCP server with the URL where your server is running (e.g., `http://localhost:8000`)
4. Boom! Your AI assistant now has podcast superpowers! 🦸‍♀️

## 🔧 Available Tools

### 🔑 Authentication Tools
- `authenticate_with_podbean()`: Get your VIP backstage pass to Podbean
- `get_podcast_tokens()`: Collect tokens for all your podcasts like Pokémon
- `get_podcast_token(podcast_id)`: Grab a token for just that special podcast

### 🎙️ Podcast Tools
- `list_podcasts_tool()`: See your podcast empire at a glance
- `get_podcast_info()`: Get the 411 on your podcast
- `get_podcast_stats(podcast_id, start_date, end_date, period, episode_id)`: Numbers, charts, and bragging rights!
- `get_daily_listeners(podcast_id, month)`: Track your growing audience day by day
- `browse_podcast_categories()`: Explore the podcast universe by category

### 🎧 Episode Tools
- `get_podcast_episodes_tool(podcast_id)`: Round up all episodes from your show
- `get_episode_details_tool(episode_id)`: Zoom in on a specific episode
- `publish_episode(podcast_id, title, content, ...)`: Release your voice to the world!
- `update_episode(episode_id, podcast_id, ...)`: Tweak that episode to perfection
- `delete_episode(episode_id, podcast_id, delete_media)`: Oops! That one needs to go...

### 💾 File Upload Tools
- `authorize_file_upload(podcast_id, filename, filesize, content_type)`: Get permission to beam files up
- `upload_file_to_podbean(presigned_url, file_path, content_type, file_key)`: Send your audio masterpieces to the cloud

### 🌐 Public Access Tools
- `get_oembed_data(url)`: Get embeddable goodies for any Podbean URL
- `get_public_episode_info(episode_url)`: Snoop on any public episode (legally, of course!)

### 🔗 OAuth Tools (for Third-Party Access)
- `generate_oauth_url(redirect_uri, scope, state)`: Create a magic login link
- `exchange_oauth_code(code, redirect_uri)`: Trade your code for a shiny token
- `refresh_oauth_token(refresh_token)`: Renew your expired token - no waiting in line!

## 📚 Available Resources

- `podbean://auth`: Your authentication treasure chest
- `podbean://podcast/{podcast_id}`: Episode collection for your podcast
- `podbean://episode/{episode_id}`: All the juicy details about an episode
- `podbean://upload/authorize`: Your upload permission slip
- `podbean://categories`: The podcast category encyclopedia
- `podbean://public/oembed`: Embed-friendly data for any Podbean URL
- `podbean://oauth/authorize`: Your OAuth permission gateway

## 💬 Available Prompts

- `podcast_summary(podcast_id)`: "Hey AI, can you summarize my podcast?"
- `episode_transcript(episode_id)`: "Turn my ramblings into readable text, please!"

## 💬 Example Usage with Any MCP Client

Here are some fun ways to chat with your AI assistant using this MCP server:

1. **Get the VIP pass**:
   ```
   Hey, can you authenticate with my Podbean account and show me my podcast collection?
   ```

2. **Round up the episodes**:
   ```
   I'm feeling nostalgic! Show me all the episodes from my "Cooking with Code" podcast.
   ```

3. **Share your brilliance with the world**:
   ```
   I'm ready to drop a new episode! It's called "AI in Podcasting" and it's all about how AI is making podcasting easier and more fun. Can you help me publish it?
   ```

4. **Check if anyone's listening** 👂:
   ```
   How's my podcast doing? Can you show me the download stats from last week?
   ```

## 🛠️ Error Handling

We've got your back when things go sideways! This server comes with super-friendly error handling:

- Authentication hiccups? We'll guide you through fixing them 🔧
- API giving you trouble? We'll tell you exactly what went wrong 🚨
- Tried something that doesn't compute? We'll let you know before it breaks 🤓
- Detailed error messages that actually make sense to humans! 😮‍💨

## 🚧 Limitations (Nobody's Perfect!)

- Want to upload files? You'll need a bit of extra setup for that 📁
- Some fancy features might need a paid Podbean subscription 💳
- Podbean has rate limits, so don't go too wild with the requests 🚀
- We can't make your podcast content go viral (that's still on you!) 🌟

## 👩‍💻 Contributing

Got ideas to make this even better? We'd love your help! Fork, code, and send us a Pull Request. Let's make podcast management even more awesome together! 🤝

## 📃 License

This project is licensed under the [Creative Commons Attribution-NonCommercial 4.0 International License](https://creativecommons.org/licenses/by-nc/4.0/).

You are free to share and adapt this code for non-commercial purposes, as long as you provide attribution and indicate any changes. For commercial use, please contact amurshak@gmail.com.


## 👏 Acknowledgments

- The amazing folks behind the Podbean API docs 📖
- The wizards who created the MCP SDK 🧙‍♂️
- You, for using this tool to make awesome podcasts! 🎉
