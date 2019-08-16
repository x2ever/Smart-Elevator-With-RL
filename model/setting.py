from src.Mission import Mission
from src.Person import Person

import gym

people = [Person(4, 5) for i in range(50)] # 2 ~ 5층에서 일하는 50명의 사람
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

if __name__ == "__main__":
    ''' 정말 간단한 회사 시나리오 1
    [일정]
    24:00 ~ 00:00 출근시간
        ~
    07:30 ~ 08:30 아침식사  
        ~
    09:00 ~ 10:00 아침회의
        ~
    13:00 ~ 14:00 점심식사
        ~
    16:00 ~ 17:00 저녁회의
        ~
    18:00 ~ 23:59 퇴근시간

    [건물 정보]
    1층 사무실
    2층 식사장소
    3층 회의실
    4층 사무실
    5층 사무실

    [인원 수]
    50명
    '''
    people = [Person(4, 5) for i in range(50)] # 4 ~ 5층에서 일하는 50명의 사람
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