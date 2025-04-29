# Easy Compositor

This is a GUI-based Python application that merges two sequences of PNG images—typically a background and a foreground—into a single MP4 video. It is especially useful in 3D animation workflows where rendering complex background scenes can be time-consuming.

The background (e.g., environment or scener) can be rendered once, while the foreground (e.g., characters or moving elements) can be rendered separately whenever adjustments are made. This workflow can reduces total rendering time and improves iteration efficiency. The tool also provides simple compositing effects such as blur and fog, allowing for quick enhancement of visual depth and atmosphere without the need for complex post-processing software. 

## Versions

- mar141.py :
First version using OpenCV to process and encode the final MP4 video from the combined PNG frames.

- mar142.py :
Second version that uses FFmpeg with single-threading, resulting in faster rendering performance compared to the first version.

- mar143.py :
Third version using FFmpeg with multi-threading, resulting in faster rendering performance compared to the second version. 


## Other files

- 360p.png : Image file of the software's logo.
