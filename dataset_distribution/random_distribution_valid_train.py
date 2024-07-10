import os
import shutil
import random

def split_data(source_dir, dest_dir, train_percent=0.7):
    """
    Split data from a source directory into training and validation sets,
    copying corresponding images and label files to destination directories.

    Args:
        source_dir (str): Path to the source directory containing 'images' and 'labels' subdirectories.
        dest_dir (str): Path to the destination directory where split data will be copied.
        train_percent (float): Percentage of data to allocate for training (default: 0.7).
        valid_percent (float): Percentage of data to allocate for validation (default: 0.3).
    """
    if not os.path.isdir(source_dir):
        print(f"Source directory '{source_dir}' does not exist.")
        return
    
    os.makedirs(dest_dir, exist_ok=True)
    os.makedirs(os.path.join(dest_dir, 'train', 'images'), exist_ok=True)
    os.makedirs(os.path.join(dest_dir, 'train', 'labels'), exist_ok=True)
    os.makedirs(os.path.join(dest_dir, 'valid', 'images'), exist_ok=True)
    os.makedirs(os.path.join(dest_dir, 'valid', 'labels'), exist_ok=True)

    image_files = [f for f in os.listdir(os.path.join(source_dir, 'images')) if f.endswith('.jpg')]
    
    if not image_files:
        print(f"No image files found in source directory '{source_dir}'.")
        return

    random.shuffle(image_files)

    num_files = len(image_files)
    num_train = int(num_files * train_percent)
    num_valid = num_files - num_train

    train_files = image_files[:num_train]
    valid_files = image_files[num_train:num_train + num_valid]

    def copy_files(files, subset):
        """
        Copy image and label files corresponding to the specified subset ('train' or 'valid').

        Args:
            files (list): List of file names to copy.
            subset (str): Subset ('train' or 'valid') where files will be copied.
        """
        for file in files:
            if file.endswith('.jpg'):
                image_src = os.path.join(source_dir, 'images', file).replace("\\", "/")
                label_file = file[:-4] + '.txt'  
                label_src = os.path.join(source_dir, 'labels', label_file).replace("\\", "/")

                shutil.copy(image_src, os.path.join(dest_dir, subset, 'images', file)).replace("\\", "/")
                shutil.copy(label_src, os.path.join(dest_dir, subset, 'labels', label_file)).replace("\\", "/")

    copy_files(train_files, 'train')
    copy_files(valid_files, 'valid')

def main():
    source_directory = 'source_directory'
    destination_directory = 'destination_directory'

    split_data(source_directory, destination_directory)

if __name__ == "__main__":
    main()