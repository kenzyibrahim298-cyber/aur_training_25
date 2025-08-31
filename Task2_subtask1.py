from random import randint
class Employee:
    def __init__(self, name, family, manager=None):
        self._name = name
        self._id = randint(1000, 9999)
        self._family = family.copy()
        self._manager = manager
        self.salary = 2500

    @property
    def id(self):
      return self._id  

    @property
    def family(self):
       return self._family.copy()
        


    def apply_raise(self, managed_employee: 'Employee', raise_percent: int):
       if managed_employee._manager == self:
          managed_employee.salary *= (1 + raise_percent / 100)
          print(managed_employee.salary)
        
       else:
          return False
       
        