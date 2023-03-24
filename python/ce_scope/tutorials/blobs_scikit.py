# conda create -n scope python=3.9
# pip install opencv-python matplotlib scikit-image 
# pip install tqdm pandas
# pip install ipython
#

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import skimage
from skimage.io import imread, imshow
from skimage.color import rgb2gray, rgb2hsv
from skimage.measure import label, regionprops, regionprops_table
from skimage.filters import threshold_otsu
from scipy.ndimage import median_filter
from matplotlib.patches import Rectangle
from tqdm import tqdm

# 1
tree = imread('polarized_meat_800.jpg')
imshow(tree);
plt.show()

# 2 blur
blur_tree = skimage.filters.gaussian(tree, sigma=(5, 5), truncate=3.5, channel_axis=2)
# 3 thresh
tree_gray = rgb2gray(blur_tree)
otsu_thresh = threshold_otsu(tree_gray)
tree_binary = tree_gray > 0.5
#imshow(tree_binary, cmap = 'gray');
#plt.show()
# 4 mask
mask = median_filter(tree_binary, 10)
red = tree[:,:,0] * mask
green = tree[:,:,1] * mask
blue = tree[:,:,2] * mask
tree_mask = np.dstack((red, green, blue))
plt.figure(num=None, figsize=(8, 6), dpi=80)
#imshow(tree_mask);
#plt.show()
#5. label
tree_blobs = label(rgb2gray(tree_mask) > 0)
imshow(tree_blobs, cmap = 'tab10');
plt.show()


# TO DO
# realtime camera
# tracking...
# gui









# ----------------------
# .X1
def threshold_checker(image):
    thresholds =  np.arange(0.1,1.1,0.1)
    tree_gray = rgb2gray(image)
    fig, ax = plt.subplots(2, 5, figsize=(17, 10))
    for n, ax in enumerate(ax.flatten()):
        ax.set_title(f'Threshold  : {round(thresholds[n],2)}',      
                       fontsize = 16)
        threshold_tree = tree_gray < thresholds[n]
        ax.imshow(threshold_tree);
        ax.axis('off')
    fig.tight_layout()

threshold_checker(tree)
plt.show()