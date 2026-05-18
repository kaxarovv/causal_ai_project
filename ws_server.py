# import asyncio
# import websockets
# import json

# async def broadcast_state(websocket):
#     print("3D Модель подключена!")
#     while True:
#         try:
#             with open('state.json', 'r') as f:
#                 data = f.read()
#                 if data: # Проверка что файл не пустой
#                     state = json.loads(data)
#                     await websocket.send(json.dumps(state))
#         except (json.JSONDecodeError, FileNotFoundError):
#             pass
#         await asyncio.sleep(0.5) # Обновление 2 раза в секунду

# async def main():
#     print("WebSocket сервер запущен на порту 8765...")
#     async with websockets.serve(broadcast_state, "0.0.0.0", 8765):
#         await asyncio.Future()

# if __name__ == "__main__":
#     asyncio.run(main())

import asyncio
import websockets
import json

# Множество для хранения всех активных подключений
connected_clients = set()

async def router(websocket):
    # Регистрируем новое подключение (например, открыли вкладку с 3D)
    connected_clients.add(websocket)
    print(f"Новое подключение! Активных клиентов: {len(connected_clients)}")
    
    try:
        async for message in websocket:
            # Как только приходит сообщение (от app.py), 
            # рассылаем его всем остальным клиентам (3D-моделям)
            receivers = [client for client in connected_clients if client != websocket]
            if receivers:
                await asyncio.gather(*(client.send(message) for client in receivers))
                
    except websockets.exceptions.ConnectionClosed:
        pass # Клиент просто закрыл вкладку
    finally:
        # Убираем клиента при отключении
        connected_clients.remove(websocket)
        print(f"Клиент отключился. Активных клиентов: {len(connected_clients)}")

async def main():
    print("🚀 In-Memory WebSocket сервер запущен на порту 8765...")
    # Отключаем лимиты на размер пакетов для скорости
    async with websockets.serve(router, "0.0.0.0", 8765, max_size=None):
        await asyncio.Future()

if __name__ == "__main__":
    asyncio.run(main())