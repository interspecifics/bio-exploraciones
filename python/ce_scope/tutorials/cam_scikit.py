import cv2
from skimage.util import img_as_float, img_as_ubyte
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import skimage
from skimage.io import imread, imshow
from skimage.color import rgb2gray, rgb2hsv
from skimage.measure import label, regionprops, regionprops_table
from skimage.color import label2rgb
from scipy.ndimage import median_filter



capture = cv2.VideoCapture(0)



while (capture.isOpened()):
    ret, frame = capture.read()
    # convert
    tree = img_as_float(frame)
    # format
    blur_tree = skimage.filters.gaussian(tree, sigma=(5, 5), truncate=3.5, channel_axis=2)
    tree_gray = rgb2gray(blur_tree)
    tree_binary = tree_gray > 0.5
    # mask
    mask = median_filter(tree_binary, 10)
    red = tree[:,:,0] * mask
    green = tree[:,:,1] * mask
    blue = tree[:,:,2] * mask
    tree_mask = np.dstack((red, green, blue))
    # blobs
    tree_blobs = label(rgb2gray(tree_mask) > 0)
    tree_overlay = label2rgb(tree_blobs, image=tree, bg_label=0)
    #print(tree_blobs.shape)
    #cv_tree = img_as_ubyte(tree_blobs)
    cv_tree = tree_overlay[:, :,::-1]
    #imshow(tree_blobs, cmap = 'tab10');
    #plt.show()
    cv2.imshow('webCam', cv_tree)
    if (cv2.waitKey(1) == ord('s')):
        break

capture.release()
cv2.destroyAllWindows()