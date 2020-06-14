import pyaudio
import configparser
import aubio
import colour
import numpy as np
import redis

config = configparser.ConfigParser()
config.read('config.ini')
#redishost = "10.0.1.18"
redishost = config['DEFAULT']['REDIS_URL']

class AudioProcessor(object):
    FORMAT = pyaudio.paFloat32
    CHANNELS = 1
    RATE = 44100
    CHUNK = 1024
    hop_s = CHUNK // 2  # hop size
    active = None

    detect_onset = True
    detect_mfcc = True

    def __init__(self):
        self.redis = redis.StrictRedis(host=redishost, port=6379, password="", decode_responses=True)

        self.a_onset = aubio.onset("default", self.CHUNK, self.hop_s, self.RATE)
        self.a_tempo = aubio.tempo("specflux", self.CHUNK, self.hop_s, self.RATE)
        self.a_notes = aubio.notes("default", self.CHUNK, self.hop_s, self.RATE)
        n_filters = 40 # required
        n_coeffs = 13 # I wonder if i made this 1....
        self.a_pvoc = aubio.pvoc(self.CHUNK, self.hop_s)
        self.a_mfcc = aubio.mfcc(self.CHUNK, n_filters, n_coeffs, self.RATE)

        self.last_average = 0
        self.colors = None
        self.range_counter = 0
        self.all_notes = set()
        self.start_stream()

    def start_stream(self):
        self.p = pyaudio.PyAudio()
        stream = self.p.open(format=self.FORMAT,
                        channels=self.CHANNELS,
                        rate=self.RATE,
                        input=True,
                        output=True,
                        input_device_index = self.get_input_device_index(),
                        output_device_index = self.get_output_device_index(),
                        frames_per_buffer = self.CHUNK,
                        stream_callback=self.callback)
        stream.start_stream()


    def get_input_device_index(self):
        for i in range(self.p.get_device_count()):
            if self.p.get_device_info_by_index(i)['name'] == 'Soundflower (2ch)':
                print("Found!{}".format(self.p.get_device_info_by_index(i)['name']))
                return i

    def get_output_device_index(self):
        for i in range(self.p.get_device_count()):
            if self.p.get_device_info_by_index(i)['name'] == 'Built-in Output':
            #if self.p.get_device_info_by_index(i)['name'] == 'AUSDOM M04S':
                print("Found!{}".format(self.p.get_device_info_by_index(i)['name']))
                return i

    def process_octave(self, ret):
        midi = self.a_notes(ret)[0]
        if 0 < midi <= 127:
            note_octave = aubio.midi2note(int(midi))
            if note_octave != "C-1":
                note = note_octave[:-1]
                self.all_notes.add(note)
                octave = int(note_octave[-1])
                ranged_octave = min(max(octave, 1), 5)
                self.redis.lpush("beat_queue", "noteoctave:{},{}".format(note, ranged_octave))
                self.redis.publish("beats", "noteoctave:{},{}".format(note, ranged_octave))

                if octave < 1 or octave > 5:
                    print("OUTSIDE EXPECTED RANGE\t\t{}".format(note_octave))
                    print("# in expected range prior:{}".format(self.range_counter))
                    print(self.all_notes)
                    self.range_counter = 0
                else:
                    self.range_counter+=1

    def process_onset(self, ret):
        if self.detect_onset:
            onset = self.a_onset(ret)[0]
            if onset > 0:
                self.redis.lpush("beat_queue", "Beat")
                self.redis.publish("beats", "Beat")

    def process_mfcc(self, ret): # power
        if self.detect_mfcc:
            spec = self.a_pvoc(ret)
            mfcc = self.a_mfcc(spec)
            try:
                val = int(sum(mfcc[1:]))  # first coefficient is a constant?
                self.redis.lpush("beat_queue", val)
                self.redis.publish("beats", val)
            except:
                pass


    def callback(self, in_data, frame_count, time_info, status):
        ret = np.fromstring(in_data, dtype=np.float32)
        ret = ret[0:self.hop_s]

        self.process_octave(ret)
        self.process_onset(ret)
        self.process_mfcc(ret)
        #How loud is it?
        #What is its pitch?
        #What is its spectrum?
        #What frequencies are present?
        #How loud are the frequencies?
        #How does the sound change over time?
        #Where is the sound coming from?
        #What’s a good guess as to the characteristics of the physical object that made the sound?

        return (in_data, pyaudio.paContinue)


if __name__ == "__main__":

    a = AudioProcessor()
    import time
    while True:
        time.sleep(0.1)
