from PIL import Image
import os
import random
import glob

def superposition_cut(img_ir, img_background):
    """
    This function superimposes an infrared image onto a background image.

    Args:
        img_ir (Image): The infrared image to be superimposed.
        img_background (Image): The background image onto which the infrared image will be superimposed.

    Returns:
        Image: The resulting image after superimposing.
    """
    img_ir = img_ir.resize((img_ir.size[0] // 2, img_ir.size[1] // 2))

    if img_ir.size[0] > img_background.size[0] or img_ir.size[1] > img_background.size[1]:
        img_ir = img_ir.resize((img_ir.size[0] // 2, img_ir.size[1] // 2))

    if img_background.size[0] < img_ir.size[0]:
        position_x = 0
    else:
        position_x = random.randint(0, img_background.size[0] - img_ir.size[0])

    if img_background.size[1] < img_ir.size[1]:
        position_y = 0
    else:
        position_y = random.randint(img_background.size[1] // 3, img_background.size[1] - img_ir.size[1])

    img_background.paste(img_ir, (position_x, position_y), img_ir)
    
    return img_background

def get_ir_images(directory, search_pattern='*ir*'):
    """
    This function retrieves infrared images from the specified directory.

    Args:
        directory (str): Path to the directory to search for infrared images.
        search_pattern (str): The pattern to search for infrared images.

    Returns:
        list: List of paths to infrared images.
    """
    ir_images = []
    for root, dirs, files in os.walk(directory):
        ir_images.extend(glob.glob(os.path.join(root, search_pattern)))
    return ir_images

def process_images(ir_images_directory, background_images_directory, output_directory):
    """
    This function processes all infrared images in the specified directory by superimposing them onto random background images.

    Args:
        ir_images_directory (str): Path to the directory containing infrared images.
        background_images_directory (str): Path to the directory containing background images.
        output_directory (str): Path to the directory where the resulting images will be saved.
    """
    ir_images = get_ir_images(ir_images_directory)

    for ir_image in ir_images:
        try:
            if not os.path.isfile(ir_image):
                print(f"The path '{ir_image}' is not a regular file.")
                continue
            
            img_ir = Image.open(ir_image)
            background_images = os.listdir(background_images_directory)
            background_image = random.choice(background_images)
            background_image_path = os.path.join(background_images_directory, background_image)
            img_background = Image.open(background_image_path)

            result_image = superposition_cut(img_ir, img_background)

            image_name = os.path.basename(ir_image)
            output_path = os.path.join(output_directory, f'superimposition_{image_name}')
            result_image.save(output_path)
        except ValueError as e:
            print(f"Error processing image {ir_image}: {e}")

def main():
    ir_images_directory = 'ir_images_directory'
    background_images_directory = 'background_images_directory'
    output_directory = 'output_directory'

    process_images(ir_images_directory, background_images_directory, output_directory)

if __name__ == "__main__":
    main()