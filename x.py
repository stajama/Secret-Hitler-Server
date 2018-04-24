from server import models

def initializeDBwithSomething():
    x = models.Player(name="test")
    x.save()

if __name__ == '__main__':
    initializeDBwithSomething()