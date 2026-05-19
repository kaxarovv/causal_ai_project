import asyncio
import websockets
import json

async def broadcast_state(websocket):
    print("3D Модель подключена!")
    while True:
        try:
            with open('state.json', 'r') as f:
                data = f.read()
                if data: # Проверка что файл не пустой
                    state = json.loads(data)
                    await websocket.send(json.dumps(state))
        except (json.JSONDecodeError, FileNotFoundError):
            pass
        await asyncio.sleep(0.5) # Обновление 2 раза в секунду

async def main():
    print("WebSocket сервер запущен на порту 8765...")
    async with websockets.serve(broadcast_state, "0.0.0.0", 8765):
        await asyncio.Future()

if __name__ == "__main__":
    asyncio.run(main())

