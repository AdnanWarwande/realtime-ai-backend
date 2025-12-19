from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from contextlib import asynccontextmanager
import asyncio
from datetime import datetime, timezone
import json
import logging

from config import get_settings
import db
import ai

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

background_tasks = set()

@asynccontextmanager
async def lifespan(app: FastAPI):
    print("Server started")
    yield
    print("Server stopped")

app = FastAPI(lifespan=lifespan)

app.mount("/static", StaticFiles(directory="static"), name="static")

@app.get("/")
async def get_home():
    return FileResponse("static/index.html")

@app.websocket("/ws/session/{client_session_id}")
async def websocket_endpoint(websocket: WebSocket, client_session_id: str):
    await websocket.accept()
    
    try:
        session_id = await db.create_session(user_id=client_session_id)
        start_time = datetime.now(timezone.utc)
        
        await websocket.send_json({
            "type": "complete",
            "content": "Session started",
            "metadata": {"session_id": session_id}
        })
        
        history_context = ""
    except Exception as e:
        logger.error(f"Failed to start: {e}")
        await websocket.close()
        return

    try:
        while True:
            data = await websocket.receive_text()
            message_data = json.loads(data)
            user_text = message_data.get("content", "")
            
            await db.log_event(session_id, "user_message", user_text)
            history_context += f"User: {user_text}\n"
            
            ai_text = ""
            async for chunk in ai.get_streaming_response(history_context, user_text):
                ai_text += chunk
                await websocket.send_json({
                    "type": "token", 
                    "content": chunk
                })
            
            await websocket.send_json({"type": "complete", "content": ""})
            await db.log_event(session_id, "ai_response", ai_text)
            history_context += f"AI: {ai_text}\n"
            
    except WebSocketDisconnect:
        pass
    except Exception as e:
        logger.error(f"Error: {e}")
        try:
            await websocket.send_json({"type": "error", "content": str(e)})
        except:
            pass
    finally:
        async def process_summary(sid, s_time):
            try:
                end_time = datetime.now(timezone.utc)
                duration = int((end_time - s_time).total_seconds())
                
                events = await db.get_session_history(sid)
                summary = await ai.generate_summary(events)
                
                await db.update_session_summary(sid, summary, duration)
            except Exception:
                pass

        task = asyncio.create_task(process_summary(session_id, start_time))
        background_tasks.add(task)
        task.add_done_callback(background_tasks.discard)

if __name__ == "__main__":
    import uvicorn
    settings = get_settings()
    uvicorn.run("main:app", host=settings.host, port=settings.port, reload=False)
