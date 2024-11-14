It's three in one!!!

This code runs on a micropython environment. It was made for the D1 Mini, but any esp32 will do too, I guess.
In fact, if you pull in the full rotary lib from its repo, any micropython mcu will do. Just call the correct rotary_irq_*** file.
The option between an encoder or three buttons is set with a bool variable in each of the three programs.
The default program is the timer, written in timerlib.py. From it the other two programs can be called, which causes a machine reset with the new program set to load instead of the timer. Further resets will return to the timer.

The display is ssd1306 based, as shown in the code.
