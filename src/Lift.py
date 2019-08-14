from .Person import Person

class Lift:
    def __init__(self):
        self.people = list()
        self.max = 5
        self.layer = 1
        self.is_open = False
    
    def append(self, person: Person):
        self.people.append(person)

    def delete(self, person: Person):
        self.people.remove(person)
