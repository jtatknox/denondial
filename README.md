# Surface Dial → Denon AVR RS-232 Control

## Warranty Disclaimer

This software and associated instructions are provided “as is,” without warranty of any kind, express or implied, including but not limited to the warranties of merchantability, fitness for a particular purpose, and noninfringement.  
In no event shall the authors or contributors be liable for any claim, damages, or other liability, whether in an action of contract, tort, or otherwise, arising from, out of, or in connection with the software or the use or other dealings in the software.

By following these instructions, you acknowledge that you do so at your own risk. This includes—but is not limited to—potential issues with your Raspberry Pi hardware, Denon AVR, Surface Dial, home network, or connected devices.

## Introduction
This guide describes how to set up a Microsoft Surface Dial to control a Denon AVR via its RS-232 interface, using a Raspberry Pi Zero 2 W. The Pi listens to the Dial’s rotation and button presses, then sends corresponding commands to the AVR over a USB→RS-232 adapter.

## Hardware Needed
- Denon AVR with RS-232 control
- Raspberry Pi Zero 2 W with Raspberry Pi OS Lite
- Microsoft Surface Dial
- Micro USB male to USB C female adapter
- [USB Type C to DB-9 Adapter Cable](https://www.adafruit.com/product/5446)

## 1. Prepare Raspberry Pi OS

Boot and log into your Pi Zero 2 W.

```wget https://github.com/conda-forge/miniforge/releases/latest/download/Miniforge3-Linux-aarch64.sh
bash Miniforge3-Linux-aarch64.sh
```

Install Mamba inside the base environment:

```conda install mamba -c conda-forge
mamba install python=3.11 -c conda-forge
mamba install asyncio serial time threading evdev -c conda-forge
```

## 2. Pair the Surface Dial

Put the Dial in pairing mode (hold the button until LED flashes). On the Pi:

```bluetoothctl
agent on
default-agent
scan on
pair XX:XX:XX:XX:XX:XX
trust XX:XX:XX:XX:XX:XX
connect XX:XX:XX:XX:XX:XX
quit
```

Replace XX:XX:XX:XX:XX:XX with your Dial’s MAC address.

## 3. Python Script

Save denon_dial.py to /home/pi/denon_dial.py

## 4. Test the Script

```python denon_dial.py
```

If it works, proceed to autostart.

## 5. Autostart on Boot

Create a systemd service:

```sudo nano /etc/systemd/system/surface_dial.service
```

Contents:

[Unit]
Description=Surface Dial Denon Control
After=bluetooth.target

[Service]
User=pi
WorkingDirectory=/home/pi
ExecStart=/home/pi/miniforge3/envs/dial/bin/python /home/pi/denon_dial.py
Restart=always

[Install]
WantedBy=multi-user.target

Enable and start:

```sudo systemctl daemon-reload
sudo systemctl enable surface_dial.service
sudo systemctl start surface_dial.service
```
