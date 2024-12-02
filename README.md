# Graduation Cap
This is a PCB that I made to sit on top of my graduation cap for my bachelor's in electrical engineering. The board is designed around the 9.5x9.5" Herff Jones caps used at UF, but it could easily be adapted for other caps. This board is capable of playing three different `.WAV` music files, and I have populated mine with three Florida Gators fight songs. There is also an LED sequence that cycles through each light on the cap while displaying a message on the OLED display.

> ![Graduation Cap](https://github.com/user-attachments/assets/597564c8-0d75-4274-ba00-1ea601e1696a)
> Side-by-side of the PCB render in KiCad and the board on my cap in real life.

# Project Inspirations

While I have had this project on my mind for a few years now, there are some people that have made similar projects, and I modeled some of my work off of theirs.

1. [LED Graduation Cap](https://github.com/matthewScohen/LED_Graduation_Cap) by Matthew Cohen

2. [Graduation Cap](https://github.com/miekush/graduation-cap) by Mike Kushnerik

Notably, Mike's project has accommodations for the tassel, which I overlooked and ended up just hot gluing onto my cap. The PCB itself is also hot glued at each of the cap's four corners.

# Code

The program to run this board is included in this repository as `main.py`, and it was designed around a Raspberry Pi Pico running MicroPython (yes, I know C would have run better, no I am not good at writing code). You will need the following driver files saved to the Pico in order for the code to run.

1. [sdcard.py](https://github.com/micropython/micropython-lib/blob/master/micropython/drivers/storage/sdcard/sdcard.py) from [micropython-lib](https://github.com/micropython/micropython-lib)

2. [sh1106.py](https://github.com/raspberrypi/pico-micropython-examples/blob/master/i2c/1106oled/sh1106.py) from [Pico MicroPython Examples](https://github.com/raspberrypi/pico-micropython-examples)

3. [tlc5940.py](https://github.com/sabogalc/tlc5940-micropython/blob/master/tlc5940.py) from [TLC5940 MicroPython Library](https://github.com/oysols/tlc5940-micropython)**

** **Please note that the code does not currently work on the Pico. I have linked to my fork of the driver which does work on the Pico and has been submitted as a pull request.**

4. [wavplayer.py](https://github.com/miketeachman/micropython-i2s-examples/blob/master/examples/wavplayer.py) from [MicroPython I2S Examples](https://github.com/miketeachman/micropython-i2s-examples)

# Ordering Parts

I have included BOMs for both DigiKey and Mouser to obtain the parts for this board, but the Mouser BOM is missing the socket headers since I could not find any on there. The board will still work with the components directly soldered down, but I liked the flexibility the sockets offered, especially while debugging. One component that will be needed to be purchased externally is the I2C OLED, and I got mine [on Amazon](https://www.amazon.com/dp/B07BHHV844).

# Notes

I wanted to have a mode where all the lights could come on at once, but I was unable to accomplish this without prominent flickering. I believe this may be due to differences in the forward voltages of the blue and orange LEDs, as the flicker does not occur when only lighting multiple LEDs of one color (side note, the blue LED was [partially invented at UF](https://www.nobelprize.org/prizes/physics/2014/nakamura/biographical/#:~:text=In%20March%201988%20Shuji%20flew%20to%20Gainesville.%20It%20was%20the%20first%20time%20the%20country%20boy%20had%20boarded%20an%20airplane.%20Like%20many%20first%2Dtime%20fliers%2C%20he%20feared%20it%20might%20fall%20from%20the%20sky.%20It%20was%20also%20his%20first%20trip%20abroad.%20He%20worried%20that%20his%20rudimentary%20English%20would%20not%20enable%20him%20to%20communicate%20with%20Americans.)!). If anyone has more information on this, please feel free to share it.

Another thing to note is that I had to cut a hole in my cap so that the battery leads were accessible, but if you wanted to power the board with a USB cable and a power bank that should work as well.

While the board is personalized to me and my graduation year, it can be modified to any year, school, or person. Of course, most of the fun in making something like this is in designing it yourself, so feel free to use this project in part or in whole to help move your project along.

> ![Graduation Picture](https://github.com/user-attachments/assets/30cfc325-f744-46fe-8498-26e7644956cf)
> Me with my graduation cap outside of UF's New Engineering Building (it's not that new but the name has stuck).