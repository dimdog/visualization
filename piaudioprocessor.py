import sounddevice as sd
from audioprocessor import AudioProcessor

class PiAudioProcessor(AudioProcessor):

    def start_stream(self):
        self.stream = sd.InputStream(samplerate=self.RATE, blocksize=self.CHUNK, channels=self.CHANNELS, callback=self.callback)
        self.stream.start()

if __name__ == "__main__":

    a = PiAudioProcessor()
    import time
    while True:
        sd.sleep(1)
