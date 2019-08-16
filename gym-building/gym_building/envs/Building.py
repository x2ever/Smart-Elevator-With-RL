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
        self.open_state = np.zeros(num_of_lift)
        self.position_state = np.zeros(num_of_lift)

        self.action_space = spaces.Discrete(5 ** num_of_lift)
        self.observation_space = spaces.Box(low=0, high=86400, shape=(1 + num_of_lift * height_of_building + height_of_building + 2 * num_of_lift, ))

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
        self.time += 3
        if self.time >= 24 * 60 * 60:
            done = True

        # [Person] Check if should move or not to
        for person in self.people: # 모든 사람들을 각각 검사해서
            if person.on_mission: # 미션 중인 사람은 넘어감
                pass
            else: # 미션중이 아니면
                for mission in person.missions:
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
            descrypted_action = action % 5 # 5진법 예를들어 23(10진법) = 43(5진법)이면 2번 승강기는 4번 액션을 1번 승강기는 3번 액션을 취한다.
            action //= 5
            if descrypted_action == 0:
                if self.height == lift.layer or lift.is_open:
                    reward -= 1
                else:
                    lift.layer += 1
            elif descrypted_action == 1:
                if 0 == lift.layer or lift.is_open:
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
                    lift.is_open = False
            else:
                pass

        # [Lift] People out
        for lift in self.lifts:
            for person in copy.copy(lift.people):
                # [Person] Check if lift is target layer
                if person.target == lift.layer and lift.is_open:
                    person.current_layer = lift.layer
                    person.on_lift = False
                    person.on_mission = False
                    person.target = None
                    lift.remove(person)

        # [Lift] People in
        for person in self.people:
            if person.on_mission and not person.on_lift:
                for lift in self.lifts:
                    # [Lift] Check if lift is full
                    if len(lift.people) == lift.max:
                        pass
                    elif lift.layer == person.current_layer and lift.is_open:
                        lift.append(person)
                        person.on_lift = True
                        person.current_layer = None
                        break

        # [Building] Check button Pressed Layer (Update state)
        # Inintializing
        self.inner_button = np.zeros(len(self.inner_button))
        self.outer_button = np.zeros(len(self.outer_button))
        self.open_state = np.zeros(len(self.open_state))
        self.position_state = np.zeros(len(self.position_state))

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
        time_state = np.array([self.time])

        # [Lift] Open and position state
        for i, lift in enumerate(self.lifts):
            if lift.is_open:
                self.open_state[i] = 1
            
            self.position_state[i] = lift.layer


        new_state = np.concatenate((time_state, self.inner_button, self.outer_button, self.open_state, self.position_state))

        # [Person] Update reward
        for person in self.people:
            if person.on_mission:
                reward -= 1
        
        if self.time % (60 * 60) == 30 * 60:
            #self._print()
            # print(new_state)
            pass

        return new_state, reward, done, {}
    
    def reset(self):
        for person in self.people:
            person.reset()
        
        for lift in self.lifts:
            lift.reset()
        
        self.time = 0
        self.inner_button = np.zeros(len(self.inner_button))
        self.outer_button = np.zeros(len(self.outer_button))
        self.open_state = np.zeros(len(self.open_state))
        self.position_state = np.zeros(len(self.position_state))

    def render(self):
        pass

    def _print(self):
        
        print("\nTime: %.1f" % (self.time / (60 * 60)))
        for i, lift in enumerate(self.lifts):
            print("Lift [%d]: %d" % (i, len(lift.people)))
        
        temp = [0, 0, 0, 0, 0, 0]
        for person in self.people:
            # print(person.target)
            if person.current_layer is not None:
                temp[person.current_layer] += 1
            else:
                temp[0] += 1
        
        print(temp)
