import os
import time

import requests
import streamlit as st

st.set_page_config(
    page_title="Autonomous Research Agent",
    page_icon="🔬",
    layout="wide",
    initial_sidebar_state="expanded",
)

# API Configuration
API_URL = os.getenv("API_URL", "http://localhost:8000").rstrip("/")

st.title("🔬 Autonomous Research Agent")
st.caption(
    "Powered by LangGraph multi-agent orchestration, Redis short-term memory, and Qdrant vector retrieval."
)

# Sidebar configuration
with st.sidebar:
    st.header("⚙️ System Status")
    try:
        health_resp = requests.get(f"{API_URL}/", timeout=3)
        if health_resp.status_code == 200:
            st.success("API Backend: Connected")
        else:
            st.error(f"API Backend Error: {health_resp.status_code}")
    except Exception:
        st.error("API Backend: Unreachable")
        st.info(f"Target URL: {API_URL}")

    st.markdown("---")
    st.markdown("### 💡 Example Queries")
    example_queries = [
        "Recent breakthroughs in room-temperature superconductivity",
        "Advancements in quantum computing hardware and error correction in 2026",
        "Applications of multi-agent AI systems in scientific discovery",
    ]
    for eq in example_queries:
        if st.button(eq, use_container_width=True):
            st.session_state["query_input"] = eq

query = st.text_input(
    "Enter research topic or query:",
    value=st.session_state.get("query_input", ""),
    placeholder="e.g. Current state of nuclear fusion energy commercialization",
)

col1, col2 = st.columns([1, 4])
with col1:
    submit_button = st.button(
        "🚀 Run Research", type="primary", use_container_width=True
    )

if submit_button:
    if not query.strip():
        st.warning("Please enter a valid research query.")
    else:
        st.info("Submitting task to API backend...")
        try:
            res = requests.post(
                f"{API_URL}/api/v1/research", json={"query": query.strip()}, timeout=10
            )
            if res.status_code == 200:
                task_data = res.json()
                task_id = task_data.get("task_id")
                st.success(f"Task queued successfully! Task ID: `{task_id}`")

                # Progress tracking UI
                progress_bar = st.progress(0)
                status_text = st.empty()

                completed = False
                attempts = 0
                max_attempts = 120  # up to 2 minutes polling

                while attempts < max_attempts and not completed:
                    time.sleep(2)
                    attempts += 1

                    try:
                        status_res = requests.get(
                            f"{API_URL}/api/v1/status/{task_id}", timeout=5
                        )
                        if status_res.status_code == 200:
                            s_data = status_res.json()
                            status = s_data.get("status", "running")
                            progress = float(s_data.get("progress", 0.1))

                            progress_bar.progress(int(progress * 100))
                            status_text.text(
                                f"Status: {status.upper()} (Step {attempts})"
                            )

                            if status == "completed":
                                completed = True
                                progress_bar.progress(100)
                                status_text.text("Status: COMPLETED")
                                break
                            elif status == "failed":
                                error_msg = s_data.get("error", "Unknown task failure.")
                                st.error(f"Research task failed: {error_msg}")
                                break
                    except Exception as poll_err:
                        status_text.text(f"Polling update... ({poll_err})")

                if completed:
                    st.markdown("---")
                    st.header("📄 Synthesized Research Report")

                    report_res = requests.get(
                        f"{API_URL}/api/v1/report/{task_id}", timeout=10
                    )
                    if report_res.status_code == 200:
                        report_data = report_res.json()
                        report_markdown = report_data.get("report", "")
                        citations = report_data.get("citations", [])

                        st.markdown(report_markdown)

                        if citations:
                            with st.expander(
                                "📚 Deduplicated References & Citations", expanded=False
                            ):
                                for idx, cit in enumerate(citations, 1):
                                    st.markdown(
                                        f"**[{idx}] [{cit.get('title', 'Reference')}]({cit.get('url', '#')})** (Source: {cit.get('source', 'web')})"
                                    )
                    else:
                        st.error("Failed to retrieve final report.")
            else:
                st.error(f"Failed to submit task. HTTP Status: {res.status_code}")
        except Exception as err:
            st.error(f"Error communicating with API server: {err}")
