# 🎙️ Ellipsis — One Click. Infinite Conversations.
![image](https://github.com/user-attachments/assets/7aad285d-952b-465f-9537-fbe692e7c8f2)


## Table of Contents

* [Introduction](#introduction)
* [Feature Comparison](#feature-comparison)
* [Tech Stack](#tech-stack)
* [Prerequisites](#prerequisites)
* [Configuration](#configuration)
* [Installation](#installation)
* [Usage](#usage)

  * [Content Generation](#content-generation)
  * [Streaming Updates (SSE)](#streaming-updates-sse)
  * [Trending Topics](#trending-topics)
  * [Podbean Publishing](#podbean-publishing)
  * [Cancellation](#cancellation)

* [License](#license)
* [Contact](#contact)

---

## Introduction

**Ellipsis** is a next-gen podcast generation agent that brings human-like, high-quality audio content to life—on *any* topic, with just **one click**.

Whether it’s **breaking news**, **deep-dive tech explainers**, **movie reviews**, or **post-match sports breakdowns**, ellipsis crafts intelligent podcast episodes that sound like they were created by seasoned hosts in a professional studio.


### 🚀 What Makes ellipsis Unique?

- **🧠 Intelligent Multi-Speaker Dialogue**  
  Automatically generates natural, engaging conversations with multiple distinct voices and personalities.

- **📚 Covers *Everything***  
  From LLM architectures to lunar eclipses, ellipsis understands the depth and nuance of any topic.

- **✅ Custom Evaluation Engine**  
  Each episode is passed through rigorous evaluation pipelines to ensure:
  - Factual accuracy 🧾  
  - Legal and ethical soundness ⚖️  
  - High conversational quality 🎧

---

## Feature Comparison

| Feature                         | Ellipsis                                           | NotebookLM                                  | NoteGPT                                             |
|---------------------------------|----------------------------------------------------|----------------------------------------------|----------------------------------------------------|
| 🎙️ Podcast Generation           | ✅ fully automated                                  | ✅ fully automated                            | ✅ fully automated                              |
| 🧠 Multi-Speaker Support        | ✅ Multiple distinct voices                         | ❌ Two-speaker conversations                  | ✅ Multiple distinct voices                     |
| 📚 Topic Versatility            | ✅ Covers news, tech, movies, sports, etc.          | ⚠️ No web search capability yet               | ⚠️ Limited to provided notebook context         |
| ✅ Factual & Legal Evaluation   | ✅ Built-in evaluators for accuracy & legality      | ⚠️ Not Clearly specified                      | ❌ No evaluation engine                            |
| 🎧 Audio Output Quality         | ✅ Human-like, podcast-ready audio                  | ✅ Human-like, podcast-ready audio            | ❌ Conversations at this point sound more robotic  |
| 🛠️ Custom Input formats         | ⚠️ Currently working on Documents                   | ✅ Supports Documents, Video URLs etc         | ⚠️ Supports Documents but not other sources        |



## Tech Stack

* **Backend**: Python, Flask, Redis (pub/sub), llama.cpp, Orpheus TTS
* **Frontend**: React, Vite, Tailwind CSS, Lucide Icons
* **Integration**: Perplexity API, Podbean MCP, Server-Sent Events (SSE)

## Prerequisites

* Node.js v16+ and npm/yarn
* Python 3.10+ and pip
* Redis server running (default on `localhost:6380`)

## Configuration

* Copy this to `backend/.env` and set:

  ```ini
  REDIS_URL=redis://localhost:6379
  PERPLEXITY_API_KEY=your_key_here
  PODBEAN_CLIENT_ID=...
  PODBEAN_CLIENT_SECRET=...
  ```

* Copy this to `frontend/.env` and set:

  ```ini
    # VCL: default set to localhost
    REACT_APP_API_URL=http://127.0.0.1:5000 
  ```

## Installation

1. **Clone the repo**

   ```bash
   git clone https://github.com/dineshkannan010/Ellipsis.git
   cd Ellipsis
   ```

2. **Backend setup**

   ```bash
   cd backend
   python -m venv venv
   source venv/bin/activate    # macOS/Linux
   venv\Scripts\activate     # Windows
   pip install -r requirements.txt
   ```
   Install native & extra-index packages
   Some packages aren’t available on PyPI and must be pulled from alternate indexes or GitHub:

   ```bash
   # llama.cpp (CPU wheel)
    pip install llama-cpp-python \
    --extra-index-url https://abetlen.github.io/llama-cpp-python/whl/cpu

   # Orpheus TTS bindings
    pip install git+https://github.com/freddyaboulton/orpheus-cpp.git

   # HuggingFace XET backend
    pip install huggingface_hub[hf_xet] hf_xet

   ```

3. **Frontend setup**

   ```bash
   cd frontend
   npm install                # or yarn install
   ```

## Usage

### Content Generation

* Launch backend:

  ```bash
  cd backend
  python app.py
  ```

* Launch Redis Server

  ```bash
  redis-server --port 6380
  ```
* Launch frontend:

  ```bash
  cd frontend
  npm run dev                # or yarn dev
  ```

* Enter a topic in the homepage textbox and hit **Enter**. Switch to the `ContentGenerationView` to see live script & audio progress.

### Streaming Updates (SSE)

* The frontend subscribes to `/stream` via EventSource.
* Backend publishes events of types `status`, `script`, and `audio`.

### Trending Topics

* Click **Trending** in the post box.
* Fetches `/api/trending`, which queries Perplexity with a custom prompt.

### Podbean Publishing

* After audio is ready, enter a prompt like `Post this podcast to Podbean`.
* The client detects `podbean` intent and calls `/api/podbean/publish` via Beacon or `fetch`.



## License

[MIT © Ellipsis]((https://github.com/dineshkannan010/Ellipsis/blob/master/LICENSE.md)) 

## Contact

For questions or feedback, open an issue or reach out to 

  <table>
    <tr>
      <td align="center">
        <a href="https://github.com/dineshkannan010">
          <sub><b>Dinesh Kannan</b></sub>
        </a><br />
      </td>
      <td align="center">
        <a href="https://github.com/lohithsowmiyan">
          <sub><b>Lohith Senthilkumar</b></sub>
        </a><br />
      </td>
      <td align="center">
        <a href="https://github.com/ParinitadasUX">
          <sub><b>Parinita Das</b></sub>
        </a><br />
      </td>
      <td align="center">
        <a href="https://github.com/manideepika21">
          <sub><b>Manideepika Myaka</b></sub>
        </a><br />
      </td>
    </tr>
  </table>
