import streamlit as st
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
            return f"Search Error: {response.status_code}"
        
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

# --- DIRECT GOOGLE AI CALL (THE PERMANENT FIX) ---
def generate_ai_script(prompt):
    # We call the API directly via URL to avoid library version errors
    url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent?key={GEMINI_API_KEY}"
    
    headers = {'Content-Type': 'application/json'}
    payload = {
        "contents": [{
            "parts": [{"text": prompt}]
        }]
    }
    
    try:
        response = requests.post(url, headers=headers, json=payload)
        if response.status_code != 200:
            return f"AI Error: {response.status_code} - {response.text}"
        
        result_json = response.json()
        # Extract the text from the Google AI response structure
        text = result_json['candidates'][0]['content']['parts'][0]['text']
        return text
    except Exception as e:
        return f"AI Connection Error: {str(e)}"

# --- MAIN UI ---
topic = st.text_input("Enter the Topic/News Event:", placeholder="e.g. Latest ISRO launch")

if st.button("Generate Viral Script"):
    if not topic:
        st.warning("Please enter a topic!")
    else:
        with st.spinner("Searching news and writing your script..."):
            # 1. Get News
            news_data = get_real_time_news(topic)
            
            if "Search Error" in news_data or "No results" in news_data:
                st.error(f"Search failed: {news_data}")
                st.stop()

            # 2. Build the Prompt
            prompt = f"""
            You are a viral Instagram Creator and News Expert. 
            Use the following real-time news data: 
            {news_data}
            
            Create a video script for the topic: {topic}
            Target Duration: {duration}
            Language: {language}
            Style: {style}
            
            STRICT STRUCTURE:
            1. **THE HOOK (0-3 seconds):** Create a pattern-interrupting, shocking, or high-curiosity opening. Stop the scroll.
            2. **THE VALUE (The Body):** Explain the news concisely. Use a problem-solution narrative. No jargon. Simple, conversational language.
            3. **THE CTA (Call to Action):** A clear, engaging instruction for the viewer.
            
            RULES:
            - If language is 'Telugu + English Mix', write it in natural 'Tanglish' (the way young people speak in cities).
            - Provide a separate section titled 'PROOFS & IMAGE LINKS' containing the URLs from the search data.
            - Ensure the script is video-ready and flows naturally.
            """
            
            # 3. Generate using the Direct Call method
            final_script = generate_ai_script(prompt)
            
            if "AI Error" in final_script or "AI Connection Error" in final_script:
                st.error(final_script)
            else:
                st.success("Done! Here is your viral script:")
                st.markdown("---")
                st.markdown(final_script)
                st.markdown("---")
