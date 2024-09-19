import tifffile
import os
import cv2
import numpy as np
import matplotlib.pyplot as plt

def img_sharp(img, channel_name):
    # Define thresholds for each channel, which is defined based on Xenium Explorer 2 software 
    thresholds = {
        'DAPI': (0, 3288),
        'boundary': (0, 5783),
        'interior_RNA': (0, 7375),
        'interior_protein': (0, 4759)
    }
    min_threshold, max_threshold = thresholds.get(channel_name, (0, 3288))

    # Clip intensity values within the threshold range
    img_clipped = np.clip(img, min_threshold, max_threshold)

    # Normalize image to the range 0-255 for 8-bit display
    img_normalized = cv2.normalize(img_clipped, None, 0, 255, cv2.NORM_MINMAX).astype(np.uint8)

    # Apply Gamma Correction
    gamma = 1.0  # Replace with the gamma value from your slider
    inv_gamma = 1.0 / gamma

    # Build a lookup table for gamma correction
    gamma_table = np.array([((i / 255.0) ** inv_gamma) * 255 for i in np.arange(0, 256)]).astype("uint8")

    # Apply the gamma correction using the lookup table
    img_gamma_corrected = cv2.LUT(img_normalized, gamma_table)

    return img_gamma_corrected


img_dir = "/hpc/group/jilab/yw564/XeniumData/Xenium_human_Pancreas_FFPE/morphology_focus"
img_name = "morphology_focus_0000.ome.tif" # These four images, including "morphology_focus_0000.ome.tif", "morphology_focus_0001.ome.tif", morphology_focus_0002.ome.tif, and morphology_focus_0003.ome.tif, are the same with four channels 'DAPI', 'boundary', 'interior_RNA', and 'interior_protein'
output_dir = "/hpc/group/jilab/yw564/XeniumData/Xenium_human_Pancreas_FFPE/preprocessing/images"
channel_names = ['DAPI', 'boundary', 'interior_RNA', 'interior_protein']

print("output_dir:", output_dir)
if not os.path.exists(output_dir):
    os.makedirs(output_dir)

# Load full resolution image channels
# The following may produce a warning: 'OME series cannot read multi-file pyramids'. This is because tifffile does not support loading a pyramidal multi-file OME-TIFF file. Only the full resolution (level=0) data will load for all channels in the directory.
fullres_multich_img = tifffile.imread(
"{}/{}".format(img_dir, img_name), is_ome=True, level=0, aszarr=False)

# Examine shape of array (number of channels, height, width), e.g. (4, 13770, 34155)
print("image_shape:", fullres_multich_img.shape)
# Extract number of channels, e.g. 4
n_ch = fullres_multich_img.shape[0]

# Plot each channel
for i in range(n_ch):
    cv2.imwrite("{}/{}_C{}.png".format(output_dir, channel_names[i], i), img_sharp(fullres_multich_img[i], channel_names[i]))
