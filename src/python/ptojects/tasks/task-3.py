from abc import ABC,abstractmethod
class Animal(ABC):
    @abstractmethod
    def make_sound(self):
        pass
    def describe(self):
        print('This is an Animal')
class Dog(Animal):
    def make_sound(self):
        return "woof"
    
class Cat(Animal):
    def make_sound(self):
       return "Meow"
   
class Cow(Animal):
    def make_sound(self):
        return "Moo"
   
x1=Dog()
x2=Cat()
x3=Cow()
x1.describe() 
print(x1.make_sound())
x2.describe() 
print(x2.make_sound())
x3.describe() 
print(x3.make_sound())

