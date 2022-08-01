import math

from machine import Pin, PWM
import uasyncio


class Rocker:
    def __init__(self):

        self.servo = PWM(Pin(12, Pin.OUT), freq=50)
        self.min_duty = 1575  # 1200 min (7940-1575=6365 this diapason equals 180 degrees for my servo MG996R)
        self.max_duty = 7940  # 8600 max

        self.current_angle = 90  # an average position, 90 degrees
        self.current_speed = 0
        self.current_amplitude = 0

        self.servo.duty_u16(self.angle_to_duty(self.current_angle))  # 90 degrees

        self.speed = 300  # 300 degrees/sec max speed in theory
        self.time_step = 0.04  # 20 msec (50Hz)

        self.is_working = False  # servo is not working, it is free
        self.is_stopping = False  # the stopping process is started
        self.is_breaking = False  # stopping immediately

    def duty_to_angle(self, duty):
        return (duty - self.min_duty) * 180 / (self.max_duty - self.min_duty)

    def angle_to_duty(self, angle):
        return int(angle * (self.max_duty - self.min_duty) / 180 + self.min_duty)

    async def turn(self, res_angle=90.0, speed=0):
        if speed == 0:
            self.servo.duty_u16(self.angle_to_duty(res_angle))
        else:
            if self.servo.duty_u16() > self.max_duty:
                self.servo.duty_u16(self.max_duty)
            elif self.servo.duty_u16() < self.min_duty:
                self.servo.duty_u16(self.min_duty)

            current_angle = self.duty_to_angle(self.servo.duty_u16())
            t = abs((res_angle - current_angle) / speed)  # time in sec for turning in the needed angle
            numbers_of_steps = int(t / self.time_step)

            angles = []
            if numbers_of_steps != 0:
                angle_step = (res_angle - self.duty_to_angle(self.servo.duty_u16())) / numbers_of_steps
                for _ in range(numbers_of_steps):
                    current_angle += angle_step
                    angles.append(current_angle)

                for a in angles:
                    await uasyncio.sleep(self.time_step)
                    self.servo.duty_u16(self.angle_to_duty(a))
        return self.servo.duty_u16()

    async def stop(self):
        self.is_stopping = True
        while self.is_working:
            await uasyncio.sleep_ms(1)
        self.is_stopping = False

    async def init_oscillation(self, amplitude):
        self.is_working = True
        await self.turn(res_angle=90, speed=90)  # set start position

    async def oscillation(self, amplitude=0, speed=0):

        await self.init_oscillation(amplitude)

        if speed == 0:
            speed = self.speed
        self.current_speed = speed
        self.current_amplitude = amplitude

        t = amplitude / speed
        steps = int(t / self.time_step)

        alphas = []
        for i in range(1, steps + 1):
            alphas.append((math.cos(math.pi / steps * i) * (-amplitude / 2)) + 90)

        new_alphas = alphas[len(alphas) // 2:-1] + list(reversed(alphas)) + alphas[0:len(alphas) // 2]
        while self.is_working:
            for i in range(len(new_alphas)):
                await uasyncio.sleep(self.time_step)
                self.servo.duty_u16(self.angle_to_duty(new_alphas[i]))
                if (self.is_stopping and i == len(new_alphas) - 1) or self.is_breaking:
                    self.is_working = False
                    self.current_angle = new_alphas[i]
                    break
        self.is_breaking = False
        self.is_stopping = False
