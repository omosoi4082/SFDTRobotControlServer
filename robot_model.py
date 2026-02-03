import random

class Robot:
    def __init__(self,robot_id):
        self.robot_id=robot_id
        self.x=random.uniform(0,10)
        self.y=random.uniform(0,10)
        self.theta=0
        self.battery=100
        self.state="IDLE"
    def update(self):
        self.x +=random.uniform(-0.3,0.3)
        self.y +=random.uniform(-0.3,0.3)
        self.theta=random.randint(0,360)
        self.battery=max(self.battery-random.uniform(0,0.2),0)
        self.state="MOVING" if self.battery>0 else "ERROR"

    def to_dict(self):
        return{
            "roboId":self.robot_id,
            "x":round(self.x,2),#round소수점 2번째 까지 반올림
            "y":round(self.y,2),
            "theta":self.theta,
            "battery":round(self.battery,1),
            "state":self.state
        }

