import numpy as np
import tensorflow as tf
import skimage.transform
from distutils.version import LooseVersion


def resize(image, output_shape, order=1, mode='constant', cval=0, clip=True,
           preserve_range=False, anti_aliasing=False, anti_aliasing_sigma=None):
    """A wrapper for Scikit-Image resize().

    Scikit-Image generates warnings on every call to resize() if it doesn't
    receive the right parameters. The right parameters depend on the version
    of skimage. This solves the problem by using different parameters per
    version. And it provides a central place to control resizing defaults.
    """
    if LooseVersion(skimage.__version__) >= LooseVersion("0.14"):
        # New in 0.14: anti_aliasing. Default it to False for backward
        # compatibility with skimage 0.13.
        return skimage.transform.resize(
            image, output_shape,
            order=order, mode=mode, cval=cval, clip=clip,
            preserve_range=preserve_range, anti_aliasing=anti_aliasing,
            anti_aliasing_sigma=anti_aliasing_sigma)
    else:
        return skimage.transform.resize(
            image, output_shape,
            order=order, mode=mode, cval=cval, clip=clip,
            preserve_range=preserve_range)

def generate_segmentation_from_masks(instance_masks, processed_bboxes, height, width):
    """Converts a mask generated by the neural network to a format similar
    to its original shape.
    mask: [height, width] of type float. A small, typically 28x28 mask.
    bbox: [y1, x1, y2, x2]. The box to fit the mask in.

    Returns a binary mask with the same size as the original image.
    """
    threshold = 0.7
    full_mask = np.zeros([processed_bboxes.shape[0], height, width], dtype=np.uint8)
    for i in range(processed_bboxes.shape[0]):
        x1, y1, x2, y2 = processed_bboxes[i].astype("int")
        mask = instance_masks[i]
        mask = resize(mask, (y2, x2))
        mask = np.where(mask >= threshold, 1, 0).astype(np.uint8)

        # Put the mask in the right location.
        full_mask[i, y1:y1+y2, x1:x1+x2] = mask

    return full_mask
