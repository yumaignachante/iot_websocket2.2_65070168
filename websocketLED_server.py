import asyncio
import websockets
import RPi.GPIO as GPIO

# GPIO setup for the LED with PWM
LED_PIN = 8
GPIO.setmode(GPIO.BOARD)
GPIO.setup(LED_PIN, GPIO.OUT)

pwm = GPIO.PWM(LED_PIN, 1000)  # Set PWM frequency to 1kHz
pwm.start(0)  # Start PWM with 0% duty cycle

connected_clients = set()

async def handle_connection(websocket, path):
    global connected_clients
    connected_clients.add(websocket)
    print("Client connected")
    
    try:
        async for message in websocket:
            brightness = int(message)
            print(f"Setting LED brightness to {brightness}%")
            pwm.ChangeDutyCycle(brightness)

            # Send the brightness value to all connected clients
            if connected_clients:
                await asyncio.gather(*(ws.send(message) for ws in connected_clients))
    except websockets.exceptions.ConnectionClosed as e:
        print(f"Connection closed: {e}")
    finally:
        connected_clients.remove(websocket)

async def main():
    server = await websockets.serve(handle_connection, "0.0.0.0", 8765)
    print("RPi B WebSocket server running on ws://0.0.0.0:8765")
    await server.wait_closed()

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("Exiting...")
    finally:
        pwm.stop()
        GPIO.cleanup()
