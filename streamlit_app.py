import streamlit as st
import requests
import websocket
import json

API_URL = "http://localhost:8000"
WS_URL = "ws://localhost:8000/ws/chat"

st.set_page_config(
    page_title="Interview Transcript Agent",
    page_icon="🎙️",
    layout="wide"
)

if "messages" not in st.session_state:
    st.session_state.messages = []


if "summary" not in st.session_state:
    st.session_state.summary = None

if st.session_state.summary is None:

    try:

        response = requests.get(
            f"{API_URL}/summary",
            timeout=300
        )

        response.raise_for_status()

        data = response.json()

        st.session_state.summary = data["summary"]

    except Exception as e:

        st.error(
            f"Could not load transcript summary: {e}"
        )

        st.stop()

st.title("🎙️ Interview Transcript Agent")

st.caption(
    "AI-powered analysis and retrieval across interview transcripts"
)


with st.expander(
    "📊 Initial Transcript Analysis",
    expanded=True
):

    st.markdown(
        st.session_state.summary
    )


st.divider()


st.subheader("💬 Ask Questions")

for message in st.session_state.messages:

    with st.chat_message(message["role"]):

        st.markdown(
            message["content"]
        )

user_message = st.chat_input(
    "Ask something about the interviews..."
)


if user_message:

    st.session_state.messages.append({
        "role": "user",
        "content": user_message
    })

    with st.chat_message("user"):

        st.markdown(user_message)

    with st.chat_message("assistant"):

        placeholder = st.empty()

        full_response = ""

        try:

            ws = websocket.create_connection(
                WS_URL,
                timeout=300
            )

            history = st.session_state.messages[:-1]

            payload = {
                "message": user_message,
                "history": history
            }

            ws.send(
                json.dumps(payload)
            )

            while True:

                raw_message = ws.recv()

                if not raw_message:
                    break

                data = json.loads(
                    raw_message
                )

                message_type = data.get("type")

                if message_type == "start":

                    continue

                elif message_type == "token":

                    token = data.get(
                        "content",
                        ""
                    )

                    full_response += token

                    placeholder.markdown(
                        full_response + "▌"
                    )


                elif message_type == "done":

                    placeholder.markdown(
                        full_response
                    )

                    break

                elif message_type == "error":

                    st.error(
                        data.get(
                            "content",
                            "Unknown error"
                        )
                    )

                    break


            ws.close()

            if full_response:

                st.session_state.messages.append({
                    "role": "assistant",
                    "content": full_response
                })

        except Exception as e:

            st.error(
                f"WebSocket error: {e}"
            )