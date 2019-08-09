import numpy as np
import warnings
from .Mission import Mission

class Person:
    def __init__(self, min_height, max_height):
        self.default_layer = np.random.randint(min_height, max_height) # 특별한 미션이 없다면 이동할 층
        self.current_mission = None
        self.on_mission = False
        self.count = 0
        self.missions = list()

    def add_mission(self, new_mission: Mission):
        allow_append = True
        for mission in self.missions:
            if mission.is_overlap_with(new_mission):
               allow_append = False
               break # 하나라도 겹치는 미션을 찾으면 검사를 끝낸다.

        if allow_append:
            self.missions.append(new_mission)
        else:
            raise warnings.warn("[Warning] Appending new mission failed.")
