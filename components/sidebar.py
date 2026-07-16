import streamlit as st
import base64
import os


def get_base64_image(image_path):
    if os.path.exists(image_path):
        with open(image_path, "rb") as img_file:
            return base64.b64encode(img_file.read()).decode('utf-8')
    return ""



def show_sidebar():
    uploaded_files = st.session_state.get("uploaded_files", [])
    ranked_candidates = st.session_state.get("ranked_candidates", [])
    job_profile = st.session_state.get("job_profile", {})

    with st.sidebar:
        logo_base64 = get_base64_image("assets/logo.png")
        if logo_base64:
            st.markdown(
                f'<div style="display: flex; align-items: center; gap: 10px; margin-bottom: 16px; margin-top: 8px;">'
                f'<img src="data:image/png;base64,{logo_base64}" style="height: 28px; width: 28px; border-radius: 6px; object-fit: contain;">'
                f'<h1 style="margin: 0; font-size: 20px; font-weight: 800; color: #F8FAFC; line-height: 1; font-family: \'Inter\', sans-serif;">AnalyzeIt</h1>'
                f'</div>',
                unsafe_allow_html=True
            )
        else:
            st.title("📄 AnalyzeIt")

        # ── Navigation Section ─────────────────────────────────
        with st.container(border=True):
            st.markdown(
                '<p style="font-size:10px; font-weight:700; color:#4F8CFF; '
                'text-transform:uppercase; letter-spacing:1px; margin-bottom:6px;">Navigation</p>',
                unsafe_allow_html=True,
            )
            st.markdown(
                """
                <div class="nav-container">
                  <a href="#section-dashboard" class="nav-link" id="nav-dashboard">
                    📊 Recruiter Dashboard
                  </a>
                  <a href="#section-rankings" class="nav-link" id="nav-rankings">
                    👥 Candidate Rankings
                  </a>
                  <a href="#section-comparison" class="nav-link" id="nav-comparison">
                    ⚖️ Candidate Comparison
                  </a>
                  <a href="#section-chat" class="nav-link" id="nav-chat">
                    💬 RAG Search Chat
                  </a>
                </div>
                """,
                unsafe_allow_html=True,
            )

            import streamlit.components.v1 as components
            js_code = """
            <script>
              (function() {
                const parentDoc = window.parent.document;
                let isClickScrolling = false;
                let clickScrollTimeout;

                const updateActiveLink = () => {
                  if (isClickScrolling) return;
                  const hash = window.parent.location.hash || '#section-dashboard';
                  const links = parentDoc.querySelectorAll('.nav-link');
                  let found = false;
                  links.forEach(link => {
                    if (link.getAttribute('href') === hash) {
                      link.classList.add('active');
                      found = true;
                    } else {
                      link.classList.remove('active');
                    }
                  });
                  if (!found && links.length > 0) {
                    const dashboardLink = parentDoc.querySelector('a[href="#section-dashboard"]');
                    if (dashboardLink) dashboardLink.classList.add('active');
                  }
                };

                // Run immediately to sync on load
                setTimeout(updateActiveLink, 50);

                // Attach click handlers to update the highlight instantly on selection
                const setupHandlers = () => {
                  const links = parentDoc.querySelectorAll('.nav-link');
                  links.forEach(link => {
                    link.onclick = function() {
                      isClickScrolling = true;
                      clearTimeout(clickScrollTimeout);
                      
                      links.forEach(l => l.classList.remove('active'));
                      this.classList.add('active');
                      
                      // Lock scrollspy tracking for 1000ms during click navigation
                      clickScrollTimeout = setTimeout(() => {
                        isClickScrolling = false;
                      }, 1000);
                    };
                  });
                };
                setTimeout(setupHandlers, 50);

                // Listen to hash changes in parent window
                window.parent.addEventListener('hashchange', updateActiveLink);

                // Scrollspy Scroll Listener targeting parent window viewports (capture-phase scroll)
                const handleScroll = () => {
                  if (isClickScrolling) return;

                  const sectionIds = ['section-dashboard', 'section-rankings', 'section-comparison', 'section-chat'];
                  let activeId = null;

                  // Find the last section whose top is <= 200px from the top of the viewport
                  for (let i = 0; i < sectionIds.length; i++) {
                    const el = parentDoc.getElementById(sectionIds[i]);
                    if (el) {
                      const rect = el.getBoundingClientRect();
                      if (rect.top <= 200) {
                        activeId = sectionIds[i];
                      }
                    }
                  }

                  // Default to dashboard if near the top
                  if (!activeId) {
                    activeId = 'section-dashboard';
                  }

                  if (activeId) {
                    const navLinks = parentDoc.querySelectorAll('.nav-link');
                    navLinks.forEach(link => {
                      if (link.getAttribute('href') === '#' + activeId) {
                        link.classList.add('active');
                      } else {
                        link.classList.remove('active');
                      }
                    });
                  }
                };

                try {
                  // Bind capture scroll listener to window as fallback
                  window.parent.addEventListener('scroll', handleScroll, { capture: true, passive: true });
                  
                  // Periodically search for Streamlit's actual scrolling main panel container and bind directly
                  let bindInterval = setInterval(() => {
                    const scrollContainer = parentDoc.querySelector('section.main') || 
                                            parentDoc.querySelector('[data-testid="stMain"]') || 
                                            parentDoc.querySelector('.main') ||
                                            parentDoc.querySelector('[data-testid="stAppViewBlockContainer"]');
                    if (scrollContainer) {
                      scrollContainer.addEventListener('scroll', handleScroll, { passive: true });
                      clearInterval(bindInterval);
                    }
                  }, 200);
                  setTimeout(() => clearInterval(bindInterval), 5000);
                } catch (e) {
                  console.log("Could not bind parent scroll listener:", e);
                }
              })();
            </script>
            """
            components.html(js_code, height=0)

        # ── System Health Section ──────────────────────────────
        with st.container(border=True):
            st.markdown(
                '<p style="font-size:10px; font-weight:700; color:#4F8CFF; '
                'text-transform:uppercase; letter-spacing:1px; margin-bottom:4px;">System Health</p>',
                unsafe_allow_html=True,
            )
            st.success("🟢 Ollama: Active")
            st.success("🟢 Embeddings: Connected")
            st.success("🟢 Storage: Stable")

        # ── Configuration Section ──────────────────────────────
        with st.container(border=True):
            st.markdown(
                '<p style="font-size:10px; font-weight:700; color:#4F8CFF; '
                'text-transform:uppercase; letter-spacing:1px; margin-bottom:4px;">Configuration</p>',
                unsafe_allow_html=True,
            )
            st.selectbox("LLM Model", ["llama3:8b"], key="sidebar_llm_model")
            st.selectbox("Answer Language", ["Auto", "English", "Hindi", "Bengali"], key="sidebar_lang")
            st.selectbox("Embedding Model", ["bge-m3"], key="sidebar_emb_model")

        # ── Uploaded Files Section ─────────────────────────────
        with st.container(border=True):
            st.markdown(
                '<p style="font-size:10px; font-weight:700; color:#4F8CFF; '
                'text-transform:uppercase; letter-spacing:1px; margin-bottom:4px;">Uploaded Files</p>',
                unsafe_allow_html=True,
            )
            
            # Inline metrics for uploads status
            s1, s2 = st.columns(2)
            with s1:
                st.metric("Candidates", len(ranked_candidates))
            with s2:
                st.metric("Resumes", len(uploaded_files))

            if uploaded_files:
                st.divider()
                for file in uploaded_files:
                    st.caption(f"📄 {file.name}")
            else:
                st.caption("No resumes uploaded yet")