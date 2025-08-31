from subtask1 import Employee
if __name__ == '__main__':
    boss = Employee('Jane Redmond', {})
    name = 'John Smith'
    family = {
        'Son': {
            'Insured': True,
            'Age': 16
        },
        'Wife':{
            'Insured': False,
            'Age': 32
        }
    }
    my_employee = Employee(name, family, boss)
    not_boss = Employee('Adam Cater', {})
    print(id(my_employee.family))
    print(id(my_employee._family))
    boss.apply_raise(my_employee, 25)
    print(not_boss.apply_raise(my_employee, 25))

     