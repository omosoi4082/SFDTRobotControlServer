import json
import time
import paho.mqtt.client as mqtt
from robot_model import Robot
from config import *

class RobotSimulator:
    def __init__(self):
        self.client=mqtt.Client()
        self.client.connect(BROKER_HOST,BROKER_POST)
        self.robots=[Robot(f"R-{i+1:03}")for i in range(ROBOT_COUNT)]
    def run(self):
      while True:
         for robot in self.robots:
            robot.update()
            topic=f"robot/{robot.robot_id}/state"#f는$같다
            payload=json.dumps(robot.to_dict())

#topic어디로 보낼지/payload무슨 데이터/qos=1최소 1번은 반드시 전달
            self.client.publish(topic,payload,qos=1)
            time.sleep(PUBLISH_INTERVAL)

