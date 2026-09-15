# This file is executed on every boot (including wake-boot from deepsleep)
#import esp
#esp.osdebug(None)
#import webrepl
#webrepl.start()

import network
import config

print("Connecting to WiFi...")
wifi = network.WLAN(network.STA_IF)
wifi.active(True)
wifi.connect(config.wifi_ssid, config.wifi_password)
while not wifi.isconnected():
    pass
print("Connected.")

if (config.enable_ftp):
    import uftpd

