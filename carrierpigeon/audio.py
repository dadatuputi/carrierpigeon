import logging
import threading
import alsaaudio
import wave
import tempfile
import time
import array

logger = logging.getLogger(__name__)


class RecordThread(threading.Thread):

    chunk_size = 1024
    audio_format = alsaaudio.PCM_FORMAT_S16_LE
    channels = 1
    rate = 44100
    recorder = None
    p = None
    stream = None

    def __init__(self):
        super().__init__()
        self.stop = threading.Event()
        self.recorder = alsaaudio.PCM(type=alsaaudio.PCM_CAPTURE)
        self.recorder.setchannels(self.channels)
        self.recorder.setrate(self.rate)
        self.recorder.setformat(self.audio_format)
        self.recorder.setperiodsize(self.chunk_size)

#        self.p = pyaudio.PyAudio()
#        self.stream = self.p.open(format=self.audio_format, 
#                                channels=self.channels, 
#                                rate=self.frequency, 
#                                input=True, 
#                                frames_per_buffer=self.chunk_size,
#                                input_device_index=0)
    
    def run(self):
        
        logger.debug("Recording started")

        frames = array.array('h')
        while not self.stop.is_set():
            frames.frombytes(self.recorder.read()[1])

        logger.debug("Recording stopped")

        with tempfile.NamedTemporaryFile(mode="wb", suffix=".wav", prefix="cpm-", delete=False) as output: 
            wf = wave.open(output)
            wf.setnchannels(self.channels)
            wf.setsampwidth(self.audio_format)
            wf.setframerate(self.rate)
            wf.writeframes(frames)
            wf.close()
            
            logger.info("Recorded {} seconds to file: {}".format(len(frames)/self.rate, output))

