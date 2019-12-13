import time
from adafruit_servokit import ServoKit


kit = ServoKit(channels=16)
for i in range(16):
    kit.servo[i].set_pulse_width_range(500, 2500)
    kit.servo[i].throttle = 1

class HandServos:
    def __init__(self, servos):
        self.servos = {}
        for servo in servos:
            self.servos[servo['label']] = servo


    def angle(self, label, angle):
        ch = self.servos[label]['channel']
        kit.servo[ch].angle = angle


    def format_servo_data(label, channel, min_angle=0, max_angle=0, inverted=False):
        return {'label': label, 'channel': channel, 'min_angle': min_angle, 'max_angle': max_angle, 'inverted': inverted}

    def full_angle(self, labels, pos):
        if not (type(labels) is list):
            labels = [labels]
        for l in labels:
            servo = self.servos[l]
            if pos:
                if not servo['inverted']:
                    self.angle(l, servo['max_angle'])
                else:
                    self.angle(l, servo['min_angle'])
            else:
                if not servo['inverted']:
                    self.angle(l, servo['min_angle'])
                else:
                    self.angle(l, servo['max_angle'])

if __name__ == '__main__':
    index = HandServos.format_servo_data('index', 0, min_angle=20, max_angle=80, inverted=True)
    middle = HandServos.format_servo_data('middle', 1, min_angle=44, max_angle=100, inverted=True)
    ring = HandServos.format_servo_data('ring', 2, min_angle=10, max_angle=75)
    pinky = HandServos.format_servo_data('pinky', 3, max_angle=65)
    wrist_left = HandServos.format_servo_data('wleft', 8, min_angle=110, max_angle=150)
    wrist_right = HandServos.format_servo_data('wright', 9, min_angle=130, max_angle=170)
    
    def move_wrist_down():
        hs.angle('wleft', 137)
        hs.angle('wright', 142)
    def move_wrist_up():
        hs.angle('wleft', 110)
        hs.angle('wright', 170)
    def move_wrist_neutral():
        hs.angle('wleft', 130)
        hs.angle('wright', 150)

    hs = HandServos([index, middle, ring, pinky, wrist_left, wrist_right])
    
    all = ['index', 'middle', 'ring', 'pinky']

    # hs.full_angle(all, 1)
    # time.sleep(.75)
    # hs.full_angle(all, 0)
    # time.sleep(.75)
    # hs.full_angle(all, 1)
    # time.sleep(.75)
    # hs.full_angle(all, 0)

    
    while True:
        data = input()
        if not len(data.split(' ')) >= 2:
            if data == 'up':
                move_wrist_up()
            elif data == 'down':
                move_wrist_down()
            elif data == 'mid':
                move_wrist_neutral()
            continue
        a1, a2 = data.split(' ')
        if a1 in all:
            a2 = int(a2)
            # if a2 == 0 or a2 == 1:
            #     hs.full_angle(a1, a2)
            # else:
            hs.angle(a1,a2)
            continue   
        a1 = int(a1)
        a2 = int(a2)
        hs.angle('wleft', a1)
        hs.angle('wright', a2)
        # finger, down, up = data.split(' ')
        # for i in range(3):
        #     hs.angle(finger, int(down))
        #     time.sleep(.75)
        #     hs.angle(finger, int(up))
        #     time.sleep(.75)
