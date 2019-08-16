from .Person import Person

class Lift:
    def __init__(self):
        self.people = list()
        self.max = 10
        self.layer = 1
        self.is_open = False
    
    def append(self, person: Person):
        self.people.append(person)

    def remove(self, person: Person):
        self.people.remove(person)

    def reset(self):
        self.__init__()
