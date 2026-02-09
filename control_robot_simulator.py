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
# 로봇 클래스 (충돌 회피 포함)
# ======================
class Robot:
    def __init__(self, robot_id):
        self.robot_id = robot_id
        self.x = random.uniform(-14, 14)
        self.z = random.uniform(-26, 26)

        self.target_x = random.uniform(-14, 14)
        self.target_z = random.uniform(-26, 26)

        self.speed = 1.5  # m/s
        self.battery = 100.0
        self.radius = 0.5  # 로봇 반경 (충돌 감지용)
       
    def update(self, dt, other_robots):
        dx = self.target_x - self.x
        dz = self.target_z - self.z
        dist = math.sqrt(dx*dx + dz*dz)

        # 목표 지점 도착 → 새 목표 생성
        if dist < 0.1:
            self.target_x = random.uniform(-14, 14)
            self.target_z = random.uniform(-26, 26)
            return None

        # 방향 벡터 정규화
        vx = dx / dist
        vz = dz / dist

        # === 충돌 회피 로직 ===
        avoidance_vx = 0
        avoidance_vz = 0
        
        for other in other_robots:
            if other.robot_id == self.robot_id:
                continue
            
            # 다른 로봇까지의 거리
            other_dx = other.x - self.x
            other_dz = other.z - self.z
            other_dist = math.sqrt(other_dx*other_dx + other_dz*other_dz)
            
            # 너무 가까우면 회피
            safe_distance = (self.radius + other.radius) * 3  # 안전 거리
            if other_dist < safe_distance and other_dist > 0.01:
                # 멀어지는 방향으로 힘 추가
                repulsion_strength = (safe_distance - other_dist) / safe_distance
                avoidance_vx -= (other_dx / other_dist) * repulsion_strength
                avoidance_vz -= (other_dz / other_dist) * repulsion_strength

        # 목표 방향 + 회피 방향 합성
        final_vx = vx + avoidance_vx * 2  # 회피 가중치
        final_vz = vz + avoidance_vz * 2
        
        # 정규화
        final_dist = math.sqrt(final_vx*final_vx + final_vz*final_vz)
        if final_dist > 0.01:
            final_vx /= final_dist
            final_vz /= final_dist

        # 이동
        self.x += final_vx * self.speed * dt
        self.z += final_vz * self.speed * dt

        # 경계 체크
        self.x = max(-14, min(14, self.x))
        self.z = max(-26, min(26, self.z))

        # yaw 계산
        yaw = math.degrees(math.atan2(final_vx, final_vz))

        # 배터리 소모
        self.battery = max(0, self.battery - 0.01 * dt)

        return {
            "robotId": self.robot_id,
            "px": round(self.x, 3),
            "py": 0,
            "pz": round(self.z, 3),
            "yaw": round(yaw, 2),
            "battery": round(self.battery, 1),
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
frame_count = 0

try:
    while True:
        now = time.time()
        dt = now - prev_time
        prev_time = now

        for robot in robots:
            # 다른 로봇 정보 전달
            data = robot.update(dt, robots)
            if data:
                payload = json.dumps(data)
                client.publish(TOPIC, payload)
                
                if frame_count % 20 == 0:
                    print(f"[{data['robotId']}] pos:({data['px']:.1f}, {data['py']:.1f} ,{data['pz']:.1f}) "
                          f"yaw:{data['yaw']:.0f}° bat:{data['battery']:.0f}%")
        
        frame_count += 1
        time.sleep(0.05)  # 20Hz
        
except KeyboardInterrupt:
    print("\n종료 중...")
    client.loop_stop()
    client.disconnect()