import streamlit as st


def render_notification(message, type="success"):
    """
    Renders a notification using native Streamlit alert components.
    Types: success, warning, error, info
    """
    if type == "success":
        st.success(message)
    elif type == "warning":
        st.warning(message)
    elif type == "error":
        st.error(message)
    else:
        st.info(message)
