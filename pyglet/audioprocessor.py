import pyaudio
import aubio
import colour
import numpy as np
import redis


class AudioProcessor(object):
    FORMAT = pyaudio.paFloat32
    CHANNELS = 1
    RATE = 44100
    CHUNK = 1024
    hop_s = CHUNK // 2  # hop size
    active = None

    def __init__(self):
        self.redis = redis.StrictRedis(host="localhost", port=6379, password="", decode_responses=True)
        self.p = pyaudio.PyAudio()
        stream = self.p.open(format=self.FORMAT,
                        channels=self.CHANNELS,
                        rate=self.RATE,
                        input=True,
                        output=False,
                        input_device_index = self.get_input_device_index(),
                        output_device_index = self.get_output_device_index(),
                        frames_per_buffer = self.CHUNK,
                        stream_callback=self.callback)

        self.a_tempo = aubio.tempo("specflux", self.CHUNK, self.hop_s, self.RATE)
        self.a_pitch = aubio.pitch("default", self.CHUNK, self.hop_s, self.RATE)
        n_filters = 40 # required
        n_coeffs = 13 # I wonder if i made this 1....
        self.a_pvoc = aubio.pvoc(self.CHUNK, self.hop_s)
        self.a_mfcc = aubio.mfcc(self.CHUNK, n_filters, n_coeffs, self.RATE)

        self.tolerance = 0.8
        self.a_pitch.set_tolerance(self.tolerance)
        self.highest_pitch = 0
        self.lowest_pitch = 99999999
        self.average_pitch = 0
        self.average_pitch_samples = 0
        self.last_average = 0
        self.colors = None
        self.pitch_range = None
        stream.start_stream()

    def reset(self):
        self.highest_pitch = 0
        self.lowest_pitch = 99999999
        self.average_pitch = 0
        self.average_pitch_samples = 0

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

    def reschedule(self, *args):
        # this means we are on a beat!
        bpm = self.a_tempo.get_bpm()
        # schedule wants 1 = 1 time per second, 0.5 = 2 times per second
        # to get from bpm to scheduling an event for every beat...
        # calculate beats per second
        bps = bpm / 60


        # now retune the colors
        self.pitch_range = self.highest_pitch - self.lowest_pitch
        if self.pitch_range < 3:
            self.pitch_range = 360
        #print("High:{}, low:{}".format( self.highest_pitch, self.lowest_pitch))
        r_b = [color for color in colour.Color("Red").range_to(colour.Color("Green"), int(self.pitch_range/3))]
        b_g = [color for color in colour.Color("Green").range_to(colour.Color("Blue"), int(self.pitch_range/3))]
        g_r = [color for color in colour.Color("Blue").range_to(colour.Color("Red"), int(self.pitch_range/3))]
        self.colors =  r_b+b_g+g_r

    def add_rays(self, *args):
        # deprecated, but maybe some useful logic in here
        for i in range(1):
            pitch_index = int(self.average_pitch - self.lowest_pitch)
            if pitch_index > len(self.colors):
                pitch_index = len(self.colors) - 1
                #print("crap")
            if pitch_index < 0:
                pitch_index = 0

    def callback(self, in_data, frame_count, time_info, status):
        # dir of a_tempo: ['__call__', '__class__', '__delattr__', '__dir__', '__doc__', '__eq__', '__format__', '__ge__', '__getattribute__', '__gt__', '__hash__', '__init__', '__init_subclass__', '__le__', '__lt__', '__ne__', '__new__', '__reduce__', '__reduce_ex__', '__repr__', '__setattr__', '__sizeof__', '__str__', '__subclasshook__', 'buf_size', 'get_bpm', 'get_confidence', 'get_delay', 'get_delay_ms', 'get_delay_s', 'get_last', 'get_last_ms', 'get_last_s', 'get_last_tatum', 'get_period', 'get_period_s', 'get_silence', 'get_threshold', 'hop_size', 'method', 'samplerate', 'set_delay', 'set_delay_ms', 'set_delay_s', 'set_silence', 'set_tatum_signature', 'set_threshold']
        # pitch is typically in the 0 - 20k range
        ret = np.fromstring(in_data, dtype=np.float32)
        ret = ret[0:self.hop_s]
        pitch = self.a_pitch(ret)[0]
        if pitch > 0 and self.a_pitch.get_confidence() > 0:
            self.average_pitch+=pitch
            self.average_pitch_samples+=1
        is_beat = self.a_tempo(ret)
        spec = self.a_pvoc(ret)
        mfcc = self.a_mfcc(spec)
        print(sum(mfcc[1:])) # first coefficient is a constant?
        if is_beat:
            # TODO send message to add a ray with color (we can always bump this up later)
            #self.source_body.add_ray(color=self.colors[pitch_index])
            self.redis.lpush("beat_queue", "Beat")
            if self.average_pitch_samples > 0:
                average_pitch = self.average_pitch / self.average_pitch_samples
                self.last_average = average_pitch
                self.highest_pitch = max([self.highest_pitch, average_pitch])
                self.lowest_pitch = min([self.lowest_pitch, average_pitch])
                #print("average Pitch:{} highest Pitch:{} lowest Pitch:{}".format(average_pitch, self.highest_pitch, self.lowest_pitch))
                self.average_pitch_samples = 0
                self.average_pitch = 0
            else:
                pass
                #print("last Pitch:{} highest Pitch:{} lowest Pitch:{}".format(self.last_average, self.highest_pitch, self.lowest_pitch))
        return (in_data, pyaudio.paContinue)


if __name__ == "__main__":

    a = AudioProcessor()
    import time
    while True:
        time.sleep(0.1)
