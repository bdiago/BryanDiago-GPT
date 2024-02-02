import streamlit as st
import time


def converse(chatbot):
    if "messages" not in st.session_state:
        st.session_state.messages = [{"role": "assistant", "content": chatbot.greet()}]

    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

    if prompt := st.chat_input("converse here"):
        message_placeholder = st.empty()
        st.session_state.messages.append({"role": "user", "content": prompt})
        with st.chat_message("user"):
            st.markdown(prompt)

        with st.spinner("Bot is responding..."):  # Display spinner while bot is processing
            with st.chat_message("assistant"):
                message_placeholder = st.empty()
                full_response = ""
                for response in chatbot.step(prompt):
                    full_response += (response or "")
                    message_placeholder.markdown(full_response + "▌")
                    time.sleep(0.005)  # Add a small delay to simulate streaming effect
                message_placeholder.markdown(full_response)
           

        st.session_state.messages.append({"role": "assistant", "content": full_response})



class Streamlit:
    def __init__(self, chatbot):
        self.chatbot = chatbot

    def run(self):
        converse(self.chatbot)