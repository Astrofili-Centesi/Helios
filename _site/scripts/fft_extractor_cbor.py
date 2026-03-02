import argparse
import logging
import numpy as np
import scipy.io.wavfile as wav
import scipy.signal as signal
import cbor2
import os

def extract_full_fft(filename, timestamp, fft_length, window_type=None):
    # Read wav file
    sample_rate, data = wav.read(filename)
    if data.ndim > 1:
        data = data[:, 0]  # Take first channel if stereo

    # Ensure fft_length does not exceed data length
    if fft_length > len(data):
        logging.error("Requested FFT length exceeds the file's data length.")
        sys.exit(1)

    # Create the window function if specified
    try:
        window = signal.get_window(window_type, fft_length) if window_type else np.ones(fft_length)
    except ValueError:
        logging.error(f"Invalid window type: {window_type}")
        sys.exit(1)

    # Calculate STFT over the entire file using the specified window and fft_length
    f, t, Zxx = signal.stft(data, fs=sample_rate, window=window, nperseg=fft_length, noverlap=fft_length // 2)
    
    # Average magnitudes over all time slices to get a single FFT-like result for the entire file
    avg_fft_magnitudes = np.mean(np.abs(Zxx), axis=1)

    # Convert to dB scale
    avg_fft_db = 20 * np.log10(avg_fft_magnitudes + 1e-10)  # Adding a small value to avoid log(0)

    # Scale dB values to uint16 range
    scale_factor = 655.35  # To map 0-100 dB range into 0-65535
    scaled_values = [float(round(dB,2)) for dB in avg_fft_db]

    # Calculate frequency values for each bin
    frequencies = [i * sample_rate / fft_length for i in range(len(avg_fft_db))]

    return timestamp, frequencies, scaled_values

def main():
    parser = argparse.ArgumentParser(description="Extract an averaged FFT from a wav file using windowing.")
    parser.add_argument("filename", type=str, help="Path to the .wav file")
    parser.add_argument("timestamp", type=str, help="Timestamp for the FFT segment (copied as-is to output)")
    parser.add_argument("fft_length", type=int, help="Length (in samples) of each FFT segment")
    parser.add_argument("--window", type=str, default=None, help="Window type for FFT (e.g., hamming, hann)")
    parser.add_argument("--output", type=str, default="output.cbor", help="Output CBOR file")
    parser.add_argument("--log", type=str, default="INFO", help="Logging level (DEBUG, INFO, WARNING, ERROR, CRITICAL)")

    args = parser.parse_args()

    # Configure logging
    logging.basicConfig(level=getattr(logging, args.log.upper(), None))

    logging.info(f"Processing file: {args.filename}")
    logging.info(f"Timestamp: {args.timestamp}")
    logging.info(f"FFT Length: {args.fft_length} samples")
    if args.window:
        logging.info(f"Using window: {args.window}")

    # Get averaged FFT data and frequency labels for each bin
    timestamp_str, frequencies, scaled_values = extract_full_fft(args.filename, args.timestamp, args.fft_length, args.window)

    # Prepare data to be saved in CBOR format
    data = {
        "timestamp": timestamp_str,
        "frequencies": frequencies,
        "fft_values": scaled_values
    }

    # Write to CBOR file
    with open(args.output, "wb") as file:
        cbor2.dump(data, file)
    
    logging.info(f"FFT data saved to {args.output}")

if __name__ == "__main__":
    main()
