# Raspberry Pi e-paper Weather & Reminder Display

a headless desk monitor built with a Raspberry Pi 4 and waveshare 2.13-inch V4 e-paper display. The dashboard gets live local weather data via APIs, tracks performance metrics, reads an upcoming calendar from JSON 

## features 

- tracking of CPU temperature, CPU load percentage, and RAM usage 'psutil'
- gets outdoor temperature and weather conditions from Open-Meteo API using Python 'requests' 
- displays sscheduled events loaded from a local JSON file
- used waveshare fast refresh 

## hardware 
- Raspberry Pi 4 Model B (2GB RAM)
- Waveshare 2.13-inch e-Paper Module V4
- Active cooling fan (GPIO 5V/GNG/TXD)
- 8-pin female to female jumper wire harness 

## key libraries 
- 'PIL'
- 'psutil' 
- 'requests'

## E-paper refresh management
Calling standard epd.sleep() powers down the display controller's internal RAM. during partial refreshes, if RAM state is lost, writing new frames on top of old ones leads to smudging. 

This was solved by using init_fast() and display_fast() 
the script tracks refresh counts and executes a full epd.init() and epd.Clear() every 15 iterations to prevent physical micro-capsule degradation. 
