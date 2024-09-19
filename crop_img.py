import os
import cv2
import zarr
import tifffile
import numpy as np
from PIL import Image
from concurrent.futures import ThreadPoolExecutor

# Function to open a Zarr file
def open_zarr(path: str) -> zarr.Group:
    store = (zarr.ZipStore(path, mode="r") if path.endswith(".zip") else zarr.DirectoryStore(path))
    return zarr.group(store=store)

def img_sharp(img, channel_name):
    # Define thresholds for each channel
    thresholds = {
        'DAPI': (0, 3288),
        'boundary': (0, 5783),
        'interior_RNA': (0, 7375),
        'interior_protein': (0, 4759)
    }
    min_threshold, max_threshold = thresholds.get(channel_name, (0, 4759))

    # Clip intensity values within the threshold range
    img_clipped = np.clip(img, min_threshold, max_threshold)

    # Normalize image to the range 0-255 for 8-bit display
    img_normalized = cv2.normalize(img_clipped, None, 0, 255, cv2.NORM_MINMAX).astype(np.uint8)

    # Apply Gamma Correction
    gamma = 1.0  # Replace with the gamma value from your slider
    inv_gamma = 1.0 / gamma

    # Apply the gamma correction using the lookup table
    gamma_table = np.array([((i / 255.0) ** inv_gamma) * 255 for i in np.arange(0, 256)]).astype("uint8")
    img_gamma_corrected = cv2.LUT(img_normalized, gamma_table)

    return img_gamma_corrected

def load_img(dir, name, uesed_channel, channel_name):
    fullres_multich_img = tifffile.imread(os.path.join(dir, name), is_ome=True, level=0, aszarr=False)
    print("image_shape:", fullres_multich_img.shape)

    img = img_sharp(fullres_multich_img[uesed_channel], channel_name)
    return img

def load_lbl(dir, name, uesed_channel):
    mask = open_zarr(os.path.join(dir, name))
    seg_mask = np.array(mask["masks"][uesed_channel])
    print("seg_mask:", seg_mask.shape, seg_mask.dtype)
    print("the number of cell:", seg_mask.max())
    return seg_mask

def get_bb(mask):
    # Convert the mask to uint8
    mask_uint8 = mask.astype(np.uint8)

    # Find contours in the binary image
    contours, _ = cv2.findContours(mask_uint8, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    if len(contours) > 0:
        contour = contours[0]
        return cv2.boundingRect(contour)
    else:
        return None

def crop(image, label, output_dir):
    # Count the number of cells
    cell_ids = np.unique(label)
    cell_ids = cell_ids[cell_ids != 0]
    max_digits = len(str(len(cell_ids)))

    crop_img_dir = os.path.join(output_dir, "crop_img")
    crop_lbl_dir = os.path.join(output_dir, "crop_lbl")

    for subdir in ["0x", "2x", "4x"]:
        os.makedirs(os.path.join(crop_img_dir, subdir), exist_ok=True)
        os.makedirs(os.path.join(crop_lbl_dir, subdir), exist_ok=True)

    img_height, img_width = image.shape

    def process_cell(cell_id):
        mask = (label == cell_id)
        bbox = get_bb(mask)

        if bbox is not None:
            x, y, w, h = bbox

            def crop_within_bounds(x, y, w, h, factor=1):
                new_x = max(x - (factor - 1) * w // 2, 0)
                new_y = max(y - (factor - 1) * h // 2, 0)
                new_w = min(factor * w, img_width - new_x)
                new_h = min(factor * h, img_height - new_y)
                return new_x, new_y, new_w, new_h
            
            # Prepare bounding boxes for 0x, 2x, and 4x
            bboxes = {
                "0x": (x, y, w, h),
                "2x": crop_within_bounds(x, y, w, h, factor=2),
                "4x": crop_within_bounds(x, y, w, h, factor=4)
            }
            for factor in ["0x", "2x", "4x"]:
                x_f, y_f, w_f, h_f = bboxes[factor]
                crop_img = image[y_f:y_f+h_f, x_f:x_f+w_f]
                crop_lbl = mask[y_f:y_f+h_f, x_f:x_f+w_f]

                cv2.imwrite(f"{os.path.join(crop_img_dir, factor)}/img_{factor}_{str(cell_id).zfill(max_digits)}.png", crop_img)
                crop_lbl_pil = Image.fromarray(crop_lbl)
                crop_lbl_pil.save(f"{os.path.join(crop_lbl_dir, factor)}/lbl_{factor}_{str(cell_id).zfill(max_digits)}.png")

    # Use ThreadPoolExecutor to parallelize processing
    with ThreadPoolExecutor() as executor:
        executor.map(process_cell, cell_ids)

def main():
    base_dir = "/hpc/group/jilab/yw564/XeniumData/Xenium_human_Pancreas_FFPE" # modify to your data dir
    
    # Image info
    img_dir = os.path.join(base_dir, "morphology_focus") 
    img_name = "morphology_focus_0000.ome.tif" # # modify to image name you use (4 channels)
    img_channel_names = ['DAPI', 'boundary', 'interior_RNA', 'interior_protein'] # determin the channel names according to your image data
    uesed_img_channel = 1 # pick a channel that you want to crop

    # Label info
    lbl_dir = base_dir
    lbl_name = "cells.zarr.zip" # used label name
    lbl_channel_names = ["nucseg", "cellseg"] # {channel 0: nucseg, channel 1: cellseg}
    used_lbl_channel = 1 # pick a label channel that corresponds to the image channel name you use

    # Output info
    output_dir = "{}/preprocessing/{}".format(base_dir, lbl_channel_names[used_lbl_channel]) # modify to your output dir
    
    print("output_dir:", output_dir)
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)
        
    # Load image and sharp the image
    image = load_img(img_dir, img_name, uesed_img_channel, img_channel_names[uesed_img_channel])

    # Load label
    label = load_lbl(lbl_dir, lbl_name, used_lbl_channel)

    # Crop image and label
    crop(image, label, output_dir)
    
    print("Finished")
    
if __name__ == "__main__":
    main()
