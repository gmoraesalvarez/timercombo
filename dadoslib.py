from machine import Pin, I2C
import machine
import ssd1306
#import ssd1306big
from rotary_irq_esp import RotaryIRQ
from random import getrandbits
from random import seed
from time import sleep
from time import time
import framebuf

rotary = True

i2c = I2C(sda=Pin(4), scl=Pin(5)) # D2 D1
display = ssd1306.SSD1306_I2C(128, 64, i2c)

p12 = Pin(12, Pin.IN, Pin.PULL_UP) #D6
p13 = Pin(13, Pin.IN, Pin.PULL_UP) #D7
p14 = Pin(14, Pin.IN, Pin.PULL_UP) #D5
p2 = Pin(2, Pin.IN, Pin.PULL_UP)	#D4
p0 = Pin(0, Pin.IN)					#D3

if (rotary):
    increment = 10
    r = RotaryIRQ(pin_num_clk=14, 
                  pin_num_dt=13, 
                  min_val=-1, 
                  max_val=1, 
                  reverse=False, 
                  half_step=True,
                  range_mode=RotaryIRQ.RANGE_BOUNDED)                  
    r.set(value = 0)
incdec = 0

timepast = 0
pausetime = 0

starttime = time()
sleeptimer = time()

size = [4,4,4,4,4,4]
idx = 0

display.fill(0)
display.text('gma DADOS_pb v0.92',20,28,1)
display.show()

def gotobed(p):
    display.fill(0)
    display.text('Au Revoir',56,28,1)
    display.show()
    sleep(2)
    display.fill(0)
    display.show()
    machine.deepsleep()
    
def prep_D():
    global size
    global idx
    print("load conf D")
    file = open("cfgD.txt", "r")
    cfg = file.read()
    file.close()
    size_str = cfg.split(',', 6)
    size[0] = int(size_str[0])
    size[1] = int(size_str[1])
    size[2] = int(size_str[2])
    size[3] = int(size_str[3])
    size[4] = int(size_str[4])
    size[5] = int(size_str[5])
    idx = 0
    run_dice()

def reshuf():
    bits = 3
    for i in [0,1,2,3,4,5]:
        seed()
        bits = (size[i]+2)//2
        num = getrandbits(bits)
        while num < 1 or num > size[i]:
            num = getrandbits(bits)
        drawDie(i,num)

def drawDieConfig(position):
    #display.fill(0)
    drawDie(position,size[position])
    if position == idx:
        if position == 0:
            offsetx = 0
            offsety = 0
        if position == 1:
            offsetx = 44
            offsety = 0
        if position == 2:
            offsetx = 88
            offsety = 0
        if position == 3:
            offsetx = 0
            offsety = 32
        if position == 4:
            offsetx = 44
            offsety = 32
        if position == 5:
            offsetx = 88
            offsety = 32

        #display.fill_rect(offsetx, offsety, 12, 12, 0)
        #display.text("*",2+offsetx,2+offsety,1)
        display.rect(offsetx, offsety, 41, 31, 1)
        display.show()

def drawDie(position,value):
    if position == 0:
        offsetx = 0
        offsety = 0
    if position == 1:
        offsetx = 44
        offsety = 0
    if position == 2:
        offsetx = 88
        offsety = 0
    if position == 3:
        offsetx = 0
        offsety = 32
    if position == 4:
        offsetx = 44
        offsety = 32
    if position == 5:
        offsetx = 88
        offsety = 32

    if size[position] in [4,6,8,10,12,20]:
        printDado(size[position],value,offsetx,offsety)
    else:
        display.fill_rect(2+offsetx, 4+offsety, 42, 32, 0)
        display.rect(2+offsetx, 4+offsety, 32, 28, 1)
        display.text(str(value),15+offsetx,15+offsety,1)
        display.show()

def cycleDieSides(p):
    global size
    global sleeptimer
    sleeptimer = time()
    size[idx] += 1
    if size[idx] == 5: size[idx] = 6
    if size[idx] == 7: size[idx] = 8
    if size[idx] == 9: size[idx] = 10
    if size[idx] == 11: size[idx] = 12
    if size[idx] in [13,14,15,16,17,18,19]: size[idx] = 20
    if size[idx] >= 21: size[idx] = 4
    drawDieConfig(idx)

def cycleDie(p):
    global idx
    global size
    global sleeptimer
    sleeptimer = time()
    save_cfg()
    idx += 1
    if idx >= 6: idx = 0
    for i in [0,1,2,3,4,5]:
        drawDieConfig(i)


def printDado(size,side,x,y):
    print("display image")
    img = "d"
    img += str(size)
    img += "l"
    img += str(side)
    img += ".pbm"
    with open(img,'rb') as f:
        f.read(83) # header data
        data = bytearray(f.read())
    fbuf = framebuf.FrameBuffer(data, 41, 31, framebuf.MONO_HLSB)
    #display.invert(1)
    display.blit(fbuf, x, y)
    display.show()

def diceExec():
    global incdec
    
    if (rotary):
        #incdec = -1
        r_new = r.value()
        if r_new != 0:
            #r_last = r_new
            #print('result =', r_new)
            if (r_new == 1):
                print("rotary move up")
                incdec = 1
            if (r_new == -1):
                print("rotary move down")
                incdec = -1
            r.set(value = 0)
            #sleep(0.15)
    else:
        #incdec = -1
        if p2.value() == 0:
            incdec = -1
            sleep(0.1)
        if p14.value() == 0:
            incdec = 1
            sleep(0.1)
    #print("running")
    if p12.value() == 0:
        run_dice()
        print("runDice")
        sleep(0.15)
    if incdec == 1:
        cycleDie(0)
        print("cycleDie")
        incdec = 0      
    if incdec == -1:
        cycleDieSides(0)
        print("cycleDieSides")
        incdec = 0
    
    if (time() - sleeptimer) > 60:
        gotobed(0)

def save_cfg():
    file = open("cfgD.txt", "w")
    cfg = ','.join(str(x) for x in size)
    file.write(cfg)
    file.close()

def run_dice():
    display.fill_rect(0, 0, 127, 63, 0)
    reshuf()
    sleeptimer = time()
