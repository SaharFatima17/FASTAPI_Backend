from fastapi import APIRouter, WebSocket, WebSocketDisconnect

router = APIRouter(tags=["WebSockets"])

@router.websocket("/ws/echo")
async def websocket_echo_endpoint(websocket: WebSocket):
    await websocket.accept()
    print("⚡ Real-time WebSocket Tunnel Opened Successfully")
    try:
        while True:
            # Client se text message receive hone ka wait karein
            data = await websocket.receive_text()
            print(f"📥 Received from client: {data}")
            
            # Wahi message client ko dynamic reply/echo karein
            await websocket.send_text(f"Server Echo: {data}")
    except WebSocketDisconnect:
        print("❌ Client dynamically disconnected from stream")