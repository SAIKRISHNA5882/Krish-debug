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

# Configure Gemini AI - Using the most stable model name
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
    
    try:
        response = requests.post(url, headers=headers, data=payload)
        if response.status_code != 200:
            return f"API Error: {response.status_code}"
        
        results = response.json()
        organic_results = results.get('organic', [])
        if not organic_results:
            return "No results found."
            
        cleaned_text = ""
        for item in organic_results:
            cleaned_text += f"Title: {item.get('title')}\nSnippet: {item.get('snippet')}\nLink: {item.get('link')}\n\n"
        return cleaned_text
    except Exception as e:
        return f"System Error: {str(e)}"

# --- MAIN UI ---
topic = st.text_input("Enter the Topic/News Event:", placeholder="e.g. Latest ISRO launch")

if st.button("Generate Viral Script"):
    if not topic:
        st.warning("Please enter a topic!")
    else:
        with st.spinner("Working..."):
            news_data = get_real_time_news(topic)
            
            if "API Error" in news_data or "No results" in news_data:
                st.error(f"Search failed: {news_data}")
                st.stop()

            prompt = f"""
            You are a viral Instagram Creator. Use this news: {news_data}
            Topic: {topic} | Duration: {duration} | Language: {language} | Style: {style}
            
            STRUCTURE:
            1. HOOK (0-3s): Shocking/Curious opening.
            2. VALUE: Concise, conversational, problem-solution narrative.
            3. CTA: Clear action for viewer.
            
            RULES:
            - Use 'Tanglish' for Telugu + English Mix.
            - Provide a 'PROOFS & LINKS' section at the end with URLs.
            """
            
            try:
                response = model.generate_content(prompt)
                st.success("Done!")
                st.markdown("---")
                st.markdown(response.text)
                st.markdown("---")
            except Exception as e:
                st.error(f"AI Error: {e}")
