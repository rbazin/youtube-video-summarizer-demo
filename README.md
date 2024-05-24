# YouTube Video Summarizer Demo

[![License](https://img.shields.io/badge/license-MIT-blue.svg)](LICENSE)
[![Python Version](https://img.shields.io/badge/python-3.11-blue.svg)](https://www.python.org/downloads/)
[![Docker](https://img.shields.io/badge/docker-%230db7ed.svg?style=flat&logo=docker&logoColor=white)](https://www.docker.com/)
[![FastAPI](https://img.shields.io/badge/FastAPI-005571?style=flat&logo=fastapi)](https://fastapi.tiangolo.com/)
[![Redis](https://img.shields.io/badge/redis-%23DD0031.svg?style=flat&logo=redis&logoColor=white)](https://redis.io/)

A full-stack demo application that generates concise summaries of YouTube videos using AI-powered transcription and summarization. Built with Python, FastAPI, Gradio, Docker, and Redis, and leveraging Whisper / AssemblyAI and Groq's LLAMA-3 model.

## Features

- Automatically fetches YouTube video transcripts or generates them using AssemblyAI's speech-to-text API
- Summarizes transcripts using Groq's powerful LLAMA-3 language model
- Presents summaries in a clear, structured format with titles, sub-sections, and bullet points
- Caches transcripts and summaries for efficient retrieval of popular videos
- Provides a simple, intuitive web interface for inputting video URLs and viewing summaries
- Containerized with Docker for easy deployment and consistency across environments

## Installation

1. Clone the repository:
   ```
   git clone https://github.com/yourusername/youtube-video-summarizer.git
   cd youtube-video-summarizer
   ```

2. Create a `.env` file in the project root with your AssemblyAI and Groq API keys:
   ```
   GROQ_API_KEY=your_groq_api_key
   ASSEMBLYAI_API_KEY=your_assemblyai_api_key
   TRANSCRIBER_MODEL_NAME="distil-large-v2"
   SUMMARIZER_MODEL_NAME="llama3-70b-8192"
   ```

3. Make sure you have Docker and Docker Compose installed on your machine. Then, run:
   ```
   docker compose --project-name ytb-summarizer --up -d --build
   ```

4. Once the build is complete and the containers are running, navigate to `http://localhost:8000/gradio` in your web browser to access the application.

## Usage

1. In the Gradio interface, paste a YouTube video URL into the input box.
2. Click "Submit" to generate a summary of the video.
3. View the generated summary, including the main title, sub-sections, and key points.
4. To summarize another video, simply paste a new URL and click "Submit" again.

## Architecture

The application consists of several key components:

- `AsyncVideoDownloader`: Fetches video metadata and transcripts (if available) from YouTube, or downloads the audio for transcription.
- `AsyncAudioTranscriber`: Transcribes audio using AssemblyAI's speech-to-text API or a local Whisper model.
- `AsyncTranscriptSummarizer`: Summarizes transcripts using Groq's LLAMA-3 model, chunking long texts for efficient processing.
- `app.py`: Defines the FastAPI endpoints and Gradio interface for the application.
- `redis`: Used for caching transcripts and summaries to avoid redundant processing.

The application is containerized using Docker, with separate services for the FastAPI application and Redis cache. The containers are orchestrated using Docker Compose for easy management and deployment.

## Contributing

Pull requests are welcome! For major changes, please open an issue first to discuss what you would like to change.

## License

This project is licensed under the terms of the MIT license. See [LICENSE](LICENSE) for more details.

## Contact

If you have any questions, feel free to open an issue or reach out directly.

Happy summarizing!