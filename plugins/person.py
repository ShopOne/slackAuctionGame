class Person:
    id = ""
    name = ""
    like = ["", ""]
    money = 0

    def __eq__(self, other):
        if not isinstance(other, Person):
            return NotImplemented
        return (self.user_id == other.user_id)

    def __init__(self, uid, uname, fmoney):
        self.id = uid
        self.name = uname
        self.money = fmoney
