import network
import uasyncio

SSID = 'FEDOR'
PASSWORD = 'molekula'


async def connect(s, p):
    wlan = network.WLAN(network.STA_IF)
    wlan.active(True)
    if not wlan.isconnected():
        print('connecting to network...')
        wlan.connect(s, p)
        while not wlan.isconnected():
            await uasyncio.sleep_ms(1)
    print('network config:', wlan.ifconfig())


uasyncio.create_task(connect(SSID, PASSWORD))
