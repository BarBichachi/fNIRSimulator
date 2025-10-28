import time
import pylsl
import config


def main():
    """
    Looks for the fNIRS stream defined in config.py and prints the data it receives.
    """
    print(f"Looking for a stream with type '{config.STREAM_TYPE}'...")

    # 1. Resolve the stream on the network
    # FIX: Call functions from the pylsl module (pylsl.resolve_stream)
    streams = pylsl.resolve_byprop('type', config.STREAM_TYPE)

    if not streams:
        print("No fNIRS stream found. Make sure your simulator is running and streaming.")
        return

    # 2. Create an inlet to receive data from the stream
    inlet = pylsl.StreamInlet(streams[0])
    stream_name = streams[0].name()
    print(f"\nSuccessfully connected to stream: '{stream_name}'")
    print("Press Ctrl+C to stop.")

    print("\nReceiving data...")
    try:
        while True:
            # 3. Get a new sample from the stream
            sample, timestamp = inlet.pull_sample()

            # 4. Print the received data to the console
            if sample:  # Check if a sample was actually received
                print(
                    f"Timestamp: {timestamp:.3f} | Data: [{sample[0]:.0f}, {sample[1]:.0f}, {sample[2]:.0f}, {sample[3]:.0f}, ...]")

            time.sleep(0.1)

    except KeyboardInterrupt:
        print("\nListener stopped.")
    except Exception as e:
        print(f"An error occurred: {e}")


if __name__ == '__main__':
    main()