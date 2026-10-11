import os
import sys
import time
import json
import subprocess
import requests
from PIL import Image, ImageDraw, ImageFont
import psutil

sys.path.append(os.path.expanduser('~/e-Paper/RaspberryPi_JetsonNano/python/lib'))
from waveshare_epd import epd2in13_V4

REFRESH_INTERVAL = 60      # Update screen every 60 seconds
FULL_REFRESH_EVERY = 15    # Full clean every 15 updates to prevent ghosting

# Coordinates for Open-Meteo API (Default: Kingston, ON - update to your lat/lon)
LATITUDE = 44.23
LONGITUDE = -76.48

def get_cpu_temp():
    try:
        output = subprocess.check_output(["vcgencmd", "measure_temp"]).decode()
        return output.replace("temp=", "").strip()
    except Exception:
        return "N/A"

def get_weather():
    try:
        url = f"https://api.open-meteo.com/v1/forecast?latitude={LATITUDE}&longitude={LONGITUDE}&current=temperature_2m,weather_code"
        res = requests.get(url, timeout=5).json()
        temp = res['current']['temperature_2m']
        code = res['current']['weather_code']
        
        # Weather code mapping
        weather_map = {
            0: "Clear", 1: "Mainly Clear", 2: "Partly Cloudy", 3: "Overcast",
            45: "Foggy", 61: "Rain", 71: "Snow", 95: "Thunderstorm"
        }
        condition = weather_map.get(code, "Cloudy")
        return f"{temp}°C, {condition}"
    except Exception:
        return "Weather unavailable"

def get_next_reminder():
    reminders_file = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'reminders.json')
    if not os.path.exists(reminders_file):
        return "No reminders file"
    try:
        with open(reminders_file, 'r') as f:
            data = json.load(f)
        
        today_str = time.strftime("%Y-%m-%d")
        
        # Check for event matching today
        for event in data.get("events", []):
            if event.get("date") == today_str:
                return f"Today {event.get('time', '')}: {event.get('title', '')}"
        
        # Fallback to first upcoming event in list
        if data.get("events"):
            first = data["events"][0]
            return f"{first.get('date')}: {first.get('title')}"
        
        return "No upcoming events"
    except Exception:
        return "Reminder JSON error"

def create_dashboard_canvas(epd):
    # Create 250x122 monochrome canvas
    image = Image.new('1', (epd.height, epd.width), 255)
    draw = ImageDraw.Draw(image)
    font = ImageFont.load_default()

    # Header
    draw.rectangle([(0, 0), (epd.height - 1, 16)], fill=0)
    draw.text((45, 2), "MECHATRONICS DESK BOARD", fill=255, font=font)

    # Metrics & Data
    temp = get_cpu_temp()
    ram_percent = psutil.virtual_memory().percent
    cpu_percent = psutil.cpu_percent()
    time_str = time.strftime("%H:%M | %b %d, %Y")
    weather_str = get_weather()
    reminder_str = get_next_reminder()

    # 250x122 Layout Grid
    draw.text((10, 22), f"Time: {time_str}", fill=0, font=font)
    draw.text((10, 38), f"Sys: {temp} | CPU: {cpu_percent}% | RAM: {ram_percent}%", fill=0, font=font)
    draw.text((10, 54), f"Weather: {weather_str}", fill=0, font=font)
    
    # Separator Line
    draw.line([(10, 72), (epd.height - 10, 72)], fill=0)

    # Reminder Section
    draw.text((10, 78), "NEXT REMINDER:", fill=0, font=font)
    draw.text((10, 94), reminder_str[:32], fill=0, font=font)  # Truncate to fit screen width

    return image

def main():
    epd = epd2in13_V4.EPD()
    update_count = 0

    print("Starting Dashboard with Weather & Reminders...")

    try:
        while True:
            if update_count % FULL_REFRESH_EVERY == 0:
                print("Performing full refresh...")
                epd.init()
                epd.Clear()
                image = create_dashboard_canvas(epd)
                epd.display(epd.getbuffer(image))
            else:
                print("Performing fast refresh...")
                epd.init_fast()
                image = create_dashboard_canvas(epd)
                if hasattr(epd, 'display_fast'):
                    epd.display_fast(epd.getbuffer(image))
                else:
                    epd.display(epd.getbuffer(image))

            epd.sleep()
            update_count += 1
            time.sleep(REFRESH_INTERVAL)

    except KeyboardInterrupt:
        print("\nStopping dashboard...")
        epd.init()
        epd.Clear()
        epd.sleep()

if __name__ == '__main__':
    main()