import streamlit as st
import google.generativeai as genai
from youtube_transcript_api import YouTubeTranscriptApi
from pytube import YouTube
from datetime import datetime
import os
from dotenv import load_dotenv
import time
import re
import requests

# Load environment variables
load_dotenv()

# Configure Gemini API
GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY", "AIzaSyCTGgc5qmllfRQ7E75cjxu7kH9tVjFuXnc")

try:
    genai.configure(api_key=GOOGLE_API_KEY)
    model = genai.GenerativeModel('gemini-2.0-flash')
except Exception as e:
    st.error("Error initializing Gemini AI. Please check your API key.")
    st.stop()

def extract_video_id(url):
    """Extract YouTube video ID from URL."""
    try:
        if not url:
            return None
        if "youtu.be" in url:
            return url.split("/")[-1].split("?")[0]
        elif "youtube.com" in url:
            return url.split("v=")[1].split("&")[0]
        return url
    except Exception:
        return None

def get_video_info(url):
    """Get video information using pytube with retries and fallback."""
    if not url:
        st.error("Please enter a valid YouTube URL")
        return None
        
    max_retries = 3
    retry_count = 0
    
    while retry_count < max_retries:
        try:
            yt = YouTube(url)
            # Add a small delay to allow video info to load
            time.sleep(2)  # Increased delay
            
            # Try to access properties with error handling
            try:
                title = yt.title
            except:
                # Fallback: Try to get title from HTML
                try:
                    video_id = extract_video_id(url)
                    response = requests.get(f"https://www.youtube.com/watch?v={video_id}")
                    title_match = re.search(r'<title>(.*?)</title>', response.text)
                    title = title_match.group(1).replace(' - YouTube', '') if title_match else "Title not available"
                except:
                    title = "Title not available"
            
            try:
                author = yt.author
            except:
                author = "Channel not available"
            
            try:
                length = yt.length
                length_str = f"{length // 60} min, {length % 60} sec"
            except:
                length_str = "Length not available"
            
            try:
                date = yt.publish_date.strftime("%d/%m/%Y") if yt.publish_date else "Not available"
            except:
                date = "Not available"
            
            return {
                'title': title,
                'channel': author,
                'length': length_str,
                'date': date
            }
            
        except Exception as e:
            retry_count += 1
            if retry_count == max_retries:
                st.warning(f"Warning: Some video information might be incomplete. Error: {str(e)}")
                # Return basic info even if full info fetch fails
                return {
                    'title': "Title not available",
                    'channel': "Channel not available",
                    'length': "Length not available",
                    'date': "Not available"
                }
            time.sleep(1)  # Wait before retrying

def get_transcript(video_id):
    """Get video transcript with fallback options."""
    if not video_id:
        st.error("Invalid video ID")
        return None
        
    try:
        # Try different language options if available
        try:
            transcript = YouTubeTranscriptApi.get_transcript(video_id)
        except:
            # Try to get available transcript languages
            transcript_list = YouTubeTranscriptApi.list_transcripts(video_id)
            
            # Try to get English transcript first
            try:
                transcript = transcript_list.find_transcript(['en']).fetch()
            except:
                # If no English, get the first available transcript
                try:
                    transcript = transcript_list.find_transcript(['en-US', 'en-GB']).fetch()
                except:
                    # Get auto-generated transcript if available
                    available_transcripts = transcript_list.find_manually_created_transcript()
                    transcript = available_transcripts.fetch()
        
        return " ".join([entry['text'] for entry in transcript])
    except Exception as e:
        st.error(f"Could not fetch video transcript. Error: {str(e)}")
        st.info("This might be because:\n1. The video has no captions available\n2. Captions are disabled for this video\n3. The video might be age-restricted or private")
        return None

def generate_summary(video_info, transcript):
    """Generate video summary using Gemini AI."""
    if not video_info or not transcript:
        return None
        
    prompt = f"""
    Analyze this YouTube video transcript and provide a detailed summary in the following format:

    Title: {video_info['title']}
    Channel: {video_info['channel']}
    Upload Date: {video_info['date']}
    Video Length: {video_info['length']}
    
    Please determine the appropriate Category and Target Audience based on the content.
    
    Provide a comprehensive summary including:
    1. Main topic and key discussion points
    2. Key takeaways with timestamps
    3. Detailed breakdown of the content
    4. Final thoughts and recommendations
    
    Transcript: {transcript}
    """
    
    try:
        response = model.generate_content(prompt)
        return response.text
    except Exception as e:
        st.error(f"Error generating summary: {str(e)}")
        return None

def chat_with_ai(question, context):
    """Chat with AI about the video content."""
    if not question or not context:
        return None
        
    prompt = f"""
    Based on the following video summary, please answer this question: {question}
    
    Context: {context}
    """
    try:
        response = model.generate_content(prompt)
        return response.text
    except Exception as e:
        st.error(f"Error generating response: {str(e)}")
        return None

# Streamlit UI
st.set_page_config(page_title="YouTube Video Summarizer & Chat", page_icon="🎥")
st.title("🎥 YouTube Video Summarizer & Chat")

# Add instructions
st.markdown("""
### How to use:
1. Enter a YouTube video URL below
2. Wait for the summary to generate
3. Ask questions about the video content in the chat interface
""")

# Input URL with placeholder
url = st.text_input("Enter YouTube Video URL:", placeholder="https://www.youtube.com/watch?v=...")

if url:
    with st.spinner("Fetching video information..."):
        video_id = extract_video_id(url)
        if not video_id:
            st.error("Invalid YouTube URL. Please check the URL and try again.")
            st.stop()
            
        video_info = get_video_info(url)
        
        if video_info:
            with st.spinner("Generating transcript..."):
                transcript = get_transcript(video_id)
            
            if transcript:
                with st.spinner("Generating summary..."):
                    summary = generate_summary(video_info, transcript)
                
                if summary:
                    st.markdown("## Video Summary")
                    st.markdown(summary)
                    
                    # Chat interface
                    st.markdown("## Chat about the Video")
                    st.markdown("Ask questions about the video content:")
                    
                    # Initialize chat history
                    if 'chat_history' not in st.session_state:
                        st.session_state.chat_history = []
                    
                    # Create columns for input and button
                    col1, col2 = st.columns([4, 1])
                    with col1:
                        question = st.text_input("Your question:", key="question_input")
                    with col2:
                        ask_button = st.button("Ask", use_container_width=True)
                    
                    if ask_button and question:
                        with st.spinner("Generating response..."):
                            response = chat_with_ai(question, summary)
                            if response:
                                st.session_state.chat_history.append(("You", question))
                                st.session_state.chat_history.append(("AI", response))
                    
                    # Display chat history
                    if st.session_state.chat_history:
                        st.markdown("### Chat History")
                        for role, message in st.session_state.chat_history:
                            if role == "You":
                                st.markdown(f"**You:** {message}")
                            else:
                                st.markdown(f"**AI:** {message}") 