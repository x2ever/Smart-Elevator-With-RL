from .Lift import Lift

import numpy as np
import copy
import cv2

import gym
from gym import error, spaces, utils
from gym.utils import seeding

class BuildingEnv(gym.Env):
    metadata = {'render.modes': ['human']}
    FONT = cv2.FONT_HERSHEY_SIMPLEX

    def __init__(self, people, num_of_lift, height_of_building):
        self.lifts = [Lift() for i in range(num_of_lift)]
        self.time = 0
        self.people = people
        self.height = height_of_building
        self.inner_button = np.zeros(height_of_building * num_of_lift)
        self.outer_button = np.zeros(height_of_building)
        self.open_state = np.zeros(num_of_lift)
        self.position_state = np.zeros(num_of_lift)
        self.inner_person_state = np.zeros(num_of_lift)
        self.default_img = np.zeros((100 * self.height + 50, 60 + num_of_lift * 100, 3), np.uint8)
        self.default_img = cv2.rectangle(self.default_img, (0, 0), (60, height_of_building * 100), (150, 150, 100), -1)
        self.default_img = cv2.rectangle(self.default_img, (0, 0), (60, height_of_building * 100), (255, 255, 255), 2)
        self.default_img = cv2.rectangle(self.default_img, (0, self.height * 100), (60 + 100 * num_of_lift, 50 + self.height * 100), (100, 200, 100), -1)
        self.default_img = cv2.rectangle(self.default_img, (0, self.height * 100), (60 + 100 * num_of_lift, 50 + self.height * 100), (255, 255, 255), 2)
        cv2.putText(self.default_img, 'Time: ', (0, self.height * 100 + 40), self.FONT, 0.6, (0,0,200), 1)
        for i in range(height_of_building):
            self.default_img = cv2.line(self.default_img, (0, 100 * i), (60, 100 * i), (255, 255, 255), 2)
            cv2.putText(self.default_img, '%d F' % (height_of_building - i), (5, 20 + i * 100), self.FONT, 0.5, (255, 255, 255), 1)
            cv2.putText(self.default_img, 'Stay:', (5, 40 + i * 100), self.FONT, 0.4, (255, 0, 100), 1)
            # cv2.putText(self.default_img, '30', (25, 55), self.FONT, 0.4, (255, 0, 100), 1)
            cv2.putText(self.default_img, 'Moving:', (5, 70 + i * 100), self.FONT, 0.4, (0, 0, 255), 1)
            # cv2.putText(self.default_img, '30', (25, 85), self.FONT, 0.4, (0, 0, 255), 1)

        self.action_space = spaces.Discrete(5 ** num_of_lift)
        self.observation_space = spaces.Box(low=0, high=1, shape=(1 + num_of_lift * height_of_building + height_of_building + 3 * num_of_lift, ))

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
        self.time += 5
        if self.time >= 24 * 60 * 60:
            done = True

        # [Person] Check if should move or not to
        for person in self.people: # 모든 사람들을 각각 검사해서
            if person.on_mission: # 미션 중인 사람은 넘어감
                pass
            else: # 미션중이 아니면
                default = True
                for mission in person.missions:
                    if mission.is_valid(self.time):
                        default = False
                        person.target = mission.target
                        if mission.target != person.current_layer:
                            person.on_mission = True
                            person.target = mission.target
                        
                        break


                # 여전히 할당받은 미션이 없다면
                if default:
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
                if 1 == lift.layer or lift.is_open:
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
                reward += 0.0001

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
                    reward += 200

        # [Lift] People in
        for person in self.people:
            if person.on_mission and (not person.on_lift) and person.target != person.current_layer and person.target is not None:
                for lift in self.lifts:
                    # [Lift] Check if lift is full
                    if len(lift.people) == lift.max:
                        pass
                    elif lift.layer == person.current_layer and lift.is_open:
                        reward += 100
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
        self.inner_person_state = np.zeros(len(self.inner_person_state))

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
            self.inner_person_state[i] = len(lift.people) / lift.max
            if lift.is_open:
                self.open_state[i] = 1
            
            self.position_state[i] = lift.layer


        new_state = np.concatenate((time_state / (24 * 60 * 60), self.inner_button, self.outer_button, self.open_state, self.position_state / self.height, self.inner_person_state))

        # [Person] Update reward
        for person in self.people:
            if person.on_mission:
                reward -= 1.5
            
            if person.on_mission and person.on_lift:
                reward += 0.7
        
        if self.time % (60 * 60) == 30 * 60:
            # self._print()
            pass

        return new_state, reward / (50 * 24 * 60 / 5), done, {}
    
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
        self.inner_person_state = np.zeros(len(self.inner_person_state))
        
        time_state = np.array([self.time])
        state = np.concatenate((time_state / (24 * 60 * 60), self.inner_button, self.outer_button, self.open_state, self.position_state / self.height, self.inner_person_state))

        return state

    def render(self, mode='rgb_array', close=False):
        img = copy.deepcopy(self.default_img)
        floor_list = np.zeros((self.height, 2))
        lift_list = np.zeros((len(self.lifts), 3))

        for person in self.people:
            if not person.on_lift and not person.on_mission:
                floor_list[person.current_layer - 1][0] += 1
            
            if not person.on_lift and person.on_mission:
                floor_list[person.current_layer - 1][1] += 1

        for i, lift in enumerate(self.lifts):
            lift_list[i][0] = len(lift.people)
            lift_list[i][1] = lift.layer - 1

            if lift.is_open:
                lift_list[i][2] = True
            else:
                lift_list[i][2] = False

        for h in range(self.height):
            cv2.putText(img, '%d' % (floor_list[h][0]), (25, (self.height - h - 1) * 100 + 55), self.FONT, 0.4, (255, 0, 100), 1)
            cv2.putText(img, '%d' % (floor_list[h][1]), (25, (self.height - h - 1) * 100 + 85), self.FONT, 0.4, (0, 0, 255), 1)

        for i, lift in enumerate(self.lifts):
            img = cv2.rectangle(img, (60 + i * 100, 0 + 100 * int(self.height - lift_list[i][1] - 1)), (160 + i * 100, 100 + 100 * int(self.height - lift_list[i][1] - 1)), (100, 150, 150), -1)
            img = cv2.rectangle(img, (60 + i * 100, 0 + 100 * int(self.height - lift_list[i][1] - 1)), (160 + i * 100, 100 + 100 * int(self.height - lift_list[i][1] - 1)), (255, 255, 255), 2)
            if lift_list[i][2]:
                img = cv2.rectangle(img, (80 + i * 100, 0 + 100 * int(self.height - lift_list[i][1] - 1)), (140 + i * 100, 100 + 100 * int(self.height - lift_list[i][1] - 1)), (10, 50, 50), -1)
                img = cv2.rectangle(img, (80 + i * 100, 0 + 100 * int(self.height - lift_list[i][1] - 1)), (140 + i * 100, 100 + 100 * int(self.height - lift_list[i][1] - 1)), (255, 255, 255), 2)

                cv2.putText(img, 'Num:', (95 + i * 100, 45 + 100 * int(self.height - lift_list[i][1] - 1)), self.FONT, 0.4, (255, 255, 255), 1)
                cv2.putText(img, '%d' % (lift_list[i][0]), (105 + i * 100, 60 + 100 * int(self.height - lift_list[i][1] - 1)), self.FONT, 0.4, (255, 255, 255), 1)
            else:
                cv2.putText(img, 'Num:', (95 + i * 100, 45 + 100 * int(self.height - lift_list[i][1] - 1)), self.FONT, 0.4, (0, 0, 0), 1)
                cv2.putText(img, '%d' % (lift_list[i][0]), (105 + i * 100, 60 + 100 * int(self.height - lift_list[i][1] - 1)), self.FONT, 0.4, (0, 0, 0), 1)

        cv2.putText(img, '%02d:%02d' % (self.time // 3600, (self.time - 3600 * (self.time // 3600)) // 60), (80, self.height * 100 + 40), self.FONT, 0.6, (0,0,200), 1)
        return img

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
