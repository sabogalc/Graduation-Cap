import os
import time
from machine import I2C, Pin, SPI
from sh1106 import SH1106_I2C
from wavplayer import WavPlayer
from sdcard import SDCard
from tlc5940 import interface, simple_byte_array

# TLC5940 GPIO pin definitions
GSCLK_PIN = 5
BLANK_PIN = 1
VPRG_PIN = 0
XLAT_PIN = 4
SCLK_PIN = 2
SIN_PIN = 3

# PMOS gate pins
PMOS_ROW1_PIN = 7
PMOS_ROW2_PIN = 6
PMOS_ROW3_PIN = 8

# Initialize the TLC5940 interface
tlc = interface(GSCLK_PIN, BLANK_PIN, VPRG_PIN, XLAT_PIN, SCLK_PIN, SIN_PIN)

# Configure PMOS pins
pmos_row1 = Pin(PMOS_ROW1_PIN, Pin.OUT)
pmos_row2 = Pin(PMOS_ROW2_PIN, Pin.OUT)
pmos_row3 = Pin(PMOS_ROW3_PIN, Pin.OUT)

# Initialize PMOS gates (turn off all rows initially)
pmos_row1.value(0)
pmos_row2.value(0)
pmos_row3.value(0)

# Initialize I2C for OLED display
i2c = I2C(0, scl=Pin(21), sda=Pin(20), freq=200000)
oled = SH1106_I2C(128, 64, i2c)
oled.rotate(1)

# Initialize SPI for SD Card
cs = Pin(13, Pin.OUT)
spi = SPI(1, baudrate=1_000_000, polarity=0, phase=0, bits=8,
          firstbit=SPI.MSB, sck=Pin(14), mosi=Pin(15), miso=Pin(12))

sd = SDCard(spi, cs)
sd.init_spi(25_000_000)
os.mount(sd, "/sd")

SCK_PIN = 16
WS_PIN = 17
SD_PIN = 18
I2S_ID = 0
BUFFER_LENGTH_IN_BYTES = 40000

# Define buttons
Button_1 = Pin(19, Pin.IN, Pin.PULL_UP)
Button_2 = Pin(10, Pin.IN, Pin.PULL_UP)
Button_3 = Pin(11, Pin.IN, Pin.PULL_UP)
Button_4 = Pin(9, Pin.IN, Pin.PULL_UP)  # Used for toggling LED sequence

# Map buttons to songs
button_songs = {
    Button_1: "The Orange And Blue.wav",
    Button_2: "We Are The Boys Of Old Florida.wav",
    Button_3: "Jaws Go Gators.wav"
}

# Initialize WavPlayer
wp = WavPlayer(
    id=I2S_ID,
    sck_pin=Pin(SCK_PIN),
    ws_pin=Pin(WS_PIN),
    sd_pin=Pin(SD_PIN),
    ibuf=BUFFER_LENGTH_IN_BYTES,
)

# Variables for LED cycling
cycling = False
led_index = 0
last_led_update = time.ticks_ms()
last_button_press = 0
debounce_delay = 200  # in milliseconds
led_update_interval = 100  # in milliseconds

# Variables for the "Go Gators!" display effect
go_gators_text = "Go Gators!"
text_x_offset = -75  # Start from left off-screen
text_scroll_speed = 2
text_last_update = time.ticks_ms()
text_update_interval = 50  # in milliseconds
text_paused = False
text_pause_start = 0
text_pause_duration = 5000  # (5 seconds)

def turn_on_leds(index):
    """
    Turn on LEDs in sequence based on the current index.
    """
    outputs = ['0'] * 16  # Initialize all outputs to '0'
    channel = index % 13   # Channels 0-12 for all rows

    # Activate the appropriate PMOS for the row
    if index < 13:
        pmos_row1.value(1)  # Turn on PMOS for row 1
        pmos_row2.value(0)  # Turn off PMOS for row 2
        pmos_row3.value(0)  # Turn off PMOS for row 3
    elif index < 26:
        pmos_row1.value(0)  # Turn off PMOS for row 1
        pmos_row2.value(1)  # Turn on PMOS for row 2
        pmos_row3.value(0)  # Turn off PMOS for row 3
    else:
        pmos_row1.value(0)  # Turn off PMOS for row 1
        pmos_row2.value(0)  # Turn off PMOS for row 2
        pmos_row3.value(1)  # Turn on PMOS for row 3

    # Set the correct channel to '1' to turn on the desired LED
    outputs[channel] = '1'

    # Convert outputs list to string
    outputs_str = ''.join(outputs)
    byte_array = simple_byte_array(outputs_str)
    tlc.set_data(byte_array)

def play_or_stop_song(button, song):
    """
    Play or stop a song based on the pressed button.
    """
    global current_button, current_song

    if current_button == button:
        wp.stop()
        clear_display()
        current_button = None
        current_song = None
    else:
        if current_button is not None:
            wp.stop()
        clear_display()
        display_text_centered([song[:-4].replace("_", " ")])
        wp.play(song, loop=False)
        current_button = button
        current_song = song

def display_text_centered(lines):
    """
    Display given lines of text centered on the OLED display.
    """
    oled.fill(0)
    line_height = 8
    actual_lines = []

    for line in lines:
        # Split lines longer than 16 characters
        if len(line) > 16:
            middle = len(line) // 2
            left = middle
            right = middle + 1

            # Search for spaces near the middle to find a good split point
            while left > 0 and line[left] != ' ':
                left -= 1
            while right < len(line) and line[right] != ' ':
                right += 1

            if (middle - left) <= (right - middle) and left > 0:
                split_point = left
            elif right < len(line):
                split_point = right
            else:
                split_point = middle  # Fallback to middle if no spaces found

            first_half = line[:split_point].strip()
            second_half = line[split_point:].strip()
            actual_lines.append(first_half)
            actual_lines.append(second_half)
        else:
            actual_lines.append(line)

    total_lines = len(actual_lines)
    total_height = total_lines * line_height
    y_start = (oled.height - total_height) // 2

    for i, line in enumerate(actual_lines):
        x = (oled.width - len(line) * 8) // 2
        y = y_start + i * line_height
        oled.text(line, x, y)

    oled.show()

def clear_display():
    """
    Clear the OLED display.
    """
    global current_button, current_song

    oled.fill(0)
    oled.show()
    current_button = None
    current_song = None

def display_go_gators():
    """
    Display "Go Gators!" on the OLED, scrolling horizontally. The text will pause for 5 seconds when it is centered.
    """
    global text_x_offset, text_scroll_speed, text_last_update, text_paused, text_pause_start, text_pause_duration

    # Calculate the center position for the text to pause
    text_width = len(go_gators_text) * 8
    center_position = (128 - text_width) // 2

    current_time = time.ticks_ms()

    # If the text is not paused, move it horizontally
    if not text_paused:
        # Check if it's time to update the text position
        if time.ticks_diff(current_time, text_last_update) > text_update_interval:
            text_last_update = current_time
            # Move the text horizontally
            text_x_offset += text_scroll_speed

            # If the text has reached the center position, start the pause
            if center_position <= text_x_offset < center_position + text_scroll_speed:
                text_x_offset = center_position  # Ensure it exactly matches the center
                text_paused = True
                text_pause_start = current_time
    else:
        # If the text is paused, check if the pause duration has elapsed
        if time.ticks_diff(current_time, text_pause_start) > text_pause_duration:
            text_paused = False
            text_last_update = current_time  # Reset update time to avoid skipping a step
            # Increment text_x_offset to resume scrolling from the center
            text_x_offset += text_scroll_speed

    # If the text has scrolled completely to the right of the screen, reset it to the left
    # This condition ensures continuous scrolling cycle
    if text_x_offset > 128:
        text_x_offset = -text_width
        text_paused = False  # Ensure not paused at start

    # Clear the display and draw the text at the current offset
    oled.fill(0)
    oled.text(go_gators_text, text_x_offset, (oled.height - 8) // 2)  # Center vertically
    oled.show()

# Variables to keep track of the currently pressed button and song
current_button = None
current_song = None

while True:
    current_time = time.ticks_ms()

    # Handle song buttons
    for button, song in button_songs.items():
        if not button.value():  # If button is pressed
            # Debounce check
            if time.ticks_diff(current_time, last_button_press) > debounce_delay:
                play_or_stop_song(button, song)
                last_button_press = current_time

    # Check if the WAV player is still playing
    if current_button is not None and not wp.isplaying():
        clear_display()
        current_button = None
        current_song = None

    # Handle Button_4 for LED cycling
    if not Button_4.value() and time.ticks_diff(current_time, last_button_press) > debounce_delay:
        cycling = not cycling  # Toggle cycling state
        last_button_press = current_time  # Update last button press time

        # Turn off all LEDs if cycling is disabled
        if not cycling:
            pmos_row1.value(0)
            pmos_row2.value(0)
            pmos_row3.value(0)
            outputs = ['0'] * 16
            tlc.set_data(simple_byte_array(''.join(outputs)))

            # Only clear display if no music is playing
            if current_song is None:
                clear_display()
        else:
            # If cycling was just turned on and music is playing, display the current song
            if current_song is not None:
                display_text_centered([current_song[:-4].replace("_", " ")])

    # Handle LED cycling
    if cycling:
        if time.ticks_diff(current_time, last_led_update) > led_update_interval:
            turn_on_leds(led_index)  # Turn on the current LED
            led_index = (led_index + 1) % 39  # Move to the next LED
            last_led_update = current_time  # Update last LED update time

        # If no music is playing and LEDs are on, display "Go Gators!"
        if current_song is None:
            display_go_gators()

    time.sleep(0.05)