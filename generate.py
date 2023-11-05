import cv2
import os
import numpy as np
from moviepy.editor import VideoFileClip, AudioFileClip, CompositeAudioClip
import glob
def generatex():
    image_directory = 'myimg'
    # Input and output settings for image video generation
    
    image_display_duration = 2700  # milliseconds (2.8 seconds)
    transition_duration = 40  # Frames 
    frame_rate = 30
    video_width = 1920
    video_height = 1080
    ZOOM_FACTOR=0.05

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

    # # Generate image video - ORIGINAL
    # image_files = sorted([f for f in os.listdir(image_directory) if f.lower().endswith(('.jpg', '.png', '.jpeg'))])

    # for i in range(len(image_files) - 1):
    #     image1 = cv2.imread(os.path.join(image_directory, image_files[i]))
    #     image2 = cv2.imread(os.path.join(image_directory, image_files[i + 1]))
        
    #     image1 = cv2.resize(image1, (video_width, video_height))
    #     image2 = cv2.resize(image2, (video_width, video_height))
        
    #     for _ in range(int(image_display_duration * frame_rate / 1000)):
    #         output_video.write(np.uint8(image1))
        
    #     for frame in range(transition_duration + 1):
    #         alpha = frame / transition_duration
    #         blended = cv2.addWeighted(image1, 1 - alpha, image2, alpha, 0)
    #         output_video.write(np.uint8(blended))

    # output_video.release()

    # Generate image video - NEW
    image_files = sorted([f for f in os.listdir(image_directory) if f.lower().endswith(('.jpg', '.png', '.jpeg'))])

    for i in range(len(image_files) - 1):
        image1_path = os.path.join(image_directory, image_files[i])
        image1 = cv2.imread(image1_path)
        image1 = prepare_image_for_video(image1, video_width, video_height)

        # Apply zoom and pan effect to the current image
        zoom_frames = zoom_and_pan_effect(image1, video_width, video_height,ZOOM_FACTOR, 'right', int(image_display_duration * frame_rate / 1000))
        for zoom_frame in zoom_frames:
            output_video.write(zoom_frame)

        # Prepare the next image
        image2_path = os.path.join(image_directory, image_files[i + 1])
        image2 = cv2.imread(image2_path)
        image2 = prepare_image_for_video(image2, video_width, video_height)

        # Transition effect to the next image
        last_zoom_frame = zoom_frames[-1]  # Take the last frame from the zoom effect
        print(f"This Image: {image1_path}")  # Debugging: Check the size of the last zoom frame
        print(f"Last zoom frame size: {last_zoom_frame.shape}")  # Debugging: Check the size of the last zoom frame
        print(f"Next image size: {image2.shape}")  # Debugging: Check the size of the next image

        for frame in range(transition_duration + 1):
            alpha = frame / transition_duration
            try:
                blended = cv2.addWeighted(last_zoom_frame, 1 - alpha, cv2.resize(image2, (last_zoom_frame.shape[1], last_zoom_frame.shape[0])), alpha, 0)
                output_video.write(blended)
            except cv2.error as e:
                print(f"Error blending frames: {e}")
                break  # Break out of the loop on error

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

    print(f"Video duration: {video_duration}")
    print(f"Background audio duration: {background_audio_duration}")
    print(f"Speech audio duration: {speech_audio_duration}")

    if video_duration < speech_audio_duration:
        adjusted_speech_audio = crop_audio(speech_audio_clip, video_duration)
    else:
        adjusted_speech_audio = speech_audio_clip.subclip(0, video_duration)


    if video_duration > background_audio_duration:
        print("Need to loop the Audio")
        adjusted_background_audio = repeat_audio(background_audio_clip, video_duration)
    else:
        adjusted_background_audio = background_audio_clip.subclip(0, video_duration)

    print(f"Background audio New duration: {adjusted_background_audio.duration}")
    print(f"Speech audio New duration: {adjusted_speech_audio.duration}")

    final_audio = adjusted_background_audio
    #final_audio = CompositeAudioClip([adjusted_background_audio.volumex(3.0), adjusted_speech_audio.volumex(0.1)])

    final_clip = video_clip.set_audio(final_audio)
    final_clip.write_videofile(output_path, audio_codec='aac')
    os.remove("memory.mp4")


    # Delete files
    
    # if background_audio_path:
    #     print(background_audio_path)
    #     os.remove(background_audio_path)

    # if speech_audio_path:
    #     print(speech_audio_path)
    #     os.remove(speech_audio_path)
    # # Check if the directory exists
    # if os.path.exists(image_directory) and os.path.isdir(image_directory):
    #     # List all files in the directory
    #     files_in_directory = os.listdir(image_directory)
        
    #     # Check if there are any files in the directory
    #     if files_in_directory:
    #         # Iterate over the files and remove them
    #         for file_name in files_in_directory:
    #             file_path = os.path.join(image_directory, file_name)
    #             if os.path.isfile(file_path):
    #                 os.remove(file_path)
    #         print("All files in the 'myimg' folder have been deleted.")

    #need to delete all images from myimg

    print("Final video with audio created:", output_path)

def prepare_image(image, target_width, target_height):
    # Calculate the target aspect ratio
    target_aspect = target_width / target_height
    
    # Get the current aspect ratio of the image
    h, w = image.shape[:2]
    current_aspect = w / h

    # If the current aspect ratio is less than the target, pad the width; else, pad the height
    if current_aspect < target_aspect:
        # Calculate padding size
        new_width = int(target_aspect * h)
        padding = (new_width - w) // 2
        image = cv2.copyMakeBorder(image, 0, 0, padding, padding, cv2.BORDER_CONSTANT, value=[0, 0, 0])
    elif current_aspect > target_aspect:
        # Calculate padding size
        new_height = int(w / target_aspect)
        padding = (new_height - h) // 2
        image = cv2.copyMakeBorder(image, padding, padding, 0, 0, cv2.BORDER_REFLECT, value=[0, 0, 0])

    return image

def zoom_and_pan_effect(image, target_width, target_height, zoom_factor, pan_direction, num_frames):
    # Ensure the image has the correct aspect ratio
    image = prepare_image(image, target_width, target_height)

    # Calculate the dimensions of the zoomed-in area
    zoomed_width = int(target_width * (1 - zoom_factor))
    zoomed_height = int(target_height * (1 - zoom_factor))

    # Calculate the step size for panning
    step_x = (image.shape[1] - zoomed_width) / num_frames if pan_direction == 'right' else 0

    frames = []
    for i in range(num_frames):
        # Calculate the sub-window (x, y, w, h)
        x = int(step_x * i)
        y = int((target_height - zoomed_height) / 2)  # Calculate the vertical center
        w = zoomed_width
        h = zoomed_height

        # Crop and resize the image
        sub_image = image[y:y+h, x:x+w]
        frame = cv2.resize(sub_image, (target_width, target_height))
        frames.append(frame)

    return frames

def scale_image_to_bounds(image, target_width, target_height):
    # Calculate the scale for the width and height independently
    scale_width = target_width / image.shape[1]
    scale_height = target_height / image.shape[0]

    # Choose the smaller scale to ensure the image fits within the video bounds
    scale = min(scale_width, scale_height)

    # Perform the scaling
    new_size = (int(image.shape[1] * scale), int(image.shape[0] * scale))
    scaled_image = cv2.resize(image, new_size, interpolation=cv2.INTER_AREA)

    return scaled_image

def prepare_image_for_video(image, video_width, video_height):
    # First, scale the image to be within the bounds set by video_width and video_height
    image = scale_image_to_bounds(image, video_width, video_height)

    # Then, pad the image to the exact video dimensions with a 16:9 aspect ratio
    image = prepare_image(image, video_width, video_height)

    return image


# Add audio to the generated video
def crop_audio(audio_clip, target_duration):
    return audio_clip.subclip(0, target_duration)

def repeat_audio(audio_clip, target_duration):
    audio_duration = audio_clip.duration
    loops_needed = int(target_duration / audio_duration)
    looped_audio = CompositeAudioClip([audio_clip] * loops_needed)
    return looped_audio
