import asyncio
import websockets
import spidev  # For ADC (e.g., MCP3008)

# Setup ADC
spi = spidev.SpiDev()
spi.open(0, 0)
spi.max_speed_hz = 1350000

def read_adc(channel):
    adc = spi.xfer2([1, (8 + channel) << 4, 0])
    data = ((adc[1] & 3) << 8) + adc[2]
    return data

async def send_potentiometer_value():
    uri = "ws://<RPi_B_IP>:8765"  # Replace <RPi_B_IP> with the IP address of RPi B
    async with websockets.connect(uri) as websocket:
        while True:
            pot_value = read_adc(0)  # Assuming potentiometer is connected to channel 0
            brightness = int((pot_value / 1023) * 100)  # Convert to percentage
            await websocket.send(str(brightness))
            print(f"Sent potentiometer value: {brightness}%")
            await asyncio.sleep(1)  # Adjust the frequency as needed

if __name__ == "__main__":
    try:
        asyncio.run(send_potentiometer_value())
    except KeyboardInterrupt:
        print("Exiting...")
    finally:
        spi.close()
