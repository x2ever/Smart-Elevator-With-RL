from src.Mission import Mission
from src.Person import Person

import gym

people = [Person(4, 4) for i in range(25)] + [Person(5, 5) for i in range(25)]# 2 ~ 5층에서 일하는 50명의 사람
breakfast = Mission(2, 7.5 * 60 * 60, 8.5 * 60 * 60) # 아침식사
morning_conference = Mission(3, 9 * 60 * 60, 10 * 60 * 60) # 아침회의
lunch = Mission(2, 13 * 60 * 60, 14 * 60 * 60) # 점심식사
dinner_conference = Mission(3, 16 * 60 * 60, 17 * 60 * 60) # 저녁회의
off_work = Mission(1, 18 * 60 * 60, 24 * 60 * 60 - 1) # 퇴근시간

for person in people:
    person.add_mission(breakfast)
    person.add_mission(lunch)
    person.add_mission(off_work)
    if person.default_layer == 4: # 4층 근무자만 아침 회의에 참가
            person.add_mission(morning_conference)
    if person.default_layer == 5: # 5층 근무자만 저녁 회의에 참가
            person.add_mission(dinner_conference)