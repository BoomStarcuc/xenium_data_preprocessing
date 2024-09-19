# Import Python libraries
# This script was tested with zarr v2.13.6
import os
import zarr
import numpy as np
# from PIL import Image
import tifffile

# Function to open a Zarr file
def open_zarr(path: str) -> zarr.Group:
    store = (zarr.ZipStore(path, mode="r")
    if path.endswith(".zip")
    else zarr.DirectoryStore(path)
    )
    return zarr.group(store=store)

# For example, use the above function to open the cells Zarr file, which contains segmentation mask Zarr arrays
mask_dir = "/hpc/group/jilab/yw564/XeniumData/Xenium_human_Pancreas_FFPE"
output_dir = "/hpc/group/jilab/yw564/XeniumData/Xenium_human_Pancreas_FFPE/preprocessing/labels"
root = open_zarr("{}/cells.zarr.zip".format(mask_dir))

'''
(root)
├── cell_id
├── cell_summary
├── masks
│   ├── 0
│   ├── 1
│   └── homogeneous_transform
└── polygon_sets
     ├── 0
     │   ├── cell_index
     │   ├── method
     │   ├── num_vertices
     │   └── vertices
     └── 1
         ├── cell_index
         ├── method
         ├── num_vertices
         └── vertices
'''

# Look at group array info and structure
root.info
root.tree() # shows structure, array dimensions, data types

# Create cell and nucleus segmentation mask np array objects to read or modify
# cellseg_mask = np.array(root["masks"][1], dtype = np.uint64)
# nucseg_mask = np.array(root["masks"][0], dtype = np.uint64)

cellseg_mask = np.array(root["masks"][1])
nucseg_mask = np.array(root["masks"][0])

# Show dimensions of the 2D segmentation mask arrays (also shown in .tree())
# .ndim() shows number of dimensions
# The shape should match the number of pixels in the morphology image.
print("cellseg:", cellseg_mask.shape, cellseg_mask.dtype)
print("nucseg:", nucseg_mask.shape, nucseg_mask.dtype)

# Show max value of cells in the masks (value=0 are background pixels)
# The .max() method counts all the values that are not 0, which should equal
# the total cells detected in the dataset (reported in e.g., analysis_summary.html
# summary tab metric).
print("the number of cell:", cellseg_mask.max())
print("the number of nuclei:", nucseg_mask.max())

im_path = os.path.join(output_dir, 'cellseg_mask.tif')
tifffile.imwrite(im_path, cellseg_mask)

im_path = os.path.join(output_dir, 'nucseg_mask.tif')
tifffile.imwrite(im_path, nucseg_mask)

# Examples for exploring file contents
# How to show array
# print(root["masks"][0][0:9].shape) # or root["masks/0"]
# print(root["cell_summary"]) #['Cell centroid in X', 'Cell centroid in Y', 'Cell area', 'Nucleus centroid in X', 'Nucleus centroid in Y', 'Nucleus area', 'z_level', 'Nucleus count']
# How to show attribute values
# print(root.attrs["major_version"])
# print(root.attrs["segmentation_methods"])

# How to list out attribute names and values
# print(dict(root.attrs.items()))
# print(dict(root['cell_summary'].attrs.items()))