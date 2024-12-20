import os

import cv2 as cv
import numpy as np
from PIL import Image as pImg
from numpy import ndarray


def save_images(_data: ndarray, _out_path: str, _scale_factor: float, _name_suffix: str) -> None:
    for _frame_num in range(_data.shape[0]):
        _frame = _data[_frame_num]
        _image = pImg.fromarray(_frame, 'RGB')

        if _scale_factor > 1.0 or _scale_factor < 1.0:
            new_size = (int(_image.width * _scale_factor), int(_image.height * _scale_factor))
            _image = _image.resize(new_size, pImg.Resampling.LANCZOS)

        _image.save(os.path.join(_out_path, f"frame_{_frame_num:03}_{_name_suffix}.png"), 'PNG')


def save_video(_data: ndarray, _codec: str, _out_path: str, _width: int, _height: int, _scale_factor: float,
               _name_suffix: str) -> None:
    if _codec.upper() == "GIF":
        _video_file_name = os.path.join(_out_path, "video.gif")

        images = []

        for _frame in _data:
            _image = pImg.fromarray(_frame)

            if _scale_factor > 1.0 or _scale_factor < 1.0:
                new_size = (int(_image.width*_scale_factor), int(_image.height*_scale_factor))
                _image = _image.resize(new_size, pImg.Resampling.LANCZOS)

            images.append(_image)

        images[0].save(_video_file_name, save_all=True, append_images=images[1:], optimize=False, duration=40, loop=0)

        return
    elif _codec.upper() == "MP4":
        _video_file_name = os.path.join(_out_path, f"video_{_name_suffix}.mp4")
        _fourcc = cv.VideoWriter_fourcc(*'mp4v')
    elif _codec.upper() == "AVI":
        _video_file_name = os.path.join(_out_path, f"video_{_name_suffix}.avi")
        _fourcc = cv.VideoWriter_fourcc(*'DIVX')
    else:
        print("Invalid media codec selected")
        exit(1)

    _video_size = (_width, _height)

    if _scale_factor > 1.0 or _scale_factor < 1.0:
        _image = pImg.fromarray(_data[0])
        _video_size = (int(_image.width*_scale_factor), int(_image.height*_scale_factor))

    _video = cv.VideoWriter(_video_file_name, _fourcc, 10, _video_size)

    for _frame in _data:
        if _scale_factor > 1.0 or _scale_factor < 1.0:
            _image = pImg.fromarray(_frame)

            new_size = (int(_image.width*_scale_factor), int(_image.height*_scale_factor))
            _image = _image.resize(new_size, pImg.Resampling.LANCZOS)
            _frame = np.array(_image)

        _video.write(cv.cvtColor(_frame, cv.COLOR_RGB2BGR))

    cv.destroyAllWindows()
    _video.release()
