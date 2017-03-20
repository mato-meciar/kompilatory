from Tkinter import *
from math import *
from idlelib.ColorDelegator import prog

class Korytnacka:
    
    def __init__(self, canvas, x=300, y=200, heading=0):
        self.canvas = canvas
        self.heading = heading
        self.x = x
        self.y = y
        self.input = ''
        self.index = 0
        self.look = ''
        self.token = ''
        self.previousToken = ''
        self.color = 'black'
        
    def next(self):
        if self.index >= len(self.input):
            self.look = '\0'
        else:
            self.look = self.input[self.index]
            self.index += 1
            
    def scan(self):
        self.previousToken = self.token
        while self.look == ' ':
            self.next()
        self.token = ''
        self.position = self.index - 1
        if self.look.isalpha() or self.look == '*':
            self.token += self.look
            self.next()
            while self.look.isalpha():
                self.token += self.look
                self.next()
        elif self.look.isdigit():
            self.token += self.look
            self.next()
            while self.look.isdigit():
                self.token += self.look
                self.next()
        elif self.look != '\0':
            self.token = self.look
            self.next()  

    def interpret(self):
        while True:
            if self.token in ('dopredu', 'dp') :
                self.scan()
                try:
                    self.dopredu(int(self.token))
                except ValueError:
                    raise Exception('Zly vstup: "' + self.token + '"')
                self.scan()
            elif self.token in ('vlavo', 'vl'):
                self.scan()
                try:
                    self.vlavo(int(self.token))
                except ValueError:
                    raise Exception('Zly vstup: "' + self.token + '"')    
                self.scan()
            elif self.token in ('vpravo', 'vp'):
                self.scan()
                try:
                    self.vpravo(int(self.token))
                except ValueError:
                    raise Exception('Zly vstup: "' + self.token + '"')
                self.scan()
            elif self.token in ('opakuj', '*'):
                if self.token == '*':
                    self.count = int(self.previousToken)
                else:
                    self.scan()
                    try:
                        self.count = int(self.token)
                    except ValueError:
                        raise Exception('Zly vstup: "' + self.token + '"')
                self.scan()
                if self.token == '[':
                    self.scan()
                    start = self.position
                    while self.count > 0:
                        self.index = start
                        self.next()
                        self.scan()
                        self.interpret()
                        self.count -= 1
                if self.token == ']':
                    self.scan()
            elif self.token.isdigit():
                self.scan()
            elif self.position == len(self.input) - 1:
                break
            else:
                raise Exception('Neznamy prikaz: "' + self.token + '"')
        
    def number(self):
        result = Const(int(self.token))
        self.scan()
        return result
    
    def muldiv(self):
        result = self.number()
        while True:
            if self.token == '*':
                self.scan()
                result = Mul(result, self.number())
            elif self.token == '/':
                self.scan()
                result = Div(result, self.number())
            else:
                return result
            
    def addsub(self):
        result = self.muldiv()
        while True:
            if self.token == '+':
                self.scan()
                result = Add(result, self.muldiv())
            elif self.token == '-':
                self.scan()
                result = Sub(result, self.muldiv())
            else:
                return result
            
    def compile(self):       
        result = Commands()
        while True:
            if self.token == 'dopredu':
                self.scan()
                result.Add(FD(self.addsub()))
            elif self.token == 'vlavo':
                self.scan()
                result.Add(LT(self.addsub()))
            elif self.token == 'vpravo':
                self.scan()
                result.Add(RT(self.addsub()))
            elif self.token == 'opakuj':
                self.scan()
                count = self.addsub()
                if self.token == '[':
                    self.scan()
                    body = self.compile()
                    if self.token == ']':
                        self.scan()
                    result.Add(Repeat(count, body))
            else:
                return result
            
    def getInput(self, input):
        self.input = input
        self.index = 0
        self.token = ''
        self.previousToken = ''
        self.look = ''

    def dopredu(self, kolko):
        newX = self.x + cos(radians(self.heading)) * kolko
        newY = self.y + sin(radians(self.heading)) * kolko
        self.canvas.create_line(self.x, self.y, newX, newY, fill=self.color)
        self.x = newX
        self.y = newY
        
    def zmaz(self):
        self.canvas.delete('all')
        self.x = int(self.canvas.cget('width')) / 2
        self.y = int(self.canvas.cget('height')) / 2
        self.heading = -90
        self.color = 'black'
        
    def farba(self, r, g, b):
        if r > 255:
            r = 255
        if g > 255:
            g = 255
        if b > 255:
            b = 255
        self.color = str('#%02x%02x%02x' % (r, g, b))
        
    def bod(self, polomer):
        self.canvas.create_oval(self.x - polomer, self.y - polomer, self.x + polomer, self.y + polomer, fill=self.color, outline=self.color)

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
          
class Expression:
    
    def Evaluate(self):
        return 0
    
class Const(Expression):
    
    def __init__(self, nValue):
        self.Value = nValue
        
    def Evaluate(self):
        return self.Value
    
class BinaryOperation(Expression):
    
    def __init__(self, nL, nR):
        self.L = nL
        self.R = nR
        
class Add(BinaryOperation):
    
    def Evaluate(self):
        return self.L.Evaluate() + self.R.Evaluate()
    
class Sub(BinaryOperation):
    
    def Evaluate(self):
        return self.L.Evaluate() - self.R.Evaluate()
    
class Mul(BinaryOperation):
    
    def Evaluate(self):
        return self.L.Evaluate() * self.R.Evaluate()
    
class Div(BinaryOperation):
    
    def Evaluate(self):
        return self.L.Evaluate() / self.R.Evaluate()
                
class Command:
    
    def Execute(self):
        pass
    
class Commands(Command):
    
    def __init__(self, *arg):
        self.Items = list(arg)
        
    def Add(self, Item):
        self.Items.append(Item)
        
    def Execute(self):
        for Item in self.Items:
            Item.Execute()
            
class TurtleCommand(Command):
    
    def __init__(self, nParam):
        self.Param = nParam
        
class FD(TurtleCommand):
    
    def Execute(self):
        k.dopredu(self.Param.Evaluate())
        
class LT(TurtleCommand):
    
    def Execute(self):
        k.vlavo(self.Param.Evaluate())
        
class RT(TurtleCommand):
    
    def Execute(self):
        k.vpravo(self.Param.Evaluate())
        
class Repeat(Command):
    
    def __init__(self, nCount, nBody):
        self.Count = nCount
        self.Body = nBody
        
    def Execute(self):
        n = self.Count.Evaluate()
        while n > 0:
            self.Body.Execute()
            n -= 1
        

def get(event):
    input = event.widget.get()
    print input
    k.getInput(input)
    k.next()
    k.scan()
    print k.token
    event.widget.delete(0, 'end')
    k.interpret()

master = Tk()

w = Canvas(master, width=600, height=400)
w.pack()

e = Entry(master, width=int(w.cget('width'))/10)
e.bind('<Return>', get)
e.pack()
e.focus_set()

k = Korytnacka(w)
k.zmaz()
k.farba(0, 0, 255)

k.getInput('opakuj 4 [dopredu 100 vpravo 90]')
k.next()
k.scan()

program = k.compile()

program.Execute()

# program = Repeat(
#     Const(4),
#     Commands(FD(Const(100)), RT(Const(90))))
# 
# program.Execute()

# k = Korytnacka(w)
# k.zmaz()
# k.farba(0, 0, 255)
# k.getInput('opakuj 4 [dp 100 vp 90]')
# k.next()
# k.scan()
#  
# k.interpret()
# k.bod(25)
# k.x = 20
# k.y = 400
# k.kresli('dld*ppd*ld', 60, 99, 0.5)



mainloop()






# expression = Add(Const(1), Mul(Const(2), Const(3)))
# print expression.Evaluate()