import pvporcupine
import speech_recognition as sr
import soxr
import numpy as np

def main():
    print(sr.Microphone.list_microphone_names())
    
    
    try:
        # Initialize Porcupine with the built-in "Porcupine" wake word.
        handle = pvporcupine.create(keywords=["computer"],access_key="cLByN9IjCzBQOeBiySgZiJRfogghPS0oA28F8M6gnXldykvSDHPLzg==")

        if not handle:
            print("no pork")
            return
        mic = sr.Microphone(device_index=1)
        recognizer = sr.Recognizer()
        recognizer.energy_threshold = 5000

        with mic as source:
            print("Ready!")
            while True:
                audio_frames = source.stream.read(1410)

                np_audio_data = np.frombuffer(audio_frames, dtype=np.int16)

                np_audio_data = soxr.resample(np_audio_data, 44100, 16000)

                keyword_index = handle.process(np_audio_data)
                if keyword_index >= 0:
                    try:
                        print("keyword")
                    except Exception as e:
                        print(e)


    except KeyboardInterrupt:
        print("Stopping...")


if __name__ == '__main__':
    main()
