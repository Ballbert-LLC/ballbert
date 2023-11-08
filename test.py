import pvporcupine
import pyaudio

def main():
    try:
        # Initialize Porcupine with the built-in "Porcupine" wake word.
        handle = pvporcupine.create(keywords=["Porcupine"])

        # Initialize PyAudio for audio input.
        pvaudio = pyaudio.PyAudio()

        # Open an audio stream with the specified input device and parameters.
        audio_stream = pvaudio.open(
            rate=handle.sample_rate,
            channels=1,
            format=pyaudio.paInt16,
            input=True,
            frames_per_buffer=handle.frame_length)

        print("Listening for 'Porcupine' wake word...")

        while True:
            pcm = audio_stream.read(handle.frame_length)
            pcm = pcm.from_buffer_copy(pcm)
            result = handle.process(pcm)

            if result:
                print("Wake word 'Porcupine' detected!")

    except KeyboardInterrupt:
        print("Stopping...")
    finally:
        if handle:
            handle.delete()
        if audio_stream:
            audio_stream.close()
        if pvaudio:
            pvaudio.terminate()

if __name__ == '__main__':
    main()
