import uasyncio
import ujson
from machine import Pin, PWM
from microdot_asyncio import Microdot, send_file
from rocker import Rocker

led = PWM(Pin(16, Pin.OUT), freq=50, duty_u16=0)

app = Microdot()

rocker = Rocker()


@app.route('/favicon.ico')
async def favicon(request):
    return send_file('static/favicon.png', status_code=200, content_type='image/vnd.microsoft.icon')


@app.route('/static/jquery-3.6.0.min.js')
async def jquery(request):
    return send_file('static/jquery-3.6.0.min.js', status_code=200, content_type='text/script; charset=utf-8')


@app.route('/static/bootstrap.bundle.min.js')
async def bootstrap_js(request):
    return send_file('static/bootstrap.bundle.min.js', status_code=200, content_type='text/javascript; charset=utf-8')


@app.route('/static/bootstrap.min.css')
async def bootstrap_css(request):
    return send_file('/static/bootstrap.min.css', status_code=200, content_type='text/css; charset=utf-8')


@app.route('/')
async def hello(request):
    return send_file('static/index.html', status_code=200, content_type='text/html; charset=utf-8')


@app.route('/turn')
async def turn(request):
    angle = request.args.get('angle', type=int, default=0)
    speed = request.args.get('speed', type=int, default=300)
    duty = await rocker.turn(angle, speed)
    return str(duty)


@app.route('/rock')
async def rock(request):
    angle = request.args.get('angle', type=int, default=0)
    speed = request.args.get('speed', type=int, default=300)
    await rocker.interrupt()
    uasyncio.create_task(rocker.oscillation(angle, speed))
    return {"amplitude": angle, "speed": speed}


@app.route('/stop')
async def stop(request):
    await rocker.stop()
    return 'Rocker are stopped'


if __name__ == "__main__":
    app.run(port=80, debug=True)
