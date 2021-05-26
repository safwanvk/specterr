import os
import numpy as np
from cv2 import VideoWriter, VideoWriter_fourcc
import cv2 as cv
import librosa
import ffmpeg
from models import *
# import threading

screen_width = 1920
screen_height = 1080
FPS = 60
seconds = 10
no_of_bars = 120
left_space = 10
max_freq = 600
division_number = 1.1**65

# t = threading.Thread()
# complete = False

class bar:
    def __init__(self, x, y, color, max_height = 100, min_height = 5, width = 10, height_decibel_ratio = 0.5):
        self.x, self.y = x, y
        self.color = color
        self.max_height, self.min_height = max_height, min_height
        self.width = width
        self.height = 0
        self.height_decibel_ratio = height_decibel_ratio

    # def update(self, decibel, dt):

    #     desired_height = -1*decibel*self.height_decibel_ratio + self.min_height
    #     speed = (desired_height - self.height)/0.05

    #     self.height += speed * dt
    #     self.height = clamp(self.min_height, self.max_height, self.height)


def main(filename):
    # Make sense of audio
    # filename='savedfile_simple1.wav'
    VidName = f'{filename}_TEMP.avi'

    no_of_circles = 4

    ts, sr = librosa.load(UPLOAD_FOLDER + filename)
    stft = np.abs(librosa.stft(ts, hop_length = 512, n_fft = 2048*4))
    spectrogram = librosa.amplitude_to_db(stft, ref=np.max)
    # frequencies = librosa.core.fft_frequencies(n_fft=2048*4)
    # freq_index_ratio = len(frequencies)/frequencies[-1]
    # max_freq = int(frequencies[-1])
    freq_step = int(max_freq/no_of_bars)
    music_duration = librosa.get_duration(ts, sr)
    print("duration", music_duration)
    seconds = int(music_duration)

    #Video things
    fourcc = VideoWriter_fourcc(*'MP42')
    video = VideoWriter(VidName, fourcc, float(FPS), (screen_width, screen_height))

    bar_width = int((screen_width-left_space)/no_of_bars)
    bar_max_height = int(screen_height*8/14)
    bars = []
    for number in range(no_of_bars):
        bars.append(bar(left_space*number, 20, (255,0,0), bar_max_height, 30, bar_width))
    

    for video_frame_no in range(FPS*seconds):
        time_frame = librosa.core.time_to_frames(video_frame_no/FPS, sr = sr)

        video_frame = np.empty((screen_height, screen_width, 3), np.uint8)
        # video_frame.fill(255)
        video_frame[:][:] = [52, 42, 37] # [37, 42, 52]
        




        bar_count = 0
        # for each in bars:

        #     barLeft = each.x + (bar_width)*bar_count + left_space
        #     barBottom = screen_height - each.min_height
        #     barRight = each.x + (bar_width)*(bar_count+1) + left_space
        #     barTop = screen_height - int(each.max_height*video_frame_no/(FPS*seconds))-each.min_height

        #     cv.rectangle(video_frame, (barLeft, barBottom), (barRight, barTop), (255, 0, 0), -1)
        #     bar_count += 1
        bar_heights = []
        # for i in range(10, max_freq, freq_step):
        #     x = np.mean(spectrogram[int(i*freq_index_ratio):int((i+freq_step)*freq_index_ratio), time_frame])  
        #     bar_heights.append(
        #         clamp(bar_max_height, bar_max_height*(1.1**(80+x))/1.1**65)
        #         )   
        len_of_freq = len(spectrogram.T[time_frame])
        no_of_els_to_add = (freq_step - len_of_freq % freq_step)
        x = np.pad(spectrogram.T[time_frame], (0, no_of_els_to_add))
        mean = np.mean(x.reshape(-1, freq_step), axis = 1)
        # bar_heights = np.power(1.1, np.mean(x.reshape(-1, freq_step), axis = 1)+ 80)*bar_max_height/1.1**65
        # bar_heights = (np.mean(x.reshape(-1, freq_step), axis = 1)+ 80)*bar_max_height/80*1.2
        bar_heights = bar_max_height*((np.power(1.1, (mean + 80))-1)/division_number)
        bar_heights[bar_heights > bar_max_height] = bar_max_height
        w = 3
        bar_heights_convolved = np.convolve(bar_heights, np.ones(w), 'valid') / w 
        

        circleradi = ((mean+80)/80*300).astype(int)
        # cv.circle(video_frame, (int(screen_width/2), int(screen_height/3)), 7, (30,174,152)[::-1], -1)
        cv.circle(video_frame, (int(screen_width/2), int(screen_height/3)), 50*int(circleradi[3]/300), (30,174,152)[::-1], -1)
        colors = [(8,217,214), (255,46,99), (234,234,234), (31,171,137)]
        for j in range(no_of_circles):
            cv.circle(video_frame, (int(640*(j)), int(screen_height/3)), circleradi[100*j+no_of_bars], colors[j][::-1], 5)
            

        no_of_available_divisions = len(bar_heights)
        for each in bars:

            barLeft = each.x + (bar_width)*bar_count + left_space
            barBottom = screen_height - each.min_height
            barRight = each.x + (bar_width)*(bar_count+1) + left_space
            if(bar_count < no_of_available_divisions):
                barTop = screen_height - int(bar_heights_convolved[bar_count]) -each.min_height
            else:
                barTop = screen_height -each.min_height

            cv.rectangle(video_frame, (barLeft, barBottom), (barRight, barTop), (bar_count/no_of_bars*244, (no_of_bars- bar_count)/no_of_bars*244, 234), -1)
            bar_count += 1

        video.write(video_frame)
    video.release()

    input_video = ffmpeg.input(VidName)
    input_audio = ffmpeg.input(UPLOAD_FOLDER + filename)
    try:
        ffmpeg.concat(input_video, input_audio, v=1, a=1).output(
            UPLOAD_FOLDER + filename + '.mp4').run()
    except ffmpeg.Error as e:
        print(e.stderr)
    if os.path.exists(VidName):
        os.remove(VidName)

    # global complete
    # complete = True



def clamp(max_value, value):

    if value > max_value:
        return max_value
    else:
        return value

