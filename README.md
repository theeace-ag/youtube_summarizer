<<<<<<< HEAD
# YouTube Video Summarizer & Chat

A Streamlit application that summarizes YouTube videos and allows users to chat about the content using Google's Gemini AI.

## Features

- Extract and summarize YouTube video transcripts
- Generate comprehensive video summaries using Gemini AI
- Interactive chat interface to ask questions about the video content
- Support for multiple languages and auto-generated captions
- Robust error handling and fallback options

## Prerequisites

- Python 3.8 or higher
- A Google API key for Gemini AI
- YouTube videos with available captions

## Installation

1. Clone the repository:
```bash
git clone <your-repository-url>
cd youtube_summarizer
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Create a `.env` file in the root directory and add your Google API key:
```
GOOGLE_API_KEY=your_api_key_here
```

## Local Development

Run the application locally:
```bash
streamlit run youtube_summarizer.py
```

## Deployment

### Deploy to Streamlit Cloud (Recommended)

1. Push your code to GitHub
2. Visit [Streamlit Cloud](https://streamlit.io/cloud)
3. Sign in with your GitHub account
4. Click "New app" and select your repository
5. Add your `GOOGLE_API_KEY` in the Streamlit Cloud secrets management
6. Deploy!

### Alternative Deployment Options

#### Deploy using Docker

1. Build the Docker image:
```bash
docker build -t youtube-summarizer .
```

2. Run the container:
```bash
docker run -p 8501:8501 -e GOOGLE_API_KEY=your_api_key_here youtube-summarizer
```

## Security Notes

- Never commit your `.env` file or expose your API keys
- Use environment variables or secrets management for API keys
- Consider implementing rate limiting for production deployments

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request. 
=======
# youtube_summarizer
>>>>>>> f15e75a7e0969a6d0f99c5286c9aa915f0a514f4
