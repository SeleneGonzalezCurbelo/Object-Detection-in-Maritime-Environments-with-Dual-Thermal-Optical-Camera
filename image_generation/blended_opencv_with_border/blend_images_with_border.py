"""
This script demonstrates alpha blending of a foreground image onto a background image.
The foreground image is resized and blended with the background using user-defined alpha values,
allowing interactive adjustment of transparency levels.
"""

import cv2 as cv
import numpy as np

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

def load_image(image_path):
    """
    Load an image from disk.

    Parameters:
    - image_path (str): File path of the image.

    Returns:
    - Loaded image as numpy array if successful, None otherwise.
    """
    image = cv.imread(image_path)
    if image is None:
        print(f"Failed to load image: {image_path}")
    return image

def expand_with_neighbors(image, target_size):
    """
    Expand an image to fit within a target size by replicating borders.

    Parameters:
    - image (numpy array): Input image to be expanded.
    - target_size (tuple): Desired size (width, height) to expand the image to.

    Returns:
    - Resized image as numpy array with replicated borders.
    """
    height, width = image.shape[:2]

    delta_w = target_size[0] - width
    delta_h = target_size[1] - height

    top = delta_h // 2
    bottom = delta_h - top
    left = delta_w // 2
    right = delta_w - left

    bordered_image = cv.copyMakeBorder(image, top, bottom, left, right, cv.BORDER_REPLICATE)

    # Resize the bordered image to the target size
    resized_image = cv.resize(bordered_image, target_size)

    return resized_image

def get_alpha_from_user():
    """
    Prompt the user to enter an alpha value for blending, handling non-numeric inputs gracefully.

    Returns:
    - float: Alpha value entered by the user.
    """
    while True:
        try:
            alpha = float(input("Enter alpha value (0.0 to 1.0): "))
            if 0.0 <= alpha <= 1.0:
                return alpha
            else:
                print("Alpha value must be between 0.0 and 1.0")
        except ValueError:
            print("Please enter a valid number")

def get_choice_from_user(prompt_text):
    """
    Prompt the user to enter a choice based on prompt_text, handling non-numeric inputs gracefully.

    Parameters:
    - prompt_text (str): Text to prompt the user with.

    Returns:
    - int: Choice entered by the user (0 or 1).
    """
    while True:
        try:
            choice = int(input(prompt_text))
            if choice == 0 or choice == 1:
                return choice
            else:
                print("Please enter either 0 or 1")
        except ValueError:
            print("Please enter a valid number (0 or 1)")

def blend_images_with_border(background_path, foreground_path):
    """
    Blend a foreground image onto a background image with user-defined alpha values.

    Parameters:
    - background_path (str): File path of the background image.
    - foreground_path (str): File path of the foreground image.
    """
    # Load images
    background = load_image(background_path)
    foreground = load_image(foreground_path)

    if background is None or foreground is None:
        exit(1)

    target_size = (500, 500)

    expanded_image = expand_with_neighbors(foreground, target_size)

    display_image(background, window_name='Background Image')

    foreground_resized = cv.resize(expanded_image, background.shape[1::-1])

    display_image(foreground_resized, window_name='Expanded Foreground Image')

    choice = 1

    while choice:
        alpha = get_alpha_from_user()

        blended_image = cv.addWeighted(background, alpha, foreground_resized, 1 - alpha, 0)

        cv.imwrite('alpha_blend_result.png', blended_image)

        blended_image_display = cv.imread('alpha_blend_result.png')
        cv.imshow("alpha blending", blended_image_display)
        cv.waitKey(0)

        choice = get_choice_from_user("Enter 1 to continue blending or 0 to exit: ")

    cv.destroyAllWindows()

def main():
    background_path = "image1.jpg"
    foreground_path = "image2.jpg"

    blend_images_with_border(background_path, foreground_path)

if __name__ == "__main__":
    main()
