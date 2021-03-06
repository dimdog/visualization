import pyaudio
import aubio
import colour
import numpy as np
import redis

redishost = "10.0.1.18"
#redishost = "localhost"

class AudioProcessor(object):
    FORMAT = pyaudio.paFloat32
    CHANNELS = 1
    RATE = 44100
    CHUNK = 1024
    hop_s = CHUNK // 2  # hop size
    active = None
    
    detect_pitch = False
    detect_onset = True
    detect_beat = False
    detect_mfcc = True

    def __init__(self):
        self.redis = redis.StrictRedis(host=redishost, port=6379, password="", decode_responses=True)
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

        self.a_onset = aubio.onset("default", self.CHUNK, self.hop_s, self.RATE)
        self.a_tempo = aubio.tempo("specflux", self.CHUNK, self.hop_s, self.RATE)
        self.a_pitch = aubio.pitch("default", self.CHUNK, self.hop_s, self.RATE)
        self.a_notes = aubio.notes("default", self.CHUNK, self.hop_s, self.RATE)
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
        self.range_counter = 0
        self.all_notes = set()
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

    def process_beat(self, ret):
        if self.detect_beat:
            is_beat = self.a_tempo(ret)
            if is_beat:
                # TODO send message to add a ray with color (we can always bump this up later)
                #self.source_body.add_ray(color=self.colors[pitch_index])
                self.redis.lpush("beat_queue", "Beat")
                self.redis.publish("beats", "Beat")
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

    def callback(self, in_data, frame_count, time_info, status):
        # pitch is typically in the 0 - 20k range
        ret = np.fromstring(in_data, dtype=np.float32)
        ret = ret[0:self.hop_s]

        self.process_octave(ret)
        self.process_onset(ret)
        self.process_mfcc(ret)
        self.process_beat(ret)

        return (in_data, pyaudio.paContinue)


if __name__ == "__main__":

    a = AudioProcessor()
    import time
    while True:
        time.sleep(0.1)
