# /content/image-to-slideshow-video-maker/generate.py

import cv2
import os
import numpy as np
from moviepy.editor import VideoFileClip, AudioFileClip, CompositeAudioClip
import glob

def generatex():

  image_directory = '/myimg'

  # Input and output settings for image video generation

  image_display_duration = 3000  # milliseconds (3 seconds)
  transition_duration = 50  # Frames (0.5 seconds) 
  frame_rate = 45
  video_width = 640
  video_height = 480

  # Input paths for audio addition
  directoryback = "/mybackground"
  mp3_files_back = glob.glob(os.path.join(directoryback, "*.mp3"))
  background_audio_path = mp3_files_back[0] if mp3_files_back else None
  print(background_audio_path)
  
  directoryspeech = "/myspeech"
  mp3_files_speech = glob.glob(os.path.join(directoryspeech, "*.mp3"))
  speech_audio_path = mp3_files_speech[0] if mp3_files_speech else None
  print(speech_audio_path)
  
  # output path
  output_path = "/final_output.mp4"

  # Rest of function to generate video

  ...

  return output_path
