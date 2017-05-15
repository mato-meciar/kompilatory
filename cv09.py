from Tkinter import *
from math import *
from idlelib.ColorDelegator import prog
import os
from _threading_local import local
import code




NOTHING = 0
NUMBER = 1
WORD = 2
SYMBOL = 3

globalMemory = list()
localMemory = list()

globalNamespace = dict()
localNamespace = dict()
globalVariableAdr = None


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
        self.kind = ''
        self.previousToken = ''
        self.color = 'black'
        self.table = 16 * [None]
        
        for i in range(16):
            self.table[i] = self.compile_other
            
        self.table[self.hash('vypis')] = self.compile_print
        self.table[self.hash('dopredu')] = self.compile_forward
        self.table[self.hash('vlavo')] = self.compile_left
        self.table[self.hash('vpravo')] = self.compile_right
        self.table[self.hash('opakuj')] = self.compile_repeat
        self.table[self.hash('ak')] = self.compile_if
        self.table[self.hash('kym')] = self.compile_while
        self.table[self.hash('definuj')] = self.compile_define
            
    def hash(self, text):
        return (8 * ord(text[0]) + ord(text[1])) % 16 
        
    def next(self):
        if self.index >= len(self.input):
            self.look = '\0'
        else:
            self.look = self.input[self.index]
            self.index += 1
            
    def scan(self):
        self.previousToken = self.token
        self.kind = NOTHING
        while self.kind == NOTHING and self.look != '':
            if self.look == ' ' or self.look == os.linesep:
                self.next()
            elif self.look.isalpha():
                self.token += self.look
                self.next()
                while self.look.isalpha():
                    self.token += self.look
                    self.next()
                self.kind = WORD
            elif self.look.isdigit():
                self.token += self.look
                self.next()
                while self.look.isdigit():
                    self.token += self.look
                    self.next()
                if self.look == '.':
                    self.token += self.look
                    self.next()
                    while self.look.isdigit():
                        self.token += self.look
                        self.next()
                    self.kind = NUMBER
                while self.look.isdigit():
                    self.token += self.look
                    self.next()
            elif self.look == '/':
                self.next()
                if self.look == '/':
                    while self.look not in [os.linesep, '']:
                        self.next()
                else:
                    self.token = '/'
                    self.kind = SYMBOL
            elif self.look in ['<', '>']:
                self.token = self.look
                self.next()
                if self.look == '=':
                    self.token += '='
                    self.next()
                self.kind = SYMBOL
            else:
                self.token = self.look
                self.next()
                self.kind = SYMBOL

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
        
    def operand(self):
        if self.kind == NUMBER:
            result = Const(float(self.token))
            self.scan()
        elif self.kind == WORD:
            if not localNamespace and self.token in localNamespace:
                result = Access(localNamespace[self.token])
            elif self.token in globalNamespace:
                id = globalNamespace[self.token]
                if isinstance(id, Variable):
                    raise Exception('Zla premenna!')
                result = Access(id)
            else:
                raise Exception('Neznama premenna!')
            self.scan()
        elif self.token == '(':
            self.scan()
            result = Expression(result)
            if self.token != ')':
                raise Exception('Problem so )!')
            self.scan()
        else:
            raise Exception('Cislo alebo nazov premennej!')
        return result
        
    def minus(self):
        if self.token == '-':
            self.scan()
            return -self.operand()
        elif self.token == '@':
            self.scan()
            return sqrt(self.operand())
        else:
            return self.operand()
    
    def muldiv(self):
        result = self.minus()
        while self.token != '':
            if self.token == '*':
                self.scan()
                result *= self.minus()
            elif self.token == '/':
                self.scan()
                result /= self.minus()
            elif self.token == '^':
                self.scan()
                result = pow(result, self.minus())
            else:
                return result
        return result
    
    def addsub(self):
        result = self.muldiv()
        while self.token != '':
            if self.token == '+':
                self.scan()
                result += self.muldiv()
            elif self.token == '-':
                self.scan()          
                result -= self.muldiv()
            else:
                return result
        return result
    
    def compare(self):
        result = self.addsub()
        while self.token != '':
            if self.token == '<':
                self.scan()
                if result < self.addsub():
                    return 1
                else:
                    return 0
            elif self.token == '>':
                self.scan()
                if result > self.addsub():
                    return 1
                else:
                    return 0
            else:
                return result
        return result
    
    def eqdiff(self):
        result = self.compare()
        while self.token != '':
            if self.token == '=':
                self.scan()
                if result == self.compare():
                    return 1
                else:
                    return 0
            elif self.token == '#':
                self.scan()
                if result != self.compare():
                    return 1
                else:
                    return 0
            else:
                return result
        return result
    
    def nott(self):
        if self.token != '!':
            return self.eqdiff()
        else:
            self.scan()
            if not self.eqdiff():
                return 1
            else:
                return 0
            
    def andd(self):
        result = self.nott()
        while self.token != '':
            if self.token == '&':
                self.scan()
                if result and self.nott():
                    return 1
                else:
                    return 0
            else:
                return result
        return result
    
    def orr(self):
        result = self.andd()
        while self.token != '':
            if self.token == '\\':
                self.scan()
                if result or self.nott():
                    return 1
                else:
                    return 0
            else:
                return result
        return result
    
    def evaluate(self, text):
        self.input = text
        self.index = 0
        self.next()
        self.scan()
        return self.orr()
    
    def graph(self, equation, canvas):
        self.x = -200
        x = -200
        step = 0.01
        while x <= 200:
            self.x = x
            y1 = -self.evaluate(equation)
            x += step
            self.x = x
            y2 = -self.evaluate(equation)
            canvas.create_line(x+int(canvas.cget('width')) / 2, y1+int(canvas.cget('height')) / 2, x+1+int(canvas.cget('width')) / 2, y2+int(canvas.cget('height')) / 2)
            x += step

    def compile_other(self, result):
        return result
            
    def compile_print(self, result):
        if self.token != 'vypis':
            self.compile_other(result)
        else:
            self.scan()
            result.Add(Print(expr))
            
    def compile_forward(self):
        if self.token != 'dopredu':
            self.compile_other()
        else:
            self.scan()
            result.Add(FD(self.addsub()))
            
    def compile_left(self, result):
        if self.token != 'vlavo':
            self.compile_other(result)
        else:
            self.scan()
            result.Add(LT(self.addsub()))
            
    def compile_right(self, result):
        if self.token != 'vpravo':
            self.compile_other(result)
        else:
            self.scan()
            result.Add(RT(self.addsub()))
            
    def comile_repeat(self, result):
        if self.token != 'opakuj':
            self.compile_other()
        else:
            self.scan()
            count = self.addsub()
            if self.token == '[':
                self.scan()
                body = self.compile()
                if self.token == ']':
                    self.scan()
                result.Add(Repeat(count, body))
            
    def compile(self):       
        result = Commands()
        while self.kind == WORD:
            if len(self.token) < 2:
                self.compile_other()    
            else:
                self.table[self.hash(self.token)](result)
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


        

def get(event):
    input = event.widget.get()
    print input
    k.getInput(input)
    k.next()
    k.scan()
    print k.token
    event.widget.delete(0, 'end')
    k.interpret()
    
class Maschine(Korytnacka):
    
    def __init__(self, canvas):
        self.INSTRUCTION_FD = 1
        self.INSTRUCTION_LT = 2
        self.INSTRUCTION_RT = 3
        self.INSTRUCTION_SET = 4
        self.INSTRUCTION_LOOP = 5
        self.INSTRUCTION_JUMP = 6
        self.INSTRUCTION_PUSH = 7
        self.INSTRUCTION_REMOVE = 8
        self.INSTRUCTION_DUPLICATE = 9
        self.INSTRUCTION_PRINT = 10
        
        self.mem = 200 * [0]
        self.top = 100
        self.mem[100] = '$'
        self.pc = 0
        self.terminated = False
        self.adr = 0
        
        self.turtle = Korytnacka(canvas)
        self.turtle.zmaz()
        
    def reset(self):
        self.pc = 0
        self.terminated = False
        
    def poke(self, code):
        self.mem[self.adr] = code
        self.adr += 1

    def push(self, value):
        self.top += 1
        self.mem[self.top] = value

    def pop(self):
        value = self.mem[self.top]
        self.remove()
        return value

    def remove(self):
        self.top -= 1

    def duplicate(self):
        self.top += 1
        self.mem[self.top] = self.mem[self.top - 1]
        
    def execute(self):
        if self.mem[self.pc] == self.INSTRUCTION_FD:
            self.pc += 1
            self.turtle.dopredu(self.pop())
        elif self.mem[self.pc] == self.INSTRUCTION_LT:
            self.pc += 1
            self.turtle.vlavo(self.pop())
        elif self.mem[self.pc] == self.INSTRUCTION_RT:
            self.pc += 1
            self.turtle.vpravo(self.pop())
        elif self.mem[self.pc] == self.INSTRUCTION_SET:
            self.pc += 1
            index = self.mem[self.pc]
            self.pc += 1
            self.mem[index] = self.mem[self.pc]
            self.pc += 1
        elif self.mem[self.pc] == self.INSTRUCTION_LOOP:
            self.pc += 1
            index = self.mem[self.pc]
            self.pc += 1
            self.mem[index] = self.mem[index] - 1
            if self.mem[index] <= 0:
                self.pc += 1
            else:
                self.pc = self.mem[self.pc]
        elif self.mem[self.pc] == self.INSTRUCTION_JUMP:
            self.pc += 1
            index = self.mem[self.pc]
            self.pc = index
        elif self.mem[self.pc] == self.INSTRUCTION_PUSH:
            self.pc += 1
            value = self.mem[self.pc]
            self.push(value)
            self.pc += 1
        elif self.mem[self.pc] == self.INSTRUCTION_REMOVE:
            self.pc += 1
            self.remove()
        elif self.mem[self.pc] == self.INSTRUCTION_DUPLICATE:
            self.pc += 1
            self.duplicate()
        elif self.mem[self.pc] == self.INSTRUCTION_PRINT:
            self.pc += 1
            print self.mem[self.top]
        else:
            self.terminated = True
            
    def run(self):
        self.reset()
        while not self.terminated:
            self.execute()
    
    

master = Tk()
 
w = Canvas(master, width=600, height=400)
w.pack()
 
# e = Entry(master, width=int(w.cget('width'))/10)
# e.bind('<Return>', get)
# e.pack()
# e.focus_set()
# 
# k = Korytnacka(w)
# k.zmaz()
# k.farba(0, 0, 255)
# 
# k.getInput('opakuj 4 [dopredu 100 vpravo 90]')
# k.next()
# k.scan()
# 
# program = k.compile()
# 
# program.Execute()

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

# mainloop()

# expression = Add(Const(1), Mul(Const(2), Const(3)))
# print expression.Evaluate()



m = Maschine(w)
m.turtle.x = 50
m.adr = 0
m.poke(m.INSTRUCTION_PUSH)
m.poke(100)
m.poke(m.INSTRUCTION_FD)
m.poke(m.INSTRUCTION_PUSH)
m.poke(90)
m.poke(m.INSTRUCTION_RT)
m.poke(m.INSTRUCTION_PUSH)
m.poke(100)
m.poke(m.INSTRUCTION_FD)
m.poke(m.INSTRUCTION_PUSH)
m.poke(666)
m.poke(m.INSTRUCTION_PRINT)
# m.mem[0] = m.INSTRUCTION_PUSH
# m.mem[1] = 1
# m.mem[2] = m.INSTRUCTION_PUSH
# m.mem[3] = 2
# m.mem[4] = m.INSTRUCTION_REMOVE
# m.mem[5] = m.INSTRUCTION_PUSH
# m.mem[6] = 3
# m.mem[7] = m.INSTRUCTION_DUPLICATE
# m.run()
# print m.mem
# m.turtle.x = 50
# m.mem = 100 * [0]
# m.mem[0] = m.INSTRUCTION_SET
# m.mem[1] = 99
# m.mem[2] = 4
# m.mem[3] = m.INSTRUCTION_FD
# m.mem[4] = 100
# m.mem[5] = m.INSTRUCTION_RT
# m.mem[6] = 90
# m.mem[7] = m.INSTRUCTION_LOOP
# m.mem[8] = 99
# m.mem[9] = 3
# m.mem[10] = 0

# m.adr = 0
# m.poke(m.INSTRUCTION_SET)
# m.poke(98)
# m.poke(10)
# outer = m.adr
# m.poke(m.INSTRUCTION_SET)
# m.poke(99)
# m.poke(4)
# body = m.adr
# m.poke(m.INSTRUCTION_FD)
# m.poke(50)
# m.poke(m.INSTRUCTION_RT)
# m.poke(90)
# m.poke(m.INSTRUCTION_LOOP)
# m.poke(99)
# m.poke(body)

# m.poke(m.INSTRUCTION_RT)
# m.poke(90)
# m.poke(m.INSTRUCTION_FD)
# m.poke(51)
# m.poke(m.INSTRUCTION_LT)
# m.poke(90)
# m.poke(m.INSTRUCTION_LOOP)
# m.poke(98)
# m.poke(outer)


m.run()

mainloop()
