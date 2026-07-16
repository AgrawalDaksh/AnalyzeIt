import streamlit as st
import datetime
import base64
import os


def get_base64_image(image_path):
    if os.path.exists(image_path):
        with open(image_path, "rb") as img_file:
            return base64.b64encode(img_file.read()).decode('utf-8')
    return ""



def show_header():
    now = datetime.datetime.now().strftime("%B %d, %Y | %I:%M %p")

    # Inject header styles for the inline components (e.g. badges or custom text)
    st.markdown("""
    <style>
    .header-badge-container {
        display: flex;
        flex-direction: column;
        align-items: flex-end;
        gap: 6px;
        padding-top: 4px;
    }
    .header-badge {
        display: inline-block;
        font-size: 12px;
        font-weight: 600;
        background: rgba(255,255,255,0.08);
        color: rgba(255,255,255,0.9) !important;
        padding: 6px 14px;
        border-radius: 20px;
        border: 1px solid rgba(255,255,255,0.15);
    }
    .header-badge-green {
        background: rgba(34,197,94,0.15) !important;
        color: #4ade80 !important;
        border: 1px solid rgba(34,197,94,0.3) !important;
    }
    .header-dot {
        display: inline-block;
        width: 7px;
        height: 7px;
        background: #4ade80;
        border-radius: 50%;
        margin-right: 5px;
        box-shadow: 0 0 8px rgba(74,222,128,0.9);
    }
    </style>
    """, unsafe_allow_html=True)

    with st.container(border=True):
        left_col, right_col = st.columns([7, 3])

        with left_col:
            logo_base64 = get_base64_image("assets/logo.png")
            if logo_base64:
                st.markdown(
                    f'<div style="display: flex; align-items: center; gap: 12px; margin-bottom: 6px; margin-top: 4px;">'
                    f'<img src="data:image/png;base64,{logo_base64}" style="height: 38px; width: 38px; border-radius: 6px; object-fit: contain;">'
                    f'<h1 style="margin: 0; font-size: 24px; font-weight: 800; color: #F8FAFC; line-height: 1; font-family: \'Inter\', sans-serif;">AnalyzeIt</h1>'
                    f'</div>',
                    unsafe_allow_html=True
                )
            else:
                st.title("📄 AnalyzeIt")
            st.caption("AI-Powered Resume Analysis & Recruitment Assistant")

        with right_col:
            st.markdown(
                f'<div class="header-badge-container">'
                f'<span class="header-badge">🕒 {now}</span>'
                f'<span class="header-badge header-badge-green">'
                f'<span class="header-dot"></span>Ollama Active</span>'
                f'</div>',
                unsafe_allow_html=True
            )