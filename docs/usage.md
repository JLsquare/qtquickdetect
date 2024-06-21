# How to Use

To use QTQuickDetect, follow these steps:

1. Import the images or videos you want to analyze through the 'Image Collections' or 'Video Collections' section.

2. Configure the presets through the 'Presets' section. Here are the preset settings:
    - Device: 'cpu' or 'gpu'
    - Half Precision: Enable or disable half precision (FP16)
    - IOU Threshold: Set the IOU threshold value
    - Image Format: Choose between 'png', 'jpg', etc.
    - Video Format: Choose between 'mp4', 'avi', etc.
    - Box Color: Set the RGBA color for the bounding box
    - Segment Color: Set the RGBA color for segmentation
    - Pose Colors: Set the RGBA colors for pose keypoints and lines
    - Text Color: Set the RGBA color for text annotations
    - Text Size: Set the size for text annotations

3. Select the desired inference task (detection, segmentation, classification, or pose), choose the weights you want to use, the preset, and the collection.

4. Run the inference. For images or videos, an inference result will be displayed. For live streams, the result will be displayed in real-time.

5. For images or videos, select the file and the model you want to see, select/deselect the objects you want to see, and save the result if needed.

6. Access old results through the 'Inference History' section.