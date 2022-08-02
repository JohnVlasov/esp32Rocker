import uasyncio
import ujson
from machine import Pin, PWM
from microdot_asyncio import Microdot, send_file, Response
from rocker import Rocker

led = PWM(Pin(16, Pin.OUT), freq=50, duty_u16=0)

app = Microdot()

rocker = Rocker()


def generator_static_file(file_name):
    buf = 2048
    with open(file_name, 'rb') as f:
        chunk = f.read(buf)
        while chunk:
            yield chunk
            chunk = f.read(buf)


@app.route('/favicon.ico')
async def favicon(request):
    return Response(body=generator_static_file('static/favicon.png'),
                    headers={"Content-Type": "image/vnd.microsoft.icon", "Cache-Control": "public; max-age=31536000"},
                    status_code=200)


@app.route('/static/jquery-3.6.0.min.js')
async def jquery(request):
    return Response(body=generator_static_file('/static/jquery-3.6.0.min.js'),
                    headers={"Content-Type": "text/javascript; charset=utf-8", "Cache-Control": "public; max-age=31536000"},
                    status_code=200)


@app.route('/static/bootstrap.bundle.min.js')
async def bootstrap_js(request):
    return Response(body=generator_static_file('static/bootstrap.bundle.min.js'),
                    headers={"Content-Type": "text/javascript; charset=utf-8", "Cache-Control": "public; max-age=31536000"},
                    status_code=200)


@app.route('/static/bootstrap.min.css')
async def bootstrap_css(request):
    return Response(body=generator_static_file('/static/bootstrap.min.css'),
                    headers={"Content-Type": "text/css; charset=utf-8", "Cache-Control": "public; max-age=31536000"},
                    status_code=200)


@app.route('/')
async def hello(request):
    return Response(body=generator_static_file('static/index.html'),
                    headers={"Content-Type": "text/html; charset=utf-8", "Cache-Control": "public; max-age=31536000"},
                    status_code=200)


@app.route('/rock')
async def rock(request):
    ampl = request.args.get('ampl', type=int, default=0)
    freq = request.args.get('freq', type=float, default=0.1)
    await rocker.stop()
    uasyncio.create_task(rocker.oscillation(ampl, freq))
    return Response(body={"ampl": ampl, "freq": freq}, status_code=200)


@app.route('/stop')
async def stop(request):
    await rocker.stop()
    return 'Rocker are stopped'


if __name__ == "__main__":
    app.run(port=80, debug=True)
