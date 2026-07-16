import streamlit as st
from datetime import datetime
import subprocess


def show_chat(rag):
    """
    Renders the RAG conversation using native st.chat_message() components.
    st.chat_input() handles the input bar.
    """
    st.markdown('<div id="section-chat"></div>', unsafe_allow_html=True)
    st.markdown("## 💬 Conversation")

    embeddings_generated = st.session_state.get("embeddings_generated", False)
    chat_history = st.session_state.get("chat_history", [])

    chat_container = st.container(height=450)

    with chat_container:
        if len(chat_history) == 0:
            if not embeddings_generated:
                st.info(
                    """
                    👋 **Welcome to AnalyzeIt**

                    To start querying candidates, please **upload resume PDFs** in the panel above.
                    Once they are indexed and embeddings are generated, this recruiter AI chat panel will unlock!
                    """
                )
            else:
                st.info(
                    """
                    👋 **Welcome to AnalyzeIt**

                    Upload one or more resume PDFs and start asking questions.

                    ### Example Questions

                    - Who knows Python?
                    - Which student has the highest CGPA?
                    - Compare Rahul Sharma and Arjun Patel.
                    - कौन Machine Learning जानता है?
                    - রাহুল শর্মার ১০ম শ্রেণির নম্বর কত?
                    """
                )
        else:
            for idx, item in enumerate(chat_history):
                role = item[0]
                message = item[1]
                timestamp = item[2] if len(item) > 2 else ""

                if role == "user":
                    with st.chat_message("user"):
                        st.markdown(message)
                        if timestamp:
                            st.caption(f"{timestamp} • Recruiter")
                else:
                    with st.chat_message("assistant"):
                        st.markdown(message)
                        if timestamp:
                            st.caption(f"{timestamp} • Assistant")
                        if st.button(
                            "📋 Copy Response Text",
                            key=f"copy_msg_{idx}",
                            help="Copy this response to clipboard",
                        ):
                            try:
                                subprocess.run(
                                    "clip",
                                    input=message.encode("utf-8"),
                                    check=True,
                                )
                                st.toast("Copied response to clipboard!")
                            except Exception:
                                st.toast("Failed to copy response.")

            # Retrieved documents after last assistant message
            if chat_history and chat_history[-1][0] == "assistant":
                last_matches = st.session_state.get("last_matches", [])
                if last_matches:
                    st.markdown("### 📄 Retrieved Documents")
                    medals = ["🥇", "🥈", "🥉"]
                    for i, (filename, score) in enumerate(last_matches):
                        match_score = round(score * 100)
                        st.info(
                            f"### {medals[i]} {filename}\n"
                            f"🎯 **Match Score:** **{match_score}%**\n"
                            f"🧠 **Embedding Model:** BGE-M3"
                        )

    # Chat Input
    chat_disabled = not embeddings_generated

    question = st.chat_input(
        "Ask anything about the uploaded resumes...",
        disabled=chat_disabled,
    )

    if question:
        user_time = datetime.now().strftime("%I:%M %p")
        st.session_state.chat_history.append(("user", question, user_time))

        with chat_container:
            with st.chat_message("user"):
                st.markdown(question)
                st.caption(f"{user_time} • Recruiter")

            with st.chat_message("assistant"):
                with st.spinner("Thinking..."):
                    if not embeddings_generated:
                        answer = "⚠ Please upload resumes first."
                        matches = []
                    else:
                        result = rag.ask_question(question)
                        answer = result["answer"]
                        matches = result["matches"]
                st.markdown(answer)

        assistant_time = datetime.now().strftime("%I:%M %p")
        st.session_state.chat_history.append(("assistant", answer, assistant_time))
        st.session_state.last_matches = matches
        st.rerun()
