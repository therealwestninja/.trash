import math

class OdomState:
    def __init__(self):
        self.x = 0.0
        self.y = 0.0
        self.yaw = 0.0

    def update(self, vx, vy, yaw_rate, dt):
        self.yaw += yaw_rate * dt
        dx = vx * dt
        dy = vy * dt

        self.x += dx * math.cos(self.yaw) - dy * math.sin(self.yaw)
        self.y += dx * math.sin(self.yaw) + dy * math.cos(self.yaw)

        return self.get()

    def get(self):
        return {"x": self.x, "y": self.y, "yaw": self.yaw}

    def reset(self):
        self.x = 0
        self.y = 0
        self.yaw = 0
        return {"status":"reset"}

state = OdomState()
