import os
import cv2
import tifffile
import numpy as np
import matplotlib.pyplot as plt
from scipy.ndimage import find_objects, gaussian_filter, generate_binary_structure, label, maximum_filter1d, binary_fill_holes


def masks_to_outlines(masks):
    """ get outlines of masks as a 0-1 array 
    
    Parameters
    ----------------

    masks: int, 2D or 3D array 
        size [Ly x Lx] or [Lz x Ly x Lx], 0=NO masks; 1,2,...=mask labels

    Returns
    ----------------

    outlines: 2D or 3D array 
        size [Ly x Lx] or [Lz x Ly x Lx], True pixels are outlines

    """
    if masks.ndim > 3 or masks.ndim < 2:
        raise ValueError('masks_to_outlines takes 2D or 3D array, not %dD array'%masks.ndim)
    outlines = np.zeros(masks.shape, bool)
    
    if masks.ndim==3:
        for i in range(masks.shape[0]):
            outlines[i] = masks_to_outlines(masks[i])
        return outlines
    else:
        slices = find_objects(masks.astype(int))
        for i,si in enumerate(slices):
            if si is not None:
                sr,sc = si
                mask = (masks[sr, sc] == (i+1)).astype(np.uint8)
                contours = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_NONE)
                pvc, pvr = np.concatenate(contours[-2], axis=0).squeeze().T            
                vr, vc = pvr + sr.start, pvc + sc.start 
                outlines[vr, vc] = 1
        return outlines

def visualization(img_file, lbl_file, output):
    image = cv2.imread(img_file, -1)
    print("img info:", image.shape, image.dtype, image.max(), image.min())

    lbl = tifffile.imread(lbl_file)
    print("The number of cell", lbl.dtype, lbl.shape, np.unique(lbl), len(np.unique(lbl)[1:]))

    outlines = masks_to_outlines(lbl)
    outX, outY = np.nonzero(outlines)

    image = np.repeat(image[...,None], 3, axis=2)
    print("new image:", image.shape)

    new_image = image.copy()
    new_image[outX, outY] = np.array([0, 0, 255])
    cv2.imwrite(output, new_image)

base_dir = "/hpc/group/jilab/yw564/XeniumData/Xenium_human_Pancreas_FFPE/preprocessing"
output_dir = "/hpc/group/jilab/yw564/XeniumData/Xenium_human_Pancreas_FFPE/preprocessing/visualization"
print("output_dir:", output_dir)
if not os.path.exists(output_dir):
    os.makedirs(output_dir)

image_file = os.path.join('{}/images'.format(base_dir), 'DAPI_C0.png')
label_file = os.path.join('{}/labels'.format(base_dir), 'nucseg_mask.tif')
output_filename = "{}/nucseg_vis.png".format(output_dir)
visualization(image_file, label_file, output_filename)

image_file = os.path.join('{}/images'.format(base_dir), 'boundary_C1.png')
label_file = os.path.join('{}/labels'.format(base_dir), 'cellseg_mask.tif')
output_filename = "{}/cellseg_vis.png".format(output_dir)
visualization(image_file, label_file, output_filename)
    



