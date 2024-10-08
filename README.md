# Xenium_data_preprocessing

## Overview
This repository was created for cropping whole tissue images into individual cell images with output including single-cell images at the original size, 2x original size, and 4x original size.

## Installation
1. Create conda environments, use:

``` 
conda create -n xenium_dp python=3.9
conda activate xenium_dp
```

2. Clone the repository, use:

``` 
git clone https://github.com/BoomStarcuc/xenium_data_preprocessing.git
```

3. Install dependencies, use:

```
pip install -r requirements.txt
```

## Data Example
In this repo, we used the [Xenium Human Pancreas](https://www.10xgenomics.com/datasets/ffpe-human-pancreas-with-xenium-multimodal-cell-segmentation-1-standard) as an example. If you are applying this to other datasets, please review the corresponding documentation and adjust the relevant parameters in the provided scripts accordingly.

**Note:** Since different datasets vary in size, you need to adjust the memory allocation of your device to avoid running out of memory. In this example, 50GB of memory was used.

## Crop whole tissue images into individual cell images

To run the algorithm on your data, use:

```
python crop_img.py
```

where 

- ```base_dir``` needs to be modified to your corresponding data path.
- ```used_img_channel``` and ```used_lbl_channel``` are corresponding to each other and are adjustable parameters. For example, in our current example, channel 1 is cell segmentation, while channel 0 is nuclear segmentation.
- ```img_dir```, ```img_name```, ```img_channel_names```, ```lbl_name```, and ```lbl_channel_names``` need to be checked if it is consistent with your used data. 

## Generate the image of each channel

To generate the image of each channel, use:

```
python read_tiff.py
```

where 

- ```base_dir``` needs to be modified to your corresponding data path.
- ```img_dir```, ```img_name``` and ```channel_names``` need to be checked if it is consistent with your used data.
- The final output is ```.png``` file.

## Generate the label of cell and nuclei

To generate the label of cell and nuclei, use:

```
python read_label.py
```

where ```mask_dir``` needs to be modified to your corresponding paths. The data structure of the segmentation mask can be checked in the Xenium document.


## Plot segmentation boundary in the corresponding image

To verify if the image correctly aligns with the corresponding segmentation after generating the image and label separately, use:

```
python plot_label.py
```

where 

- ```base_dir``` needs to be modified to your corresponding path.
- ```image_file``` and ```label_file``` need to be checked if it is consistent with your output directory and name.
