import cv2 as cv
import numpy as np
from PIL import Image

def cv2pillow(img):
    return Image.fromarray(np.uint8(img))

