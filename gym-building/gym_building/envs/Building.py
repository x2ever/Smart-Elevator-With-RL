from .Lift import Lift

import numpy as np
import copy
import cv2

import gym
from gym import error, spaces, utils
from gym.utils import seeding

class BuildingEnv(gym.Env):
    metadata = {'render.modes': ['human']}

    def __init__(self, people, num_of_lift, height_of_building):
        self.lifts = [Lift() for i in range(num_of_lift)]
        self.time = 0
        self.people = people
        self.height = height_of_building
        self.inner_button = np.zeros(height_of_building * num_of_lift)
        self.outer_button = np.zeros(height_of_building)

    def step(self, action):
        '''
        [Time] += 1
        [Person] Check if should move or not to
        [Lift] Action: up, down, open, open_stay, close, close_stay
        [Lift] People out
            [Person] Check if lift is target layer
        [Lift] People in
            [Lift] Check if lift is full
        [Building] Check button Pressed Layer (Update state)
        [Person] Update reward
            [Person] if on mission: reward -1

        return new_state, reward, done, ?
        '''
        new_state = None
        reward = 0
        done = False
        
        # [Time] += 1
        self.time += 1
        if self.time >= 24 * 60 * 60:
            done = True
            self.time -= 24 * 60 * 60

        # [Person] Check if should move or not to
        for person in self.people: # 모든 사람들을 각각 검사해서
            if person.on_mission: # 미션 중인 사람은 넘어감
                pass
            else: # 미션중이 아니면
                for mission in person.mission:
                    if mission.is_valid(self.time):
                        if mission.target != person.current_layer:
                            person.on_mission = True
                            person.target = mission.target

                        break
                    # 여전히 할당받은 미션이 없다면
                    if not person.on_mission:
                        if person.default_layer != person.current_layer: # Default 층에 있는지 확인
                            person.on_mission = True
                            person.target = person.default_layer

        # [Lift] Action: up, down, open, close, stay
        for lift in self.lifts: # discrete
            descrypted_action = action % 5
            action //= 6
            if descrypted_action == 0:
                if self.height == lift.layer:
                    reward -= 1
                else:
                    lift.layer += 1
            elif descrypted_action == 1:
                if 0 == lift.layer:
                    reward -= 1
                else:
                    lift.layer -= 1
            elif descrypted_action == 2:
                if lift.is_open:
                    reward -= 1
                else:
                    lift.is_open = True
            elif descrypted_action == 3:
                if not lift.is_open:
                    reward -= 1
                else:
                    pass
            else:
                pass

        # [Lift] People out
        for lift in self.lifts:
            for person in copy.deepcopy(lift.people):
                # [Person] Check if lift is target layer
                if person.target == lift.layer:
                    person.current_layer = lift.layer
                    person.on_lift = False
                    person.on_mission = False
                    person.target = None
                    lift.delete(person)

        # [Lift] People in
        for person in self.people:
            if person.on_mission:
                for lift in self.lifts:
                    # [Lift] Check if lift is full
                    if len(lift.people) == lift.max:
                        pass
                    else:
                        lift.append(person)
                        person.on_lift = True
                        person.current_layer = None
                        break

        # [Building] Check button Pressed Layer (Update state)
        # Inintializing
        self.inner_button = np.zeros(len(self.inner_button))
        self.outer_button = np.zeros(len(self.outer_button))
        # [Buidling] Inner
        padding = 0
        for lift in self.lifts:
            for person in lift.people:
                self.inner_button[padding + person.target - 1] = 1
            
            padding += self.height # Update next lift's buttons

        # [Building] Outer
        for person in self.people:
            if not person.on_lift and person.on_mission:
                self.outer_button[person.current_layer - 1] = 1

        # [Building] Time state
        time_state = np.eye(24 * 60 * 60)[self.time]
        new_state = np.concatenate((time_state, self.inner_button, self.outer_button))

        # [Person] Update reward
        for person in self.people:
            if person.on_mission:
                reward -= 1

        return new_state, reward, done
    
    def reset(self):
        for person in self.people:
            person.reset()
        
        for lift in self.lifts:
            lift.reset()
        
        self.time = 0
        self.inner_button = np.zeros(len(self.inner_button))
        self.outer_button = np.zeros(len(self.outer_button))

    def render(self):
        pass