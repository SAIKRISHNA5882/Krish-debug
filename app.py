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

# --- API KEYS ---
try:
    GEMINI_API_KEY = st.secrets["GEMINI_API_KEY"]
    SERPER_API_KEY = st.secrets["SERPER_API_KEY"]
except:
    st.error("API Keys not found! Please add them to Streamlit Secrets.")
    st.stop()

# Configure Gemini AI - UPDATED TO 1.5 FLASH
genai.configure(api_key=GEMINI_API_KEY)
model = genai.GenerativeModel('gemini-1.5-flash')

# --- REAL-TIME SEARCH FUNCTION (FIXED) ---
def get_real_time_news(query):
    url = "https://google.serper.dev/search"
    payload = json.dumps({"q": query})
    headers = {
        'X-API-KEY': SERPER_API_KEY,
        'Content-Type': 'application/json'
    }
    response = requests.request("POST", url, headers=headers, data=payload)
    results = response.json()
    
    # This part cleans the news so the AI doesn't crash
    organic_results = results.get('organic', [])
    cleaned_text = ""
    for item in organic_results:
        cleaned_text += f"Title: {item.get('title')}\nSnippet: {item.get('snippet')}\nLink: {item.get('link')}\n\n"
    
    return cleaned_text

# --- MAIN UI ---
topic = st.text_input("Enter the Topic/News Event:", placeholder="e.g. Latest ISRO launch or Indian Political News")

if st.button("Generate Viral Script"):
    if not topic:
        st.warning("Please enter a topic first!")
    else:
        with st.spinner("Searching real-time news and writing your viral script..."):
            try:
                # 1. Fetch cleaned real-time data
                cleaned_news = get_real_time_news(topic)
                
                if not cleaned_news:
                    st.error("No news found for this topic. Try a different keyword.")
                    st.stop()

                # 2. The Prompt
                prompt = f"""
                You are a viral Instagram Content Creator and News Expert. 
                Use the following real-time search data: 
                {cleaned_news}
                
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
                - Provide a separate section titled 'PROOFS & IMAGE LINKS' containing the URLs from the search data.
                - Ensure the script is video-ready and flows naturally.
                """
                
                # 3. Generate the content
                response = model.generate_content(prompt)
                
                # 4. Display the result
                st.success("Done! Here is your viral script:")
                st.markdown("---")
                st.markdown(response.text)
                st.markdown("---")
                
            except Exception as e:
                st.error(f"An error occurred: {e}")
