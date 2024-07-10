import os

def modify_to_class_boat(folder_path):
    """
    Modify all .txt files in the specified folder by changing the first value
    of each line to '0' (class boat).

    Args:
    folder_path (str): The path to the folder containing .txt files to be modified.
    """
    file_list = os.listdir(folder_path)

    for file_name in file_list:
        if file_name.endswith('.txt'):
            file_path = os.path.join(folder_path, file_name).replace("\\", "/")
            with open(file_path, 'r') as file:
                lines = file.readlines()
                print(file_path)
                print(lines)
            
            if lines:
                modified_lines = [line.strip().split() for line in lines]
                for line in modified_lines:
                    line[0] = '0'
                
                with open(file_path, 'w') as file:
                    for line in modified_lines:
                        file.write(' '.join(line).replace("\\", "/") + '\n')

def main():
    folder_path = "E:/Practicas/fiftyone/Datasets finales/a/labels"

    modify_to_class_boat(folder_path)

    print("The .txt files in the folder have been modified.")

if __name__ == "__main__":
    main()