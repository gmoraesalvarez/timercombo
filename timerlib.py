from machine import Pin, I2C, PWM
import machine
import ssd1306
from rotary_irq_esp import RotaryIRQ
from time import sleep
from time import sleep_ms
from time import ticks_ms
from time import ticks_diff
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
buzz = PWM(p0)
buzz.freq(0)
buzz.duty(0)

increment = 30
if (rotary):
    increment = 15
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
runnin = False
text = ""
buzzstart = True
tock = 0
line_pos = -5
buzz_ms = ticks_ms()
buzz_tock = 0
sleeptimer = time()
due = False

size = [4,4,4,4,4,4]
idx = 0

display.fill(0)
display.text('gma TIMER v0.92',20,28,1)
display.show()

def resetDice():
    file = open("isDice.txt", "w")
    file.write("1")
    file.close()
    #import sys
    #sys.exit()
    import machine
    machine.reset()

def resetChrono():
    file = open("isDice.txt", "w")
    file.write("2")
    file.close()
    #import sys
    #sys.exit()
    import machine
    machine.reset()

def prep_T():
    global size
    global remain
    global timepast
    global idx
    
    print("load conf T")
    file = open("cfg.txt", "r")
    cfg = file.read()
    file.close()
    size_str = cfg.split(',', 3)
    size[0] = int(size_str[0])
    size[1] = int(size_str[1])
    size[2] = int(size_str[2])
    remain = size[idx] - timepast
    set_index_str()
    show()

def startpause():
    global runnin
    global starttime
    global pausetime
    global timepast
    global line_pos
    global sleeptimer
    global size
    global idx
    global isDice
    
    
    line_pos = -5
    starttime = time()
    buzz.duty(0)
    if runnin:
        runnin = False
        pausetime = timepast
    else:
        if rotary: save_cfg()
        if (size[idx] == 3570): resetDice()
        if (size[idx] == 3585): resetChrono()
        runnin = True
        starttime -= pausetime

            
def reset():
    global idx
    global pausetime
    global remain
    global due
    if pausetime > 0:
        pausetime = 0
        due = False
    else:
        #die_index += 1
        #if die_index >= 6: die_index = 0
        #set_index_str()
        save_cfg()
    remain = size[idx]
    

def silence():
    buzz.duty(0)
    
def set_index_str():
    global idx
    global index_str
    if idx == 0:
            index_str = "A"
    if idx == 1:
            index_str = " B"
    if idx == 2:
            index_str = "  C"


def scream(ms):
    buzz.duty(0)
    
    if ms in [1,2,3,31,32,33]:
        buzz.freq(600)
        buzz.duty(512)
    if ms in [7,8,37,38]:
        buzz.freq(800)
        buzz.duty(512)
    if ms in [11,12,41,42]:
        buzz.freq(900)
        buzz.duty(512)
    
def inc():
    size[idx] += increment
    if size[idx] >= 3600: size[idx] = 0
    
    
def dec():
    size[idx] -= increment
    if size[idx] < 0: size[idx] = 3600
    

    
def time_to_str(seconds):
    min = seconds // 60
    sec = seconds % 60
    string = "%02d" % min
    string += ":"
    string += "%02d" % sec
    return string


def time_to_7seg(seconds):
    min = seconds // 60
    sec = seconds % 60

    min_0 = min // 10
    draw_7seg(4, 32, min_0)

    min_1 = min % 10
    draw_7seg(24, 32, min_1)

    display.vline(42,40,2,1)
    display.vline(42,44,2,1)
    
    sec_0 = sec // 10
    draw_7seg(46, 32, sec_0)
        
    sec_1 = sec % 10
    draw_7seg(66, 32, sec_1)
        
    
    
def draw_7seg(x,y,num_):

    num = abs(num_)
                        #A  B  C  D  E  F  G
    if num == 0: segs = [1, 1, 1, 0, 1, 1, 1]
    if num == 1: segs = [0, 0, 0, 0, 0, 1, 1]
    if num == 2: segs = [0, 1, 1, 1, 1, 1, 0]
    if num == 3: segs = [0, 0, 1, 1, 1, 1, 1]
    if num == 4: segs = [1, 0, 0, 1, 0, 1, 1]
    if num == 5: segs = [1, 0, 1, 1, 1, 0, 1]
    if num == 6: segs = [1, 1, 1, 1, 1, 0, 1]
    if num == 7: segs = [0, 0, 1, 0, 0, 1, 1]
    if num == 8: segs = [1, 1, 1, 1, 1, 1, 1]
    if num == 9: segs = [1, 0, 1, 1, 1, 1, 1]
    
    display.vline(x,y,8,segs[0])
    display.vline(x,y+12,8,segs[1])    
    display.hline(x+3,y-1,8,segs[2])
    display.hline(x+3,y+10,8,segs[3])
    display.hline(x+3,y+20,8,segs[4])
    display.vline(x+12,y,8,segs[5])
    display.vline(x+12,y+12,8,segs[6])

def draw_7seg_s(x,y,num_,size):

    num = abs(num_)
                        #A  B  C  D  E  F  G
    if num == 0: segs = [1, 1, 1, 0, 1, 1, 1]
    if num == 1: segs = [0, 0, 0, 0, 0, 1, 1]
    if num == 2: segs = [0, 1, 1, 1, 1, 1, 0]
    if num == 3: segs = [0, 0, 1, 1, 1, 1, 1]
    if num == 4: segs = [1, 0, 0, 1, 0, 1, 1]
    if num == 5: segs = [1, 0, 1, 1, 1, 0, 1]
    if num == 6: segs = [1, 1, 1, 1, 1, 0, 1]
    if num == 7: segs = [0, 0, 1, 0, 0, 1, 1]
    if num == 8: segs = [1, 1, 1, 1, 1, 1, 1]
    if num == 9: segs = [1, 0, 1, 1, 1, 1, 1]
    
    display.vline(x,y,size,segs[0])
    display.vline(x,y+2+size,size,segs[1])    
    display.hline(x+(size//4),y-1,size,segs[2])
    display.hline(x+(size//4),y+2+size,size,segs[3])
    display.hline(x+(size//4),y+4+size+size,size,segs[4])
    display.vline(x+(size//2)+size,y,size,segs[5])
    display.vline(x+(size//2)+size,y+4+size,size,segs[6])

    
def save_cfg():
    file = open("cfg.txt", "w")
    cfg = ','.join(str(x) for x in size)
    file.write(cfg)
    file.close()



def show():
    display.fill(0)
    timer_time_str = ""
    timer_time_str += time_to_str(size[idx])
    #timer_time_str += "|"
       
    display.text(timer_time_str,82,2,1)
    #display.text(index_str,2,2,1)
    #if buzzstart: display.text("***",110,56,1)
    if (size[idx] == 3585):
        display.text('CRONOMETRO',14,28,1)
    elif (size[idx] == 3570):
        display.text('JOGAR DADOS!!!',14,28,1)
    else:
        time_to_7seg(remain)
    
    display.hline(line_pos,60,4,1)
    display.show()

def gotobed(p):
    display.fill(0)
    display.text('Au Revoir',56,28,1)
    display.show()
    sleep(2)
    display.fill(0)
    display.show()
    machine.deepsleep() 
###################################################
###################################################

def timerExec():
    global tock
    global buzz_tock
    global buzz_ms
    global buzzstart
    global pausetime
    global timepast
    global starttime
    global sleeptimer
    global remain
    global due
    global size
    global idx
    global line_pos
    global r
    global incdec
    global r_last

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
            sleep(0.05)
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
        startpause()
        print("startpause")
        sleep(0.15)
        show()
    #if p13.value() == 0:
     #   cycleTimer()
      #  print("cycleDieSides")
       # sleep(0.1)
    if incdec == 1:
        if pausetime > 0:
            reset()
        else:
            if not runnin:
                inc()
                remain = size[idx]
                if not rotary: save_cfg()
                print("more")
        incdec = 0
        show()
        #sleep(0.1)
    if incdec == -1:
        if pausetime > 0:
            reset()
        else:
            if not runnin:
                dec()
                remain = size[idx]
                if not rotary: save_cfg()
                print("less")
        incdec = 0
        show()
        #sleep(0.1)
    if runnin:
        sleeptimer = time()
        if ticks_diff(ticks_ms(), tock) > 16:
            line_pos += 8
            tock = ticks_ms()
        if line_pos > 127:
            line_pos = 0
        timepast = time() - starttime
        remain = size[idx] - timepast
        if remain == 0:
            buzzstart = True
            due = True
            starttime = time()      
        if buzzstart:
            if ticks_diff(ticks_ms(), buzz_ms) > 16:
                buzz_tock += 1
                buzz_ms = ticks_ms()
            if buzz_tock > 60:
                buzz_tock = 0
            scream(buzz_tock)
        if due:
            remain = timepast
        show()
    else:
        silence()
        buzzstart = False
        if pausetime == 0:
                    #if ((time() - sleeptimer) % 2) == 0: print("counting down to sleep")
                    if (time() - sleeptimer) > 120:
                        gotobed(0) 
        #show()
