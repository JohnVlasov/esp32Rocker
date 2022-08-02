import math

import utime
from machine import Pin, PWM
import uasyncio


class Rocker:
    def __init__(self):

        self.servo = PWM(Pin(12, Pin.OUT), freq=50)
        self.min_duty = 1575  # 1200 min (7940-1575=6365 this diapason equals 180 degrees for my servo MG996R)
        self.max_duty = 7940  # 8600 max

        self.init_angle = 90  # an average position, 90 degrees
        self.current_direction = 'up'

        self.servo.duty_u16(self.angle_to_duty(self.init_angle))  # 90 degrees

        self.time_step = 0.04  # 20 msec (50Hz)

        self.is_working = False  # servo is not working, it is free
        self.is_stopping = False  # the stopping process is started
        self.is_breaking = False  # stopping immediately

    def duty_to_angle(self, duty):
        return (duty - self.min_duty) * 180 / (self.max_duty - self.min_duty)

    def angle_to_duty(self, angle):
        return int(angle * (self.max_duty - self.min_duty) / 180 + self.min_duty)

    async def stop(self):
        self.is_stopping = True
        start = utime.time()
        while self.is_working:
            await uasyncio.sleep_ms(1)
            timeout = utime.time() - start
            if timeout > 10:
                self.is_working = False
                break
        self.is_stopping = False

    async def oscillation(self, amplitude=0, freq=0):
        if amplitude == 0 or freq == 0:
            return
        self.is_working = True
        init = True  # starting process

        t = 1 / freq
        steps = int(t / self.time_step)

        alphas = []  # list of angles for servo, started from 90 degrees
        for i in range(1, (steps + 1)):
            alphas.append(90 + (1 - math.cos(2 * math.pi / steps * i) * (amplitude / 2)))
        alphas = alphas[len(alphas) // 4:-1] + alphas[0: len(alphas) // 4]
        while self.is_working:
            for i in range(len(alphas)):
                if (i < len(alphas) - 1) and (alphas[i + 1] > alphas[i]) or i == len(alphas) - 1:
                    direction = 'up'
                else:
                    direction = 'down'

                if self.current_direction == direction:
                    if (direction == 'up' and alphas[i] >= 90) or (direction == 'down' and alphas[i] <= 90):
                        init = False
                if init:
                    continue
                await uasyncio.sleep(self.time_step)
                self.servo.duty_u16(self.angle_to_duty(alphas[i]))

                if self.is_stopping:
                    if i < (len(alphas) - 1):
                        if (direction == 'up' and (alphas[i] < 90 <= alphas[i + 1])) or (direction == 'down' and (alphas[i] > 90 >= alphas[i + 1])):
                            self.is_working = False
                            self.current_direction = direction
                            break

        self.is_breaking = False
        self.is_stopping = False
