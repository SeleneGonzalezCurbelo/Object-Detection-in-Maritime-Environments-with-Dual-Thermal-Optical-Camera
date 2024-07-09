"""
This script combines two images using OpenCV's addWeighted function.
The foreground image is resized to match the dimensions of the background image,
and then both images are combined with a specified opacity.
"""

import cv2 as cv
import os

def load_image(image_path):
    """
    Load an image from disk.

    Parameters:
    - image_path (str): File path of the image.

    Returns:
    - Loaded image as numpy array if successful, None otherwise.
    """
    if not os.path.exists(image_path):
        print(f"File not found: {image_path}")
        return None
    image = cv.imread(image_path)
    if image is None:
        print(f"Failed to load image: {image_path}")
    return image

def resize_image(image, target_width, target_height):
    """
    Resize an image to a specified width and height.

    Parameters:
    - image (numpy array): Image to resize.
    - target_width (int): Target width of the resized image.
    - target_height (int): Target height of the resized image.

    Returns:
    - Resized image as numpy array.
    """
    return cv.resize(image, (target_width, target_height))

def blend_images(background, foreground):
    """
    Blend a foreground image onto a background image using OpenCV's addWeighted function.

    Parameters:
    - background (numpy array): Background image.
    - foreground (numpy array): Foreground image.
    - alpha (float): Weight of the foreground image in blending.

    Returns:
    - Blended image as numpy array.
    """
    return cv.addWeighted(background, 0.1, foreground, 1, 0)

def display_image(image, window_name='Image'):
    """
    Display an image in a new window until a key is pressed.

    Parameters:
    - image (numpy array): Image to display.
    - window_name (str): Name of the window.
    """
    cv.namedWindow(window_name, cv.WINDOW_NORMAL)
    cv.imshow(window_name, image)
    cv.waitKey(0)
    cv.destroyAllWindows()

def save_image(image, save_path):
    """
    Save an image to disk.

    Parameters:
    - image (numpy array): Image to save.
    - save_path (str): File path to save the image.
    """
    cv.imwrite(save_path, image)
    print(f"Image saved to: {save_path}")

def blending_openvc(background_path, foreground_path):
    """
    Combine a background image with a foreground image using OpenCV's addWeighted function.

    Parameters:
    - background_path (str): Background image file path.
    - foreground_path (str): Foreground image file path.
    """
    background = load_image(background_path)
    foreground = load_image(foreground_path)

    if background is None or foreground is None:
        exit(1)

    foreground_resized = resize_image(foreground, background.shape[1], background.shape[0])

    blended_image = blend_images(background, foreground_resized)
    cwd = os.getcwd()

    filename = "blended_result.jpg"

    result_path = os.path.join(cwd, filename)
    
    save_image(blended_image, result_path)

    display_image(blended_image, window_name='Blended Image')


def main():
    background_path = "image1.jpg"
    foreground_path = "image2.jpg"

    blending_openvc(background_path, foreground_path)

if __name__ == "__main__":
    main()