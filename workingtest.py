from PIL import Image
from subprocess import Popen, PIPE
from random import Random
rand = Random()
fps, duration = 24, 200
#p = Popen(['ffmpeg', '-y', '-f', 'image2pipe', '-vcodec', 'mjpeg', '-r', '24', '-i', '-', '-vcodec', 'libx264', '-qscale', '5', '-r', '24', 'static/video.mp4'], stdin=PIPE)
#p = Popen(['ffmpeg', '-y', '-f', 'image2pipe', '-vcodec', 'mjpeg', '-r', '24', '-i', '-', '-vcodec', 'libx265', 'static/out.mp4'], stdin=PIPE)
#p = Popen(['ffmpeg', '-y', '-f', 'image2pipe', '-vcodec', 'mjpeg', '-r', '24', '-i', '-', '-c:v', 'libx264', '-crf', '21', '-preset', 'veryfast', '-f', 'hls', '-hls_time', '4', '-hls_playlist_type', 'event', 'static/stream.m3u8'], stdin=PIPE)
p = Popen(["ffmpeg", '-y', '-f', 'image2pipe', '-vcodec', 'mjpeg', '-r', '24', '-i', '-', \
       "-c:v", "libx264", \
       "-preset", "superfast", "-profile:v", "baseline", "-level", "3.0", \
       "-tune", "zerolatency", "-s", "1280x720", "-b:v", "1400k", \
       "-bufsize", "1400k", "-use_timeline", "1", "-use_template", "1", \
       "-init_seg_name", "init-stream$RepresentationID$.mp4", \
       "-min_seg_duration", "2000000", "-media_seg_name", "$RepresentationID\$-\$Number\$.mp4", \
       "-f", "dash", "static/stream.mpd"], stdin=PIPE)
for i in range(fps * duration):
    r = rand.randint(0,255)
    g = rand.randint(0,255)
    b = rand.randint(0,255)
    im = Image.new("RGB", (300, 300), (r,g,b))
    im.save(p.stdin, 'JPEG')
p.stdin.close()
p.wait()
