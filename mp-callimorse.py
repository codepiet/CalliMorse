# Callimorse
# 2025-11-23 P. Gabriel
# echtes micropython
# A: morsen
# B: Einstellungen (cycle Ton/LED)
# Header unten links: Externe Morse-Taste
from calliope_mini import *
import time
import music

# -----------------------------------------------------------
# Konfiguration: Zeitgrenzen in Millisekunden
# -----------------------------------------------------------
THRESHOLD_LONG   = 200     # länger als 200 ms = Strich
THRESHOLD_LETTER = 600     # Pause > 600 ms = Buchstabe fertig
THRESHOLD_WORD   = 1300    # Pause > 1300 ms = Wortende

# -----------------------------------------------------------
# Fester Morse-Baum
# -----------------------------------------------------------
morse_tree = [
    ("",   1,   2),    # 0
    ("E",  3,   4),    # 1
    ("T",  5,   6),    # 2
    ("I",  7,   8),    # 3
    ("A",  9,  10),    # 4
    ("N", 11,  12),    # 5
    ("M", 13,  14),    # 6
    ("S", 15,  16),    # 7
    ("U", 17,  18),    # 8
    ("R", 19,  20),    # 9
    ("W", 21,  22),    # 10
    ("D", 23,  24),    # 11
    ("K", 25,  26),    # 12
    ("G", 27,  28),    # 13
    ("O", 29,  30),    # 14
    ("H", -1,  -1),    # 15
    ("V", -1,  -1),    # 16
    ("F", -1,  -1),    # 17
    ("",  -1,  -1),    # 18 (unused)
    ("L", -1,  -1),    # 19
    ("",  -1,  -1),    # 20 (unused)
    ("P", -1,  -1),    # 21
    ("J", -1,  -1),    # 22
    ("B", -1,  -1),    # 23
    ("X", -1,  -1),    # 24
    ("C", -1,  -1),    # 25
    ("Y", -1,  -1),    # 26
    ("Z", -1,  -1),    # 27
    ("Q", -1,  -1),    # 28
    ("",  -1,  -1),    # 29 (unused)
    ("",  -1,  -1),    # 30 (unused)
]

pin0.set_pull(pin0.PULL_UP)

# -----------------------------------------------------------
# Morse-Code → Buchstabe
# -----------------------------------------------------------
def morse_to_char(code):
    index = 0
    for s in code:
        if s == ".":
            index = morse_tree[index][1]
        else:
            index = morse_tree[index][2]
        if index < 0:
            return ""   # Sicherheitsfallback
    return morse_tree[index][0]

# LED on
def ledan():
    led.set_green(0)
    led.set_red(0)
    led.set_blue(10)

# -----------------------------------------------------------
# Variable
# -----------------------------------------------------------
letter = ""
pressed = False
press_time = 0
release_time = 0
space_printed = False
setting_sound = True
setting_led = True


# -----------------------------------------------------------
# Hauptprogramm
# -----------------------------------------------------------
display.clear()
display.scroll("CalliMorse", 70)

while True:
    # Taste gedrückt? (intern oder Pin0)
    if button_b.is_pressed():
        if setting_sound and setting_led:
            setting_sound = False
            ledan()
            time.sleep_ms(30)
            led.clear()
        elif not setting_sound and setting_led:
            setting_led = False
        elif not setting_sound and not setting_led:
            setting_sound = True
            music.pitch(440)
            time.sleep_ms(30)
            music.stop()
        else:
            setting_sound = True
            setting_led = True
            music.pitch(440)
            ledan()
            time.sleep_ms(30)
            music.stop()
            led.clear()
        text = "Ton {} - LED {}"
        display.scroll(text.format("an" if setting_sound else "aus", "an" if setting_led else "aus"), 70)
        time.sleep_ms(500)        
    if button_a.is_pressed() or pin0.read_digital() == 0:
        if not pressed:
            pressed = True
            if setting_led:
                ledan()
            if setting_sound:
                music.pitch(440)
            press_time = time.ticks_ms()
    else:
        if pressed:
            # Taste losgelassen
            if setting_sound:
                music.stop()
            if setting_led:
                led.clear()
            duration = time.ticks_ms() - press_time
            pressed = False

            if duration < THRESHOLD_LONG:
                letter += "."
                print(".")
            else:
                letter += "-"
                print("-")

            release_time = time.ticks_ms()
            space_printed = False
        else:
            # Taste weiterhin nicht gedrückt
            duration = time.ticks_ms() - release_time

            if release_time > 0 and not space_printed and duration > THRESHOLD_LETTER:
                ch = morse_to_char(letter)
                display.show(ch)
                print(ch)
                letter = ""
                space_printed = True

            if release_time > 0 and duration > THRESHOLD_WORD:
                display.clear()
                release_time = 0

    time.sleep_ms(30)