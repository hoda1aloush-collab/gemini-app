import os
import base64
import streamlit as st
from google import genai
from google.genai import types

# جلب مفتاح Gemini من إعدادات السيرفر
GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY")
client = genai.Client(api_key=GEMINI_API_KEY)

st.set_page_config(
    page_title="Gemini AI",
    page_icon="✨",
    layout="centered",
)

# إعدادات تطبيق الويب التقدمي (PWA) للتثبيت على الموبايل
st.markdown("""
<link rel="manifest" href="/app/static/manifest.json">
<meta name="mobile-web-app-capable" content="yes">
<meta name="apple-mobile-web-app-capable" content="yes">
<meta name="apple-mobile-web-app-status-bar-style" content="black-translucent">
<meta name="apple-mobile-web-app-title" content="Gemini AI">
<link rel="apple-touch-icon" href="/app/static/icon-192x192.png">
<meta name="theme-color" content="#6366f1">
<script>
if ('serviceWorker' in navigator) {
  window.addEventListener('load', function() {
    navigator.serviceWorker.register('/app/static/sw.js', {scope: '/app/static/'})
    .then(function(reg) { console.log('SW registered, scope:', reg.scope); })
    .catch(function(err) { console.warn('SW registration failed:', err); });
  });
}
</script>
""", unsafe_allow_html=True)

st.title("✨ Gemini AI")

# تقسيم التطبيق لتبويبين: شات وصور
tab_chat, tab_image = st.tabs(["💬 Chat", "🎨 Image Generation"])

with tab_chat:
    st.subheader("Chat with Gemini")
    
    if "messages" not in st.session_state:
        st.session_state.messages = []
        
    for msg in st.session_state.messages:
        with st.chat_message(msg["role"]):
            st.markdown(msg["content"])
            
    if prompt := st.chat_input("Type a message..."):
        st.session_state.messages.append({"role": "user", "content": prompt})
        with st.chat_message("user"):
            st.markdown(prompt)
            
        history = [
            types.Content(
                role="user" if m["role"] == "user" else "model",
                parts=[types.Part.from_text(text=m["content"])],
            )
            for m in st.session_state.messages[:-1]
        ]
        
        history.append(
            types.Content(role="user", parts=[types.Part.from_text(text=prompt)])
        )
        
        with st.chat_message("assistant"):
            response_placeholder = st.empty()
            full_response = ""
            try:
                stream = client.models.generate_content_stream(
                    model="gemini-2.5-flash",
                    contents=history,
                    config=types.GenerateContentConfig(max_output_tokens=8192),
                )
                for chunk in stream:
                    if chunk.text:
                        full_response += chunk.text
                        response_placeholder.markdown(full_response + " ▌")
                response_placeholder.markdown(full_response)
            except Exception as e:
                full_response = f"Error: {e}"
                response_placeholder.error(full_response)
                
        st.session_state.messages.append({"role": "assistant", "content": full_response})
        
    if st.session_state.messages:
        if st.button("🗑️ Clear chat", key="clear_chat"):
            st.session_state.messages = []
            st.rerun()

with tab_image:
    st.subheader("Generate Images with Gemini")
    
    image_prompt = st.text_area(
        "Describe the image you want to generate",
        placeholder="A photorealistic cat wearing a tiny astronaut helmet on the moon...",
        height=100,
    )
    
    if st.button("Generate Image", type="primary", disabled=not image_prompt.strip()):
        with st.spinner("Generating image..."):
            try:
                response = client.models.generate_content(
                    model="gemini-2.5-flash-image",
                    contents=image_prompt,
                    config=types.GenerateContentConfig(
                        response_modalities=["IMAGE", "TEXT"]
                    ),
                )
                image_shown = False
                for part in response.candidates[0].content.parts:
                    if part.inline_data is not None:
                        image_bytes = base64.b64decode(part.inline_data.data)
                        st.image(image_bytes, use_container_width=True)
                        st.download_button(
                            label="📥 Download Image",
                            data=image_bytes,
                            file_name="gemini_image.png",
                            mime="image/png"
                        )
                        image_shown = True
                if not image_shown:
                    st.warning("No image data found in response.")
            except Exception as e:
                st.error(f"Error generating image: {e}")
