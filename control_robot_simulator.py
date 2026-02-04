import time
import json
import random
import math
import paho.mqtt.client as mqtt

# ======================
# MQTT 설정
# ======================
BROKER = "localhost"
PORT = 1883
TOPIC = "robots/telemetry"

client = mqtt.Client()
client.connect(BROKER, PORT)
client.loop_start()

# ======================
# 로봇 클래스
# ======================
class Robot:
    def __init__(self, robot_id):
        self.robot_id = robot_id
        self.x = random.uniform(-5, 5)
        self.z = random.uniform(-5, 5)

        self.target_x = random.uniform(-5, 5)
        self.target_z = random.uniform(-5, 5)

        self.speed = 1.0  # m/s
        self.battery = 100.0

    def update(self, dt):
        dx = self.target_x - self.x
        dz = self.target_z - self.z
        dist = math.sqrt(dx*dx + dz*dz)

        # 목표 지점 도착 → 새 목표 생성
        if dist < 0.1:
            self.target_x = random.uniform(-5, 5)
            self.target_z = random.uniform(-5, 5)
            return

        # 방향 벡터 정규화
        vx = dx / dist
        vz = dz / dist

        # 이동 
        self.x += vx * self.speed * dt
        self.z += vz * self.speed * dt

        # yaw 계산 (Unity에서 바로 사용 가능)
        yaw = math.degrees(math.atan2(vx, vz))

        # 배터리 소모
        self.battery = max(0, self.battery - 0.01)

        return {
            "robotId": self.robot_id,
            "px": self.x,
            "py": 0,
            "pz": self.z,
            "yaw": yaw,
            "battery": self.battery,
            "hasPayload": random.random() > 0.5
        }

# ======================
# 로봇 생성
# ======================
robots = [
    Robot("Robot-01"),
    Robot("Robot-02"),
    Robot("Robot-03")
]

# ======================
# 메인 루프
# ======================
prev_time = time.time()

while True:
    now = time.time()
    dt = now - prev_time
    prev_time = now

    for robot in robots:
        data = robot.update(dt)
        if data:
            payload = json.dumps(data)
            client.publish(TOPIC, payload)

    time.sleep(0.05)  # 20Hz
