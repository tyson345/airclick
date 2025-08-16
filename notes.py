import speech_recognition as sr
import pyttsx3
import webbrowser
import subprocess
import os
import time
import tempfile
from datetime import datetime
import json
import threading
import pyautogui
import keyboard
from gtts import gTTS
from playsound import playsound

class NotesMode:
    def __init__(self):
        self.recognizer = sr.Recognizer()
        self.tts_engine = pyttsx3.init()
        self.tts_engine.setProperty('rate', 150)
        self.tts_engine.setProperty('volume', 1.0)
        self.running = True
        self.current_message = ""
        self.notes_folder = "saved_notes"
        self.temp_dir = tempfile.gettempdir()
        
        # Create notes folder if it doesn't exist
        if not os.path.exists(self.notes_folder):
            os.makedirs(self.notes_folder)
    
    def speak(self, text, use_ai_voice=True):
        """Speak text aloud"""
        print(f"[NOTES ASSISTANT]: {text}")
        
        if not text.strip():
            return
            
        if use_ai_voice:
            try:
                temp_file = os.path.join(self.temp_dir, f"notes_response_{time.time()}.mp3")
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
            self.tts_engine.say(text)
            self.tts_engine.runAndWait()
        except Exception as e:
            print(f"[TTS ERROR] pyttsx3 failed: {e}")
    
    def listen_for_message(self):
        """Listen for user message input"""
        with sr.Microphone() as source:
            self.recognizer.adjust_for_ambient_noise(source, duration=1)
            self.speak("I'm listening for your message...", use_ai_voice=False)
            try:
                # Listen for longer messages
                audio = self.recognizer.listen(source, timeout=10, phrase_time_limit=15)
                message = self.recognizer.recognize_google(audio)
                print(f"[USER MESSAGE]: {message}")
                return message
            except sr.UnknownValueError:
                self.speak("Sorry, I didn't understand that. Please try again.")
                return None
            except sr.RequestError:
                self.speak("Network error occurred")
                return None
            except sr.WaitTimeoutError:
                self.speak("I didn't hear anything")
                return None
    
    def listen_for_command(self):
        """Listen for user commands"""
        with sr.Microphone() as source:
            self.recognizer.adjust_for_ambient_noise(source, duration=1)
            try:
                audio = self.recognizer.listen(source, timeout=5, phrase_time_limit=8)
                command = self.recognizer.recognize_google(audio)
                print(f"[USER COMMAND]: {command}")
                return command.lower()
            except sr.UnknownValueError:
                self.speak("Sorry, I didn't understand that command.")
                return None
            except sr.RequestError:
                self.speak("Network error occurred")
                return None
            except sr.WaitTimeoutError:
                self.speak("I didn't hear anything")
                return None
    
    def save_to_notepad(self, message, filename=None):
        """Save message to notepad and file"""
        try:
            if not filename:
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                filename = f"note_{timestamp}.txt"
            
            filepath = os.path.join(self.notes_folder, filename)
            
            # Save to file
            with open(filepath, 'w', encoding='utf-8') as f:
                f.write(f"Created: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
                f.write(f"Message: {message}\n")
            
            # Open in notepad
            if os.name == 'nt':  # Windows
                subprocess.Popen(['notepad.exe', filepath])
            else:  # Linux/Mac
                subprocess.Popen(['gedit', filepath])  # or 'nano', 'vim'
            
            return f"Note saved as {filename} and opened in notepad"
        except Exception as e:
            return f"Error saving note: {str(e)}"
    
    def send_to_whatsapp(self, message):
        """Send message to WhatsApp Web"""
        try:
            # Open WhatsApp Web
            webbrowser.open("https://web.whatsapp.com")
            self.speak("Opening WhatsApp Web. Please select a contact and I'll type the message.")
            
            # Wait for user to select contact
            time.sleep(5)
            
            # Type the message
            pyautogui.typewrite(message)
            
            return "Message typed in WhatsApp. Press Enter to send."
        except Exception as e:
            return f"Error with WhatsApp: {str(e)}"
    
    def send_to_twitter(self, message):
        """Send message to Twitter"""
        try:
            # Open Twitter
            webbrowser.open("https://twitter.com/compose/tweet")
            self.speak("Opening Twitter. I'll type your message.")
            
            # Wait for page to load
            time.sleep(3)
            
            # Type the message
            pyautogui.typewrite(message)
            
            return "Message typed in Twitter. Review and click Tweet to send."
        except Exception as e:
            return f"Error with Twitter: {str(e)}"
    
    def send_to_facebook(self, message):
        """Send message to Facebook"""
        try:
            # Open Facebook
            webbrowser.open("https://www.facebook.com")
            self.speak("Opening Facebook. I'll help you post your message.")
            
            # Wait for page to load
            time.sleep(3)
            
            # Type the message (user will need to click in the post box first)
            pyautogui.typewrite(message)
            
            return "Message typed in Facebook. Click in the post box first if needed."
        except Exception as e:
            return f"Error with Facebook: {str(e)}"
    
    def send_to_instagram(self, message):
        """Send message to Instagram"""
        try:
            # Open Instagram
            webbrowser.open("https://www.instagram.com")
            self.speak("Opening Instagram. You can use this message for a post or story.")
            
            return f"Instagram opened. Your message: {message}"
        except Exception as e:
            return f"Error with Instagram: {str(e)}"
    
    def send_to_linkedin(self, message):
        """Send message to LinkedIn"""
        try:
            # Open LinkedIn
            webbrowser.open("https://www.linkedin.com")
            self.speak("Opening LinkedIn. I'll help you create a post.")
            
            # Wait for page to load
            time.sleep(3)
            
            # Type the message
            pyautogui.typewrite(message)
            
            return "Message typed in LinkedIn. Click in the post area first if needed."
        except Exception as e:
            return f"Error with LinkedIn: {str(e)}"
    
    def process_message_action(self, message, action):
        """Process the action for the message"""
        if "save" in action or "note" in action:
            result = self.save_to_notepad(message)
            self.speak(result)
        elif "whatsapp" in action:
            result = self.send_to_whatsapp(message)
            self.speak(result)
        elif "twitter" in action:
            result = self.send_to_twitter(message)
            self.speak(result)
        elif "facebook" in action:
            result = self.send_to_facebook(message)
            self.speak(result)
        elif "instagram" in action:
            result = self.send_to_instagram(message)
            self.speak(result)
        elif "linkedin" in action:
            result = self.send_to_linkedin(message)
            self.speak(result)
        else:
            self.speak("I didn't understand the action. Please say 'save', 'whatsapp', 'twitter', 'facebook', 'instagram', or 'linkedin'.")
    
    def run(self):
        """Main notes mode loop"""
        self.speak("Notes Mode activated! I can help you save notes or send messages to social apps.")
        
        while self.running:
            self.speak("Press N to start a new message, or say 'exit' to quit notes mode.")
            
            # Wait for 'N' key press
            keyboard.wait('n')
            
            # Get the message
            message = self.listen_for_message()
            if not message:
                continue
            
            self.current_message = message
            self.speak(f"I heard: {message}")
            
            # Ask what to do with the message
            self.speak("What would you like to do? Say 'save' to save as note, or name a social app like 'whatsapp', 'twitter', 'facebook', 'instagram', or 'linkedin'.")
            
            # Listen for action
            action = self.listen_for_command()
            if not action:
                continue
            
            if "exit" in action or "quit" in action:
                break
            
            # Process the action
            self.process_message_action(message, action)
            
            time.sleep(1)
        
        self.speak("Notes mode shutting down.")
    
    def stop(self):
        """Stop the notes mode"""
        self.running = False

if __name__ == "__main__":
    notes_mode = NotesMode()
    try:
        notes_mode.run()
    except KeyboardInterrupt:
        notes_mode.speak("Notes mode shutting down")
