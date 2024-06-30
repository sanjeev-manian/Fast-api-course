class lives:
    def talk(self):
        print("tak")


class animal(lives):
    weight: int
    animal_type: str
    age: int

    def __init__(self, age: int) -> None:
        self.age = age

    def talk(self):
        super().talk()
        print("talking")
