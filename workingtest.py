from PIL import Image
from subprocess import Popen, PIPE

fps, duration = 24, 10
p = Popen(['ffmpeg', '-y', '-f', 'image2pipe', '-vcodec', 'mjpeg', '-r', '24', '-i', '-', '-vcodec', 'libx264', '-qscale', '5', '-r', '24', 'static/video.mp4'], stdin=PIPE)
#p = Popen(['ffmpeg', '-y', '-f', 'image2pipe', '-vcodec', 'mjpeg', '-r', '24', '-i', '-', '-vcodec', 'libx265', 'static/out.mp4'], stdin=PIPE)
#p = Popen(['ffmpeg', '-y', '-f', 'image2pipe', '-vcodec', 'mjpeg', '-r', '24', '-i', '-', '-vcodec', 'libx264', '-qscale', '5', '-r', '24', '-f','mpegts', 'udp://10.0.1.5:1234'], stdin=PIPE)
for i in range(fps * duration):
    im = Image.new("RGB", (300, 300), (i, 1, 1))
    im.save(p.stdin, 'JPEG')
p.stdin.close()
p.wait()
