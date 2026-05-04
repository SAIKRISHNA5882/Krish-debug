import streamlit as st
import google.generativeai as genai
import requests
import json

# --- PAGE CONFIGURATION ---
st.set_page_config(page_title="Viral Reel Script Generator", page_icon="📱")

st.title("🚀 Viral Reel Script Generator")
st.markdown("Generate high-engagement scripts based on real-time news.")

# --- SIDEBAR SETTINGS ---
with st.sidebar:
    st.header("Settings")
    language = st.selectbox("Select Language", 
                            ["Telugu + English Mix", "Telugu", "Hindi", "English"])
    
    duration = st.selectbox("Video Duration", 
                            ["30 Seconds", "60 Seconds", "90 Seconds", "120 Seconds", "180 Seconds"])
    
    style = "Slightly formal news presenter, conversational, engaging, and viral."

# --- API KEYS (Handled via Streamlit Secrets) ---
# We use st.secrets so your keys stay hidden from the public
try:
    GEMINI_API_KEY = st.secrets["GEMINI_API_KEY"]
    SERPER_API_KEY = st.secrets["SERPER_API_KEY"]
except:
    st.error("API Keys not found! Please add them to Streamlit Secrets.")
    st.stop()

# Configure Gemini AI
genai.configure(api_key=GEMINI_API_KEY)
model = genai.GenerativeModel('gemini-pro')

# --- REAL-TIME SEARCH FUNCTION ---
def get_real_time_news(query):
    url = "https://google.serper.dev/search"
    payload = json.dumps({"q": query})
    headers = {
        'X-API-KEY': SERPER_API_KEY,
        'Content-Type': 'application/json'
    }
    response = requests.request("POST", url, headers=headers, data=payload)
    return response.text

# --- MAIN UI ---
topic = st.text_input("Enter the Topic/News Event:", placeholder="e.g. Latest ISRO launch or Indian Political News")

if st.button("Generate Viral Script"):
    if not topic:
        st.warning("Please enter a topic first!")
    else:
        with st.spinner("Searching real-time news and writing your viral script..."):
            # 1. Fetch real-time data
            raw_news = get_real_time_news(topic)
            
            # 2. The Prompt (The "Instructions" for the AI)
            prompt = f"""
            You are a viral Instagram Content Creator and News Expert. 
            Use the following real-time search data: {raw_news}
            
            Create a video script for the topic: {topic}
            Target Duration: {duration}
            Language: {language}
            Style: {style}
            
            STRICT STRUCTURE:
            1. **THE HOOK (0-3 seconds):** Create a pattern-interrupting, shocking, or high-curiosity opening. Stop the scroll.
            2. **THE VALUE (The Body):** Explain the news concisely. Use a problem-solution narrative. No jargon. Simple, conversational language.
            3. **THE CTA (Call to Action):** A clear, engaging instruction for the viewer (e.g., 'Comment your thoughts below').
            
            ADDITIONAL REQUIREMENTS:
            - If language is 'Telugu + English Mix', write it in natural 'Tanglish' (the way young people speak in cities).
            - Provide a separate section titled 'PROOFS & IMAGE LINKS' containing the URLs from the search data that the user can use for b-roll or evidence.
            - Ensure the script is video-ready and flows naturally.
            """
            
            # 3. Generate the content
            response = model.generate_content(prompt)
            
            # 4. Display the result
            st.success("Done! Here is your viral script:")
            st.markdown("---")
            st.markdown(response.text)
            st.markdown("---")

