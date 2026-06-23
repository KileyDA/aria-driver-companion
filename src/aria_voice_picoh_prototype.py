from ohbot import ohbot
import speech_recognition as sr
import subprocess
import time
import csv
from datetime import datetime
from pathlib import Path


# -----------------------------
# Settings
# -----------------------------

LOG_FILE = Path("data/voice_logs/aria_voice_log.csv")

# Leave this as None first.
# If SpeechRecognition uses the wrong microphone, we will set this later.
MIC_DEVICE_INDEX = None


# -----------------------------
# Utility functions
# -----------------------------

def speak(text):
    """
    Uses Raspberry Pi espeak for voice output.
    This avoids ohbot.say(), which was causing Festival dependency issues.
    """
    print("ARIA:", text)
    subprocess.run(["espeak", text])


def log_event(command, response):
    """
    Saves each interaction to a CSV log file.
    """
    LOG_FILE.parent.mkdir(parents=True, exist_ok=True)

    file_exists = LOG_FILE.exists()

    with open(LOG_FILE, mode="a", newline="") as file:
        writer = csv.writer(file)

        if not file_exists:
            writer.writerow(["timestamp", "command", "response"])

        writer.writerow([
            datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            command,
            response
        ])


# -----------------------------
# Picoh movement functions
# -----------------------------

def reset_picoh():
    ohbot.reset()
    time.sleep(0.3)


def look_attentive():
    """
    Basic attentive posture.
    """
    ohbot.move(1, 5)
    ohbot.move(2, 5)
    time.sleep(0.3)


def nod():
    """
    Simple nod movement.
    """
    ohbot.move(1, 7)
    time.sleep(0.25)
    ohbot.move(1, 3)
    time.sleep(0.25)
    ohbot.move(1, 5)


def shake_head():
    """
    Simple side-to-side movement.
    """
    ohbot.move(2, 3)
    time.sleep(0.25)
    ohbot.move(2, 7)
    time.sleep(0.25)
    ohbot.move(2, 5)


def tired_reaction():
    """
    More serious reaction for tired command.
    """
    look_attentive()
    ohbot.move(1, 4)
    time.sleep(0.4)
    nod()


def bored_reaction():
    """
    Gentle animated reaction for boredom.
    """
    look_attentive()
    ohbot.move(2, 4)
    time.sleep(0.3)
    ohbot.move(2, 6)
    time.sleep(0.3)
    ohbot.move(2, 5)


# -----------------------------
# Command handling
# -----------------------------

def react_to_command(command):
    """
    Takes recognised speech and chooses Picoh reaction.
    Returns False if the program should stop.
    """
    command = command.lower().strip()

    print("Command detected:", command)

    if "hello" in command or "hi" in command:
        response = "Hello Kelly. ARIA is ready."
        look_attentive()
        speak(response)
        nod()

    elif "fine" in command or "okay" in command or "good" in command:
        response = "Good to hear. I will check in again later."
        look_attentive()
        speak(response)
        nod()

    elif "bored" in command:
        response = "Thanks for telling me. Try changing your focus. Take a short break when it is safe."
        bored_reaction()
        speak(response)
        nod()

    elif "tired" in command or "sleepy" in command:
        response = "Thanks for being honest. Please consider stopping for a safe rest break."
        tired_reaction()
        speak(response)
        nod()

    elif "stop" in command or "shutdown" in command or "quit" in command:
        response = "Okay. I will stop listening now."
        speak(response)
        reset_picoh()
        log_event(command, response)
        return False

    else:
        response = "I heard you, but I do not know that command yet."
        shake_head()
        speak(response)

    log_event(command, response)
    return True


# -----------------------------
# Microphone listening
# -----------------------------

def listen_once(recognizer, microphone):
    """
    Listens once and converts speech to text.
    Uses Google speech recognition, so internet is needed.
    """
    with microphone as source:
        print("\nListening... Say: hello, fine, bored, tired, or stop")
        recognizer.adjust_for_ambient_noise(source, duration=0.5)

        try:
            audio = recognizer.listen(source, timeout=6, phrase_time_limit=4)
        except sr.WaitTimeoutError:
            print("No speech detected.")
            return ""

    try:
        command = recognizer.recognize_google(audio)
        print("You said:", command)
        return command

    except sr.UnknownValueError:
        print("Could not understand audio.")
        return ""

    except sr.RequestError as error:
        print("Speech recognition service error:", error)
        return ""


# -----------------------------
# Main program
# -----------------------------

def main():
    recognizer = sr.Recognizer()

    if MIC_DEVICE_INDEX is None:
        microphone = sr.Microphone()
    else:
        microphone = sr.Microphone(device_index=MIC_DEVICE_INDEX)

    reset_picoh()
    look_attentive()

    speak("ARIA voice control is ready.")
    speak("Say hello, fine, bored, tired, or stop.")

    keep_running = True

    while keep_running:
        command = listen_once(recognizer, microphone)

        if command:
            keep_running = react_to_command(command)

        time.sleep(1)

    print("ARIA stopped.")


if __name__ == "__main__":
    main()
