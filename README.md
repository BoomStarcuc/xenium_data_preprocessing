# Xenium_data_preprocessing

## Overview
This repository was created for cropping whole tissue images into individual cell images with output including single-cell images at the original size, twice the size, and four times the size.

## Installation
1. Create conda environments, use:

``` 
conda create -n xenium_dp python=3.9
conda activate xenium_dp
```

2. Clone the repository, use:

``` 
https://github.com/BoomStarcuc/xenium_data_preprocessing.git
```

3. Install dependencies, use:

```
pip install -r requirement.txt
```

## Cropping whole tissue images into individual cell images

To run the algorithm on your data, use:

```
python crop_img.py
```

where ```img_dir```, ```img_name```, ```img_channel_names```, ```uesed_img_channel```, ```lbl_dir```, ```lbl_name```, and ```lbl_channel_names```, ```used_lbl_channel```, and '''output_dir''' in this ```crop_img.py``` need to be modified to your corresponding paths, names, and specific channel.

## Generate the image of each channel

To generate the image of each channel, use:

```
python read_tiff.py
```

where ```img_dir```, ```img_name```, ```img_channel_names```, and '''output_dir''' need to be modified to your corresponding paths and image and channel names. The output format is '''.png''' file.

## Generate the label of cell and nuclei

To generate the label of cell and nuclei, use:

```
python read_label.py
```

where ```img_dir```, ```img_name```, ```img_channel_names```, and '''output_dir''' need to be modified to your corresponding paths and image and channel names. The output format is '''.png''' file.
