import json
import time
import math
import random
from dataclasses import dataclass,asdict

@dataclass
class RobotTelemetry:
    robotId:str
    px:float
    py:float
    pz:float
    yaw:float
    battery:float
    hasPayload:bool

class RobotSimulator:
    def __init__(self,robot_id:str):
        self.robot_id=robot_id

        self.x=random.uniform(-5,5)
        self.z=random.uniform(-5,5)
        self.y=0,0
        
        self.target_x=self.x
        self.target_z=self.z
        self.speed=1.0
        self.battery=100
        self.has_payload=False

        self.pick_new_target()

    def pick_new_target(self):
        self.target_x=random.uniform(-5,5)
        self.target_z=random.uniform(-5,5)
     
    def update(self,dt:float):
        dx =self.target_x- self.x
        dz =self.target_z- self.z
        distance = math.sqrt(dx * dx + dz *dz)
        # 목표 도착
        if distance<0.1:
            self.pick_new_target()
            self.has_payload=random.random()>0.5
            return
         # 이동 방향 정규화
        dir_x= dx/distance
        dir_z= dz/distance
         # 실제 이동 (속도 기반)
        self.x += dir_x * self.speed * dt
        self.z += dir_z * self.speed * dt

        # yaw 계산 (라디안 → 도)
        yaw_rad = math.atan2(dir_x, dir_z)
        yaw_deg = math.degrees(yaw_rad)

        # 배터리 감소
        self.battery = max(0, self.battery - 0.01 * dt)

        self.yaw = yaw_deg


    def to_dto(self) -> RobotTelemetry:
        return RobotTelemetry(
            robotId=self.robot_id,
            px=self.x,
            py=self.y,
            pz=self.z,
            yaw=self.yaw,
            battery=self.battery,
            hasPayload=self.has_payload
        )
    

    def run_simulation():
        robots = [
            RobotSimulator("Robot-01"),
            RobotSimulator("Robot-02"),
            RobotSimulator("Robot-03"),
        ]

    tick_rate = 10  # Hz
    dt = 1.0 / tick_rate

    # while True:
    #     for robot in robots:
    #         robot.update(dt)
    #         dto = robot.to_dto()

    #         # MQTT로 보낼 JSON (지금은 print)
    #         payload = json.dumps(asdict(dto), indent=2)
    #         print(payload)

    #     time.sleep(dt)


    #     if __name__ == "__main__":
    #         run_simulation()