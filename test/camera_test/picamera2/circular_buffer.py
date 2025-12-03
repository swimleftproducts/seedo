import time

from picamera2 import Picamera2
from picamera2.encoders import H264Encoder
from picamera2.outputs import CircularOutput2, PyavOutput

picam2 = Picamera2()

config = picam2.create_video_configuration( 
  main = {'size': (1280, 720), 'format': 'YUV420'}, 
  controls={"FrameDurationLimits": (16666, 16666)}
)
picam2.configure(config)
encoder = H264Encoder(bitrate=10000000)
circular = CircularOutput2(buffer_duration_ms=5000)
picam2.start_recording(encoder, circular)

circular.open_output(PyavOutput("start.mp4"))
time.sleep(5)
circular.close_output()
circular.open_output(PyavOutput("end.mp4"))
picam2.stop_recording()