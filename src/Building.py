from .Lift import Lift

import numpy as np

class Building:
    def __init__(self, people, num_of_lift, height_of_building):
        self.lifts = [Lift() for i in range(num_of_lift)]
        self.time = 0
        self.people = people
        self.button_pressed_layer = np.zeros(height_of_building)

    def _step(self, action):
        '''
        [Time] += 1
        [Person] Check if should move or not to
        [Lift] Action: up, down, open, open_stay, close, close_stay
        [Lift] People out
            [Person] Check if lift is target layer
        [Lift] People in
            [Lift] Check if lift is full
            [Person] Check if trying to move
        [Building] Check button Pressed Layer
        [Person] Update reward
            [Person] On mission: -1

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

        # [Lift] Action: up, down, open, close, stay
        for lift in self.lifts: # discrete
            descrypted_action = action % 5
            action //= 6
            if descrypted_action == 0:
                if lift.max == lift.layer:
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
                



        return new_state, reward, done