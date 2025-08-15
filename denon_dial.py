import asyncio
import serial
import time
import threading
from evdev import InputDevice, ecodes, list_devices

SERIAL_PORT = '/dev/ttyUSB0'
DIAL_NAME = 'Surface Dial System Multi Axis'
ACCUMULATE_THRESHOLD = 5  # ticks per volume step

class DenonController:
    def __init__(self):
        self.ser = None
        self.muted = False
        self.lock = threading.Lock()
        self.connect_serial()

    def connect_serial(self):
        while True:
            try:
                self.ser = serial.Serial(SERIAL_PORT, 9600, timeout=1)
                print("Connected to Denon over RS‑232.")
                return
            except Exception as e:
                print(f"Serial connection failed: {e}. Retrying in 5s…")
                time.sleep(5)

    def send_cmd(self, cmd):
        with self.lock:
            try:
                self.ser.write(f"{cmd}\r".encode())
                time.sleep(0.05)
            except Exception as e:
                print(f"Error sending command: {e}. Reconnecting…")
                self.connect_serial()

    def volume_up(self):
        self.send_cmd("MVUP")

    def volume_down(self):
        self.send_cmd("MVDOWN")

    def toggle_mute(self):
        self.muted = not self.muted
        cmd = "MUON" if self.muted else "MUOFF"
        print("Muting" if self.muted else "Unmuting")
        self.send_cmd(cmd)

async def find_dial():
    import evdev
    while True:
        devices = [evdev.InputDevice(fn) for fn in evdev.list_devices()]
        for d in devices:
            if DIAL_NAME in d.name:
                return d
        await asyncio.sleep(5)

async def dial_producer(queue, dial):
    accumulator = 0
    async for ev in dial.async_read_loop():
        if ev.type == ecodes.EV_REL and ev.code == ecodes.REL_DIAL:
            accumulator += ev.value
            if accumulator >= ACCUMULATE_THRESHOLD:
                await queue.put("volume_up")
                accumulator = 0
            elif accumulator <= -ACCUMULATE_THRESHOLD:
                await queue.put("volume_down")
                accumulator = 0
        elif ev.type == ecodes.EV_KEY and ev.code == ecodes.BTN_0 and ev.value == 1:
            await queue.put("toggle_mute")

async def command_consumer(denon, queue):
    while True:
        action = await queue.get()
        if action == "volume_up":
            denon.volume_up()
        elif action == "volume_down":
            denon.volume_down()
        elif action == "toggle_mute":
            denon.toggle_mute()
        queue.task_done()

async def main():
    dial = await find_dial()  # <-- await here
    denon = DenonController()
    dial = find_dial()    queue = asyncio.Queue()
    await asyncio.gather(
        dial_producer(queue, dial),
        command_consumer(denon, queue),
    )

if __name__ == "__main__":
    asyncio.run(main())