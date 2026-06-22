from ohbot import ohbot
import time
import subprocess

def speak(text):
    subprocess.run(["espeak",text])

print("Initialising Picoh...")

ohbot.reset()

print("Moving Picoh...")

ohbot.move(1, 8)
time.sleep(0.5)

ohbot.move(2, 10)
time.sleep(0.5)

ohbot.move(2,3)
time.sleep(0.5)

print("Speaking...")

speak("Hello Kelly, ARIA is starting")

time.sleep(1)

ohbot.reset()

print("Done")
