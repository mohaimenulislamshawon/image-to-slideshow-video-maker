import cv2
import os
import numpy as np
from moviepy.editor import VideoFileClip, AudioFileClip, CompositeAudioClip
import glob
def generatex():
    image_directory = 'myimg'
    # Input and output settings for image video generation
    
    image_display_duration = 3000  # milliseconds (3 seconds)
    transition_duration = 50  # Frames (0.5 seconds)
    frame_rate = 45
    video_width = 640
    video_height = 480

    # Input paths for audio addition
    directoryback = "mybackground"
    mp3_files_back = glob.glob(os.path.join(directoryback, "*.mp3"))
    background_audio_path = mp3_files_back[0] if mp3_files_back else None
    print(background_audio_path)
    directoryspeech = "myspeech"
    mp3_files_speech = glob.glob(os.path.join(directoryspeech, "*.mp3"))
    speech_audio_path = mp3_files_speech[0] if mp3_files_speech else None
    print(speech_audio_path)
    # output path
    output_path = "static/final_output.mp4"

    # Create an in-memory video writer
    fourcc = cv2.VideoWriter_fourcc(*'mp4v')
    output_video = cv2.VideoWriter("memory.mp4", fourcc, frame_rate, (video_width, video_height))

    # Generate image video
    image_files = sorted([f for f in os.listdir(image_directory) if f.lower().endswith(('.jpg', '.png', '.jpeg'))])

    for i in range(len(image_files) - 1):
        image1 = cv2.imread(os.path.join(image_directory, image_files[i]))
        image2 = cv2.imread(os.path.join(image_directory, image_files[i + 1]))
        
        image1 = cv2.resize(image1, (video_width, video_height))
        image2 = cv2.resize(image2, (video_width, video_height))
        
        for _ in range(int(image_display_duration * frame_rate / 1000)):
            output_video.write(np.uint8(image1))
        
        for frame in range(transition_duration + 1):
            alpha = frame / transition_duration
            blended = cv2.addWeighted(image1, 1 - alpha, image2, alpha, 0)
            output_video.write(np.uint8(blended))

    output_video.release()

    # Add audio to the generated video
    def crop_audio(audio_clip, target_duration):
        return audio_clip.subclip(0, target_duration)

    def repeat_audio(audio_clip, target_duration):
        audio_duration = audio_clip.duration
        loops_needed = int(target_duration / audio_duration)
        looped_audio = CompositeAudioClip([audio_clip] * loops_needed)
        return looped_audio

    # Create a video clip from the in-memory video
    memory_video = cv2.VideoCapture("memory.mp4")
    memory_video.set(cv2.CAP_PROP_FPS, frame_rate)
    memory_video.set(cv2.CAP_PROP_FRAME_WIDTH, video_width)
    memory_video.set(cv2.CAP_PROP_FRAME_HEIGHT, video_height)

    video_clip = VideoFileClip("memory.mp4")

    background_audio_clip = AudioFileClip(background_audio_path)
    speech_audio_clip = AudioFileClip(speech_audio_path)   

    video_duration = video_clip.duration
    background_audio_duration = background_audio_clip.duration
    speech_audio_duration = speech_audio_clip.duration

    if video_duration < speech_audio_duration:
        adjusted_speech_audio = crop_audio(speech_audio_clip, video_duration)
    else:
        adjusted_speech_audio = speech_audio_clip.subclip(0, video_duration)


    if video_duration > background_audio_duration:
        adjusted_background_audio = repeat_audio(background_audio_clip, video_duration)
    else:
        adjusted_background_audio = background_audio_clip.subclip(0, video_duration)


    final_audio = CompositeAudioClip([adjusted_background_audio.volumex(3.0), adjusted_speech_audio.volumex(0.1)])

    final_clip = video_clip.set_audio(final_audio)
    final_clip.write_videofile(output_path, audio_codec='aac')
    os.remove("memory.mp4")
    if background_audio_path:
        print(background_audio_path)
        os.remove(background_audio_path)

    if speech_audio_path:
        print(speech_audio_path)
        os.remove(speech_audio_path)
    # Check if the directory exists
    if os.path.exists(image_directory) and os.path.isdir(image_directory):
        # List all files in the directory
        files_in_directory = os.listdir(image_directory)
        
        # Check if there are any files in the directory
        if files_in_directory:
            # Iterate over the files and remove them
            for file_name in files_in_directory:
                file_path = os.path.join(image_directory, file_name)
                if os.path.isfile(file_path):
                    os.remove(file_path)
            print("All files in the 'myimg' folder have been deleted.")

    #need to delete all images from myimg

    print("Final video with audio created:", output_path)

