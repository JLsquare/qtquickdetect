import pytest
import numpy as np
import cv2 as cv
from pathlib import Path
from qtquickdetect.models.preset import Preset
from qtquickdetect.pipeline.torchvision_pose_pipeline import TorchVisionPosePipeline

# Create a test preset instance
preset = Preset("test")

@pytest.fixture
def test_images_path(tmp_path):
    """
    Fixture to provide test images path.
    """
    # Create a directory for test images
    images_dir = tmp_path / "test_images"
    images_dir.mkdir()

    # Create a dummy image
    dummy_image = np.random.randint(0, 256, (100, 100, 3), dtype=np.uint8)
    dummy_image_path = images_dir / "dummy_image.jpg"
    cv.imwrite(str(dummy_image_path), dummy_image)

    return [dummy_image_path]

@pytest.fixture
def test_videos_path(tmp_path):
    """
    Fixture to provide test videos path.
    """
    # Create a directory for test videos
    videos_dir = tmp_path / "test_videos"
    videos_dir.mkdir()

    # Create a dummy video
    dummy_video_path = videos_dir / "dummy_video.mp4"
    height, width = 100, 100
    fourcc = cv.VideoWriter_fourcc(*'mp4v')
    out = cv.VideoWriter(str(dummy_video_path), fourcc, 1.0, (width, height))
    for _ in range(10):
        frame = np.random.randint(0, 256, (height, width, 3), dtype=np.uint8)
        out.write(frame)
    out.release()

    return [dummy_video_path]

def test_torchvision_pose_pipeline_images(test_images_path):
    """
    Test the TorchVisionPosePipeline with image input.
    """
    weight = "keypointrcnn_resnet50_fpn"
    results_path = Path("results")
    pipeline = TorchVisionPosePipeline(weight, preset, test_images_path, None, None, results_path)

    def on_finished_file_signal(input_path, image_path, json_path):
        assert image_path.exists()
        assert json_path.exists()

    pipeline.finished_file_signal.connect(on_finished_file_signal)
    pipeline.run()

def test_torchvision_pose_pipeline_videos(test_videos_path):
    """
    Test the TorchVisionPosePipeline with video input.
    """
    weight = "keypointrcnn_resnet50_fpn"
    results_path = Path("results")
    pipeline = TorchVisionPosePipeline(weight, preset, None, test_videos_path, None, results_path)

    def on_finished_file_signal(input_path, video_path, json_path):
        assert video_path.exists()
        assert json_path.exists()

    pipeline.finished_file_signal.connect(on_finished_file_signal)
    pipeline.run()
