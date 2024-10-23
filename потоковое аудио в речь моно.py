import tkinter as tk
from tkinter import ttk
import threading
import pyaudio
import azure.cognitiveservices.speech as speechsdk

class SpeechToTextApp:
    def __init__(self, root):
        self.root = root
        root.title("Speech to Text")

        # Azure Speech Service ключ и регион как атрибуты экземпляра
        self.speech_key = "aafc081ed79c46c38cf4d5a355d320e0"
        self.speech_region = "westeurope"

        self.audio_stream = None
        self.speech_recognizer = None

        # GUI Components
        self.device_var = tk.StringVar()
        self.device_dropdown = ttk.Combobox(root, textvariable=self.device_var, width=50)
        self.device_dropdown['values'] = self.get_device_names()
        self.device_dropdown.grid(column=0, row=0)
        self.device_dropdown.current(0)

        self.start_button = tk.Button(root, text="Start", command=self.start_recognition)
        self.start_button.grid(column=1, row=0)

        self.stop_button = tk.Button(root, text="Stop", command=self.stop_recognition, state='disabled')
        self.stop_button.grid(column=2, row=0)

        self.text_area = tk.Text(root, height=15, width=80)
        self.text_area.grid(column=0, row=1, columnspan=3, sticky="nsew", padx=5, pady=5)

    def get_device_names(self):
        p = pyaudio.PyAudio()
        names = [p.get_device_info_by_index(i)['name'] for i in range(p.get_device_count())]
        p.terminate()
        return names

    def start_recognition(self):
        self.start_button.config(state='disabled')
        self.stop_button.config(state='normal')
        device_index = self.device_dropdown.current()
        threading.Thread(target=self.recognize_speech_from_mic, args=(device_index,)).start()

    def recognize_speech_from_mic(self, device_index):
        p = pyaudio.PyAudio()
        stream = p.open(format=pyaudio.paInt16,
                        channels=1,
                        rate=16000,
                        input=True,
                        input_device_index=device_index,
                        frames_per_buffer=1024)

        audio_stream = speechsdk.audio.PushAudioInputStream()
        audio_config = speechsdk.audio.AudioConfig(stream=audio_stream)
        speech_config = speechsdk.SpeechConfig(subscription=self.speech_key, region=self.speech_region)
        self.speech_recognizer = speechsdk.SpeechRecognizer(speech_config=speech_config, audio_config=audio_config)

        def recognized(args):
            self.text_area.insert(tk.END, args.result.text + "\n")
            self.text_area.see(tk.END)

        self.speech_recognizer.recognized.connect(recognized)

        self.speech_recognizer.start_continuous_recognition()

        try:
            while self.speech_recognizer is not None:
                data = stream.read(1024, exception_on_overflow=False)
                audio_stream.write(data)
        finally:
            stream.stop_stream()
            stream.close()
            p.terminate()

    def stop_recognition(self):
        if self.speech_recognizer:
            self.speech_recognizer.stop_continuous_recognition()
            self.speech_recognizer = None
        self.start_button.config(state='normal')
        self.stop_button.config(state='disabled')

if __name__ == "__main__":
    root = tk.Tk()
    app = SpeechToTextApp(root)
    root.mainloop()
