import speech_recognition as sr
import pyttsx3
import keyboard
import webbrowser
import requests
import time
import os
import tempfile
import subprocess
import platform
import psutil
from gtts import gTTS
from playsound import playsound
import threading

class VoiceAssistant:
    def __init__(self):
        self.backup_engine = pyttsx3.init()
        self.backup_engine.setProperty('rate', 150)
        self.backup_engine.setProperty('volume', 1.0)
        self.recognizer = sr.Recognizer()
        self.temp_dir = tempfile.gettempdir()
        self.running = True
        self._stop_event = threading.Event()

    def speak(self, text, use_ai_voice=True):
        """Speak text aloud"""
        print(f"[ASSISTANT]: {text}")

        if not text.strip():
            return

        if use_ai_voice:
            try:
                temp_file = os.path.join(self.temp_dir, f"assistant_response_{time.time()}.mp3")
                gTTS(text=text, lang='en').save(temp_file)

                if os.path.exists(temp_file) and os.path.getsize(temp_file) > 0:
                    playsound(temp_file)
                    os.remove(temp_file)
                    return
                else:
                    raise Exception("MP3 file not created properly")

            except Exception as e:
                print(f"[TTS ERROR] gTTS failed, switching to pyttsx3: {e}")

        try:
            self.backup_engine.say(text)
            self.backup_engine.runAndWait()
        except Exception as e:
            print(f"[TTS ERROR] pyttsx3 failed: {e}")

    def listen_command(self):
        """Listen for user voice command"""
        with sr.Microphone() as source:
            self.recognizer.adjust_for_ambient_noise(source, duration=1)
            self.speak("I'm listening...", use_ai_voice=False)
            try:
                audio = self.recognizer.listen(source, timeout=5, phrase_time_limit=8)
                command = self.recognizer.recognize_google(audio)
                print(f"[USER]: {command}")
                return command.lower()
            except sr.UnknownValueError:
                self.speak("Sorry, I didn't understand that")
            except sr.RequestError:
                self.speak("Network error occurred")
            except sr.WaitTimeoutError:
                self.speak("I didn't hear anything")
            return ""

    def get_weather(self):
        """Get current weather"""
        try:
            api_key = "84412b09ce71e6cde9b4a6608c07b132"
            city = "Shivamogga"
            url = f"http://api.openweathermap.org/data/2.5/weather?q={city}&appid={api_key}&units=metric"
            data = requests.get(url, timeout=5).json()
            if data.get("cod") != 200:
                return "Could not fetch weather data"
            temp = data["main"]["temp"]
            desc = data["weather"][0]["description"]
            return f"Current weather in {city}: {desc}. Temperature is {temp} degrees Celsius."
        except:
            return "Weather service unavailable"

    def get_news(self, full=False):
        """Get latest tech news using NewsAPI with retry and longer timeout"""
        api_key = "d19ed07ff1c8464ab335b5109ded9caf"
        url = f"https://newsapi.org/v2/top-headlines?category=technology&country=in&apiKey={api_key}"

        for attempt in range(2):
            try:
                articles = requests.get(url, timeout=10).json().get("articles", [])[:5]

                if not articles:
                    return "No news found at the moment."

                if full:
                    news_texts = [f"{art['title']}: {art['description'] or ''}" for art in articles]
                    return "Here is the latest tech news in detail: " + " ... ".join(news_texts)
                else:
                    headlines = [art['title'] for art in articles]
                    return "Latest tech headlines: " + " ... ".join(headlines)

            except Exception as e:
                print(f"[NEWS ERROR Attempt {attempt+1}] {e}")
                if attempt == 0:
                    time.sleep(2)

        return "News service unavailable after multiple attempts"

    def get_system_info(self):
        """Get PC system stats"""
        cpu = psutil.cpu_percent()
        battery = psutil.sensors_battery()
        batt_str = f"Battery at {battery.percent}%" if battery else "No battery detected"
        return f"System info: CPU usage {cpu} percent. {batt_str}."

    def open_app(self, app_name):
        """Open local apps"""
        system_os = platform.system()
        try:
            if system_os == "Windows":
                subprocess.Popen(app_name)
            elif system_os == "Darwin":
                subprocess.Popen(["open", "-a", app_name])
            else:
                subprocess.Popen([app_name])
            return f"Opening {app_name}"
        except:
            return f"Could not open {app_name}"

    def search_google(self, query):
        """Search Google"""
        webbrowser.open(f"https://www.google.com/search?q={query}")
        return f"Searching Google for {query}"

    def set_timer(self, seconds):
        """Set a timer"""
        def countdown():
            time.sleep(seconds)
            self.speak(f"Time's up! Your {seconds} second timer is over.")
        threading.Thread(target=countdown, daemon=True).start()
        return f"Timer set for {seconds} seconds."

    def perform_command(self, command):
        """Process commands and speak result"""
        if not command:
            self.speak("Please say something")
            return

        response = ""

        # Weather
        if "weather" in command:
            response = self.get_weather()

        # News
        elif "full news" in command:
            response = self.get_news(full=True)
        elif "news" in command or "update" in command:
            response = self.get_news(full=False)

        # Timer
        elif "set timer" in command:
            try:
                seconds = int(''.join([c for c in command if c.isdigit()]))
                if seconds > 0:
                    response = self.set_timer(seconds)
                else:
                    response = "Please specify a valid number of seconds."
            except:
                response = "Please tell me the timer duration in seconds."

        # System info
        elif "system info" in command or "status" in command:
            response = self.get_system_info()

        # Search
        elif command.startswith("search"):
            query = command.replace("search", "").strip()
            response = self.search_google(query) if query else "What should I search for?"

        # Websites
        elif "open youtube" in command:
            webbrowser.open("https://www.youtube.com")
            response = "Opening YouTube"
        elif "open google" in command:
            webbrowser.open("https://www.google.com")
            response = "Opening Google"
        elif "open gmail" in command:
            webbrowser.open("https://mail.google.com")
            response = "Opening Gmail"
        elif "open whatsapp" in command:
            webbrowser.open("https://web.whatsapp.com")
            response = "Opening WhatsApp Web"
        elif "open instagram" in command:
            webbrowser.open("https://www.instagram.com")
            response = "Opening Instagram"
        elif "open facebook" in command:
            webbrowser.open("https://www.facebook.com")
            response = "Opening Facebook"
        elif "open twitter" in command:
            webbrowser.open("https://twitter.com")
            response = "Opening Twitter"
        elif "open linkedin" in command:
            webbrowser.open("https://www.linkedin.com")
            response = "Opening LinkedIn"

        # Local apps
        elif "open notepad" in command:
            response = self.open_app("notepad.exe")
        elif "open calculator" in command:
            response = self.open_app("calc.exe")
        elif "open paint" in command:
            response = self.open_app("mspaint.exe")
        elif "open word" in command:
            response = self.open_app("winword.exe")
        elif "open excel" in command:
            response = self.open_app("excel.exe")
        elif "open powerpoint" in command:
            response = self.open_app("powerpnt.exe")

        # Name
        elif "your name" in command:
            response = "I am AirClick Voice Assistant"

        # Exit
        elif any(word in command for word in ["exit", "quit", "stop"]):
            self.speak("Goodbye! Voice mode is shutting down.")
            return "exit"

        else:
            response = "I don't know that command yet"

        self.speak(response)

    def run(self):
        """Main loop for web integration"""
        self.speak("AirClick Voice Assistant ready to help!")
        while self.running and not self._stop_event.is_set():
            self.speak("Press and hold V to speak", use_ai_voice=False)
            
            # Wait for 'v' key press or stop event
            start_time = time.time()
            while not self._stop_event.is_set():
                if keyboard.is_pressed('v'):
                    command = self.listen_command()
                    if command:
                        if self.perform_command(command) == "exit":
                            self.stop()
                            return
                    break
                
                # Check every 100ms and timeout after 30 seconds of inactivity
                time.sleep(0.1)
                if time.time() - start_time > 30:
                    break
            
            if self._stop_event.is_set():
                break
                
            time.sleep(0.5)

    def stop(self):
        """Stop the voice assistant"""
        self.running = False
        self._stop_event.set()
        self.speak("Voice mode shutting down")

if __name__ == "__main__":
    assistant = VoiceAssistant()
    try:
        assistant.run()
    except KeyboardInterrupt:
        assistant.speak("Assistant shutting down")
