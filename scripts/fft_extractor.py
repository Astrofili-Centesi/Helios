import argparse
import logging
import numpy as np
import scipy.io.wavfile as wav
import scipy.signal as signal
import csv
import sys
import os

def extract_full_fft(filename, timestamp, fft_length, window_type=None):
    # Read wav file
    sample_rate, data = wav.read(filename)
    if data.ndim > 1:
        data = data[:, 0]  # Take first channel if stereo

    # normalize
    data = data.astype(np.float32) / 32768.0

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

    # Convert to dB scale and format to two decimal places
    avg_fft_db = 20 * np.log10(avg_fft_magnitudes + 1e-10)  # Adding a small value to avoid log(0)
    avg_fft_db = [f"{x:.2f}" for x in avg_fft_db]

    # Calculate frequency values for each bin
    frequencies = [f"{i * sample_rate / fft_length:.2f}" for i in range(len(avg_fft_db))]

    return timestamp, frequencies, avg_fft_db

def main():
    parser = argparse.ArgumentParser(description="Extract an averaged FFT from a wav file using windowing.")
    parser.add_argument("filename", type=str, help="Path to the .wav file")
    parser.add_argument("timestamp", type=str, help="Timestamp for the FFT segment (copied as-is to output)")
    parser.add_argument("fft_length", type=int, help="Length (in samples) of each FFT segment")
    parser.add_argument("--window", type=str, default=None, help="Window type for FFT (e.g., hamming, hann)")
    parser.add_argument("--output", type=str, default="output.csv", help="Output CSV file")
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
    timestamp_str, frequencies, avg_fft_db = extract_full_fft(args.filename, args.timestamp, args.fft_length, args.window)

    # Check if file exists to determine write mode and header requirement
    file_exists = os.path.isfile(args.output)
    
    # Write or append to CSV
    with open(args.output, mode="a" if file_exists else "w", newline='') as file:
        writer = csv.writer(file)
        
        # Write header only if file doesn't exist
        if not file_exists:
            writer.writerow(["timestamp"] + frequencies)
        
        # Write the new row of data
        writer.writerow([timestamp_str] + avg_fft_db)
    
    logging.info(f"FFT data saved to {args.output}")

if __name__ == "__main__":
    main()
