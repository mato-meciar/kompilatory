import math
from math import sqrt
from Tkinter import *

class Vyraz:
    
    def next(self):
        if self.index >= len(self.input):
            self.look = '\0'
        else:
            self.look = self.input[self.index]
            self.index += 1
            
    def scan(self):
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
        elif self.look == '!':
            self.token = '!'
            self.next()
        elif self.look == '&':
            self.token = '&'
            self.next()
        elif self.look != '\0':
            self.token = self.look
            self.next()
            
    def number(self):
        if self.token == 'x':
            self.scan()
            return self.x
        else:
            try:
                result = int(self.token)
                self.scan()
                return result
            except ValueError:
                raise Exception('chyba cislo alebo neznama x')
    
    def braces(self):
        if self.token != '(' and self.token != '[':
            return self.number()
        else:
            self.scan()
            result = self.orr()
            if self.token == ')':
                self.scan()
                return result
            elif self.token == ']':
                self.scan()
                return abs(result)
        
    def minus(self):
        if self.token == '-':
            self.scan()
            return -self.braces()
        elif self.token == '@':
            self.scan()
            return sqrt(self.braces())
        else:
            return self.braces()
    
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
    
v = Vyraz()
print v.evaluate('-(1+2)*((3+1)*[-3])')


master = Tk()

w = Canvas(master, width=600, height=400)
w.pack()

v.graph('x ^ 2 - 200', w)

mainloop()
