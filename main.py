from machine import Pin, I2C
#import machine
import ssd1306

import framebuf
import network
#import gc

#gc.enable()
#gc.mem_alloc()
# using default address 0x3C
i2c = I2C(sda=Pin(4), scl=Pin(5)) # D2 D1
display = ssd1306.SSD1306_I2C(128, 64, i2c)

display.fill(0)
display.text('Oi! : )',56,28,1)
display.show()

isDice = False
isChrono = False

file = open("isDice.txt", "r")
isit = file.read()
file.close()
if (isit == "1"): isDice = True
if (isit == "2"): isChrono = True
##########################################
##########################################
##########################################


if (isChrono):
    print("it is chrono")
    import chronolib
    chronolib.prep_C()
    file = open("isDice.txt", "w")
    file.write("0")
    file.close()
elif (isDice):
    print("it is dice")
    import dadoslib
    dadoslib.prep_D()
    file = open("isDice.txt", "w")
    file.write("0")
    file.close()
else:
    display.fill(0)
    display.text('Oi! :-)',56,28,1)
    display.show()
    print("it is timer")
    import timerlib
    timerlib.prep_T()

####################################################

sta_if = network.WLAN(network.STA_IF)
sta_if.active(False)
ap_if = network.WLAN(network.AP_IF)
ap_if.active(False)


while True:
    if (isChrono):
    	chronolib.chronoExec()
    elif (isDice):
    	dadoslib.diceExec()
    else:
    	timerlib.timerExec()     
