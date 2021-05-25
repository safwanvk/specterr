import os
import numpy as np
from cv2 import VideoWriter, VideoWriter_fourcc
import cv2 as cv
import librosa
import ffmpeg
from models import *
import threading

screen_width = 1920
screen_height = 1080
FPS = 60
seconds = 10
no_of_bars = 100
left_space = 10

t = threading.Thread()
complete = False

class bar:
    def __init__(self, x, y, color, max_height=100, min_height=5, width=10, height_decibel_ratio=0.5):
        self.x, self.y = x, y
        self.color = color
        self.max_height, self.min_height = max_height, min_height
        self.width = width
        self.height = 0
        self.height_decibel_ratio = height_decibel_ratio

    def update(self, decibel, dt):

        desired_height = -1*decibel*self.height_decibel_ratio + self.min_height
        speed = (desired_height - self.height)/0.05

        self.height += speed * dt
        self.height = clamp(self.min_height, self.max_height, self.height)


def main(filename):
    # Make sense of audio
    # filename='savedfile_simple1.wav'
    VidName = f'{filename}_TEMP.avi'

    ts, sr = librosa.load(UPLOAD_FOLDER + filename)
    max_freq = 10000
    stft = np.abs(librosa.stft(ts, hop_length=512, n_fft=2048*4))
    spectrogram = librosa.amplitude_to_db(stft, ref=np.max)
    frequencies = librosa.core.fft_frequencies(n_fft=2048*4)
    freq_index_ratio = len(frequencies)/frequencies[-1]
    max_freq = int(frequencies[-1])
    freq_step = 100
    music_duration = librosa.get_duration(ts, sr)
    print("duration", music_duration)
    seconds = int(music_duration)

    # Video things
    fourcc = VideoWriter_fourcc(*'MP42')
    video = VideoWriter(VidName, fourcc, float(FPS),
                        (screen_width, screen_height))

    bar_width = int(screen_width/no_of_bars)
    bar_max_height = int(screen_height*5/14)
    bars = []
    for number in range(no_of_bars):
        bars.append(bar(left_space*number, 20, (255, 0, 0),
                    bar_max_height, 30, bar_width))

    for video_frame_no in range(FPS*seconds):
        time_frame = librosa.core.time_to_frames(video_frame_no/FPS, sr=sr)

        video_frame = np.empty((screen_height, screen_width, 3), np.uint8)
        video_frame.fill(255)

        bar_count = 0
        # for each in bars:

        #     barLeft = each.x + (bar_width)*bar_count + left_space
        #     barBottom = screen_height - each.min_height
        #     barRight = each.x + (bar_width)*(bar_count+1) + left_space
        #     barTop = screen_height - int(each.max_height*video_frame_no/(FPS*seconds))-each.min_height

        #     cv.rectangle(video_frame, (barLeft, barBottom), (barRight, barTop), (255, 0, 0), -1)
        #     bar_count += 1
        bar_heights = []
        for i in range(0, max_freq, freq_step):
            x = np.mean(spectrogram[int(i*freq_index_ratio):int((i+freq_step)*freq_index_ratio), time_frame])
            bar_heights.append(bar_max_height*(80+x)/80)
        no_of_available_divisions = len(bar_heights)
        for each in bars:

            barLeft = each.x + (bar_width)*bar_count + left_space
            barBottom = screen_height - each.min_height
            barRight = each.x + (bar_width)*(bar_count+1) + left_space
            if(bar_count < no_of_available_divisions):
                barTop = screen_height - \
                    int(bar_heights[bar_count]) - each.min_height
            else:
                barTop = screen_height - each.min_height

            cv.rectangle(video_frame, (barLeft, barBottom),
                         (barRight, barTop), (255, 0, 0), -1)
            bar_count += 1

        video.write(video_frame)
    video.release()

    input_video = ffmpeg.input(VidName)
    input_audio = ffmpeg.input(UPLOAD_FOLDER + filename)
    try:
        ffmpeg.concat(input_video, input_audio, v=1, a=1).output(
            UPLOAD_FOLDER + filename +'.mp4').run()
    except ffmpeg.Error as e:
        print(e.stderr)
    if os.path.exists(VidName):
        os.remove(VidName)
    global complete
    complete = True



def clamp(min_value, max_value, value):

    if value < min_value:
        return min_value

    if value > max_value:
        return max_value

    return value

