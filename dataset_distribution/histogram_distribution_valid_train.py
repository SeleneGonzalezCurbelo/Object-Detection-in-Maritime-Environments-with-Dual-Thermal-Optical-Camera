import os
import cv2
import numpy as np
from sklearn.metrics.pairwise import euclidean_distances
import shutil

def calculate_color_histogram(image):
    """
    Calculate the color histogram of an image.

    Args:
        image: numpy array representing the image.

    Returns:
    - hist: flattened numpy array representing the color histogram.
    """
    hist = cv2.calcHist([image], [0, 1, 2], None, [8, 8, 8], [0, 256, 0, 256, 0, 256])
    hist = cv2.normalize(hist, hist).flatten() 
    return hist

def resize_image(image, target_size):
    """
    Resize an image to the specified target size.

    Args:
        image: numpy array representing the image.
        target_size: tuple representing the target size (width, height).

    Returns:
    - resized_image: numpy array representing the resized image.
    """
    resized_image = cv2.resize(image, target_size)
    return resized_image

    
def distribute_images(images_folder_path, labels_folder_path):
    """
    Distribute images into training and validation sets based on histogram distances.

    Args:
        images_folder_path: path to the folder containing images.
        labels_folder_path: path to the folder containing labels.

    This function calculates color histograms for images, computes distances between them,
    and then copies them into respective training and validation folders.
    """
    images = []
    labels = []

    target_size = (1280, 1280)

    image_names = os.listdir(images_folder_path)
    label_names = os.listdir(labels_folder_path)

    for filename in os.listdir(images_folder_path):
        image_path = os.path.join(images_folder_path, filename)
        image = cv2.imread(image_path)
        try:
            image = resize_image(image, target_size)
        except Exception as e:
            print(f"Error resizing image '{filename}': {e}")
        if image is not None:
            images.append(image)
            label_path = os.path.join(labels_folder_path, filename.replace('.png', '.txt'))  
            label_path = label_path.replace("\\", "/")
            if not os.path.exists(label_path):
                label_path = os.path.join(labels_folder_path, filename.replace('.jpg', '.txt'))  
                label_path = label_path.replace("\\", "/")
            with open(label_path, 'r') as file:
                label = file.read().strip()  
                label = label.replace("\\", "/")
                labels.append(label)

    images = np.array(images)
    labels = np.array(labels)

    images_features = np.array([calculate_color_histogram(image) for image in images])

    distances = euclidean_distances(images_features)
    sorted_indices = np.argsort(distances, axis=1)

    num_total_images = len(images)
    num_train_images = int(num_total_images * 0.7)  

    if num_train_images < 0.7 * num_total_images:
        num_train_images += 1

    num_validation_images = num_total_images - num_train_images

    train_indices = set()
    current_idx = sorted_indices.shape[0] - 1  
    while len(train_indices) < num_train_images:
        for idx in sorted_indices[current_idx]:
            if idx not in train_indices:
                train_indices.add(idx)
                if len(train_indices) >= num_train_images:
                    break
        current_idx -= 1

    valid_indices = []
    for idx in range(num_total_images):
        if idx not in train_indices:
            valid_indices.append(idx)
            if len(valid_indices) >= num_validation_images:
                break

    train_folder = "train_folder"
    valid_folder = "valid_folder"
    os.makedirs(train_folder, exist_ok=True)
    os.makedirs(valid_folder, exist_ok=True)

    train_images_folder = os.path.join(train_folder, "images")
    train_labels_folder = os.path.join(train_folder, "labels")
    valid_images_folder = os.path.join(valid_folder, "images")
    valid_labels_folder = os.path.join(valid_folder, "labels")
    os.makedirs(train_images_folder, exist_ok=True)
    os.makedirs(train_labels_folder, exist_ok=True)
    os.makedirs(valid_images_folder, exist_ok=True)
    os.makedirs(valid_labels_folder, exist_ok=True)

    for idx in train_indices:
        image_name = image_names[idx]
        label_name = label_names[idx]
        
        source_image_path = os.path.join(images_folder_path, image_name)
        destination_image_path = os.path.join(train_images_folder, image_name)
        shutil.copyfile(source_image_path, destination_image_path)

        source_label_path = os.path.join(labels_folder_path, label_name)
        destination_label_path = os.path.join(train_labels_folder, label_name)
        shutil.copyfile(source_label_path, destination_label_path)

    for idx in valid_indices:
        image_name = image_names[idx]
        label_name = label_names[idx]
        
        source_image_path = os.path.join(images_folder_path, image_name)
        destination_image_path = os.path.join(valid_images_folder, image_name)
        shutil.copyfile(source_image_path, destination_image_path)

        source_label_path = os.path.join(labels_folder_path, label_name)
        destination_label_path = os.path.join(valid_labels_folder, label_name)
        shutil.copyfile(source_label_path, destination_label_path)

    print(f"Copied {len(train_indices)} images and labels to the training set.")
    print(f"Copied {len(valid_indices)} images and labels to the validation set.")


def main():
    images_folder_path = "images_folder_path"
    labels_folder_path = "labels_folder_paths"

    distribute_images(images_folder_path, labels_folder_path)

if __name__ == "__main__":
    main()