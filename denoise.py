import cv2
import numpy as np

img = cv2.imread('data/1 (copy).png',0)
dst = cv2.fastNlMeansDenoising(img)
cv2.imwrite('data/1denoised.png', dst)