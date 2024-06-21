# Installation

QTQuickDetect has been tested on both Windows and Linux, with Python 3.10, 3.11, and 3.12. MacOS is currently not supported.

## Assisted Installation

The easiest way to install QTQuickDetect is by having [conda](https://docs.conda.io/en/latest/) or [miniconda](https://docs.conda.io/en/latest/miniconda.html) installed on your system. Please refer to their respective documentation for installation instructions.

Once you have either conda or miniconda installed, please download QTQuickDetect from the [releases page](https://qtquickdetect.feur.live/) and extract the contents to a folder of your choice.

Finally, navigate to the folder where you extracted QTQuickDetect and run the following commands:

```bash
# navigate to the root folder of the extracted QTQuickDetect zip archive
conda create -n qtquickdetect python=3.10
conda activate qtquickdetect
pip install qtquickdetect
```

Whenever you wish to use QTQuickDetect, you can simply run both :

```bash
conda activate qtquickdetect
qtquickdetect
```

## Advanced Installation

You can install QTQuickDetect without any extra dependencies by simply creating a python virtual environement, activating it, and installing the software using `pip install <path_to_qtquickdetect>`.

### GPU Acceleration

#### Windows

By default, QTQuickDetect will use the CPU for all computations. If you have a compatible NVIDIA GPU, you can install the GPU version of PyTorch by following instructions at the [PyTorch website](https://pytorch.org/get-started/previous-versions/#v230). Please make sure to install a pytorch version from the 2.3.x series, and a torchvision version from the 0.18.x series.

#### Linux

Unlike windows, the default torch package comes with CUDA (NVidia) support. If you do not wish to have the extra libraries installed, you can install the CPU-only version of PyTorch by following instructions at the [PyTorch website](https://pytorch.org/get-started/previous-versions/#v230). Please make sure to install a pytorch version from the 2.3.x series, and a torchvision version from the 0.18.x series.

For Radeon GPU owners, you may try your luck with the ROCm version of PyTorch, available from [the same page](https://pytorch.org/get-started/previous-versions/#v230). Please note that the 2.3**.0** release is broken and doesn't work, try to install the 2.3**.1** release instead.

- For Navi 2 GPUs (rx 6xxx series), please set the `HSA_OVERRIDE_GFX_VERSION=10.3.0` environment variable before running QTQuickDetect.
- For Navi 3 GPUs (rx 7xxx series), everything should work smoothly.

If your card isn't listed above, you're on your own, *good luck*.