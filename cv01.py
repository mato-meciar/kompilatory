from Tkinter import *
from math import *

class Korytnacka:
    
    def __init__(self, canvas, x=300, y=200, heading=0):
        self.canvas = canvas
        self.heading = heading
        self.x = x
        self.y = y
        self.input = ''
        self.index = 0
        self.look = ''
        
    def next(self):
        if self.index >= len(self.input):
            self.look = '\0'
        else:
            self.look = self.input[self.index]
            self.index += 1
            
    def scan(self):
        pass
            
    def getInput(self, input):
        self.input = input

    def dopredu(self, kolko):
        newX = self.x + cos(radians(self.heading)) * kolko
        newY = self.y + sin(radians(self.heading)) * kolko
        self.canvas.create_line(self.x, self.y, newX, newY)
        self.x = newX
        self.y = newY

    def vpravo(self, uhol):
        self.heading += uhol

    def vlavo(self, uhol):
        self.heading -= uhol

    def kresli(self, text, uhol, krok, zmena):
        for char in text:
            if krok < 1:
                return
            elif char == 'd':
                self.dopredu(krok)
            elif char == 'c':
                self.dopredu(-krok)
            elif char == 'l':
                self.vlavo(uhol)
            elif char == 'p':
                self.vpravo(uhol)
            elif char == '*':
                self.kresli(text, uhol, krok * zmena, zmena)

master = Tk()

w = Canvas(master, width=600, height=400)
w.pack()

k = Korytnacka(w)
k.getInput('dopredu 100 vlavo 90')
while k.look != '\0':
    print k.look
    k.next()



mainloop()


def uloha1(input):
    words = len(input.split())
    spaces = input.count(' ')
    other = 0
    for char in input:
        if not char.isalpha() and not char.isspace():
            other += 1
    return 'subor obsahuje ' + str(words) + ' slov, ' + str(spaces) + ' medzier a ' + str(other) + ' inych znakov'


# print uloha1("Dobry den,\na ako sa dnes mate?")
