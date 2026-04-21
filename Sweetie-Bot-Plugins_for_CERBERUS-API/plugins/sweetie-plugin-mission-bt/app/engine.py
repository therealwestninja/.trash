import time

class MissionEngine:
    def __init__(self):
        self.current = None
        self.pointer = 0

    def start(self, mission):
        self.current = mission
        self.pointer = 0
        return {"status":"started"}

    def tick(self):
        if not self.current:
            return {"status":"idle"}

        nodes = self.current.get("nodes", [])
        if self.pointer >= len(nodes):
            return {"status":"complete"}

        node = nodes[self.pointer]

        if node["action"] == "wait":
            time.sleep(node["payload"].get("seconds",1))
            self.pointer += 1
            return {"status":"waiting_done"}

        # pass-through action
        result = {
            "execute": node
        }
        self.pointer += 1
        return result

    def stop(self):
        self.current = None
        self.pointer = 0
        return {"status":"stopped"}

engine = MissionEngine()
