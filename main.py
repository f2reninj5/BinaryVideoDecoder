import argparse
import os
import struct
import time
from argparse import Namespace
from typing import BinaryIO

import numpy as np
from numpy import ndarray

from saving import save_images, save_video


def get_args() -> Namespace:
    parser = argparse.ArgumentParser(description='Optional app description')

    parser.add_argument('--frames', action='store_true',
                        help="When enabled, program will output the individual frames")
    parser.add_argument('--bin', type=str, nargs=1, help="path to input binary file. Defaults to 'out.bin'")
    parser.add_argument('--codec', type=str, nargs=1,
                        help="The video extension to use, AVI, MP4 or GIF. Defaults to MP4")
    parser.add_argument('--compare', type=str, nargs=1,
                        help="Specify a path to another binary which will be put beside the first binary in the output.")
    parser.add_argument('--overwrite', action='store_true',
                        help="when enabled, videos/images will not be stored in subfolders of the time")

    return parser.parse_args()


def get_file_information(_file: BinaryIO) -> (int, int, int, int):
    print(f"Reading data for {_file.name}")
    _numofframes: int = struct.unpack('<Q', _file.read(8))[0]
    _numofchannels: int = struct.unpack('B', _file.read(1))[0]
    _height: int = struct.unpack('B', _file.read(1))[0]
    _width: int = struct.unpack('B', _file.read(1))[0]

    print(f"Number of frames: {_numofframes}")
    print(f"Number of channels: {_numofchannels}")
    print(f"Height: {_height}")
    print(f"Width: {_width}")
    print()

    return _numofframes, _numofchannels, _width, _height


def read_bin() -> ndarray:
    _filename = args.bin[0] if args.bin else "test.bin"

    _compare_file_name = args.compare[0] if args.compare else None
    _compare_file: (BinaryIO | None) = open(_compare_file_name, 'rb') if args.compare else None

    if not os.path.exists(_filename) or (not (os.path.exists(_compare_file_name) if _compare_file else True)):
        print("The specified input file does not exist:")
        print(_filename)
        exit(1)

    with open(_filename, 'rb') as _file:
        _src_number_of_frames, _src_number_of_channels, _src_width, _src_height = get_file_information(_file)

        if _compare_file:
            _comp_number_of_frames, _comp_number_of_channels, _comp_width, _comp_height = get_file_information(
                _compare_file)

        _output_width = _src_width + _comp_width if _compare_file else _src_width

        _data = np.zeros((_src_number_of_frames, _output_width, _src_height, _src_number_of_channels), np.uint8)

        for frame in range(_src_number_of_frames):
            for c in range(_src_number_of_channels):
                for x in range(_output_width):
                    for y in range(_src_height):
                        if _compare_file and x >= _src_width:
                            _pixel = struct.unpack('B', _compare_file.read(1))[0]
                        else:
                            _pixel = struct.unpack('B', _file.read(1))[0]

                        _data[frame][x][y][c] = _pixel

    if _compare_file:
        _compare_file.close()

    return _data


if __name__ == "__main__":
    args = get_args()

    data = read_bin()

    _, height, width, _ = data.shape

    out_path = "out" if args.overwrite else os.path.join("out", str(int(time.time())))

    if args.overwrite:
        for file in os.listdir(out_path):
            os.remove(os.path.join(out_path, file))

    if args.frames:
        save_images(data, out_path)

    if not args.frames:
        codec: str = args.codec[0] if args.codec else 'MP4'
        save_video(data, codec, out_path, width, height)

    print("Finished.")
