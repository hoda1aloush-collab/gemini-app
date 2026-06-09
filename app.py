import streamlit as st
import os
from google import genai

# جلب المفتاح من الإعدادات
api_key = os.environ.get("GEMINI_API_KEY")
client = genai.Client(api_key=api_key)

st.title("Gemini AI Chat")

if "messages" not in st.session_state:
    st.session_state.messages = []

for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

if prompt := st.chat_input("أهلاً! كيف يمكنني مساعدتك؟"):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    with st.chat_message("assistant"):
        response = client.models.generate_content(
            model="gemini-2.0-flash",
            contents=prompt,
        )
        st.markdown(response.text)
    st.session_state.messages.append({"role": "assistant", "content": response.text})
