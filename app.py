from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware

from graph import graph, session_summary

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/summary")
async def get_summary():

    return {
        "summary": session_summary
    }


@app.websocket("/ws/chat")
async def websocket_chat(websocket: WebSocket):

    await websocket.accept()

    print("WebSocket connected")

    try:

        while True:

            data = await websocket.receive_json()

            user_message = data.get("message", "")
            history = data.get("history", [])

            if not user_message.strip():
                continue

            messages = []

            for msg in history:

                messages.append({
                    "role": msg["role"],
                    "content": msg["content"]
                })

            messages.append({
                "role": "user",
                "content": user_message
            })

            print(f"User: {user_message}")

            await websocket.send_json({
                "type": "start"
            })

            try:

                async for event in graph.astream(
                    {
                        "messages": messages
                    },
                    stream_mode="messages",
                ):

                    message_chunk, metadata = event

                    if metadata.get("langgraph_node") != "agent":
                        continue

                    content = message_chunk.content

                    if not content:
                        continue

                    if isinstance(content, str):

                        await websocket.send_json({
                            "type": "token",
                            "content": content
                        })

                await websocket.send_json({
                    "type": "done"
                })

                print("Graph completed")

            except WebSocketDisconnect:

                print("Client disconnected while streaming")
                break

            except Exception as e:

                print("Graph error:", repr(e))

                try:

                    await websocket.send_json({
                        "type": "error",
                        "content": str(e)
                    })

                except (WebSocketDisconnect, RuntimeError):

                    break

    except WebSocketDisconnect:

        print("WebSocket disconnected")

    except Exception as e:

        print("WebSocket error:", repr(e))

    finally:

        print("WebSocket connection ended")


if __name__ == "__main__":

    import uvicorn

    uvicorn.run(
        app,
        host="0.0.0.0",
        port=8000
    )