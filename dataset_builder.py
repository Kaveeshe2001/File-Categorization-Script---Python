import os
import random
import shutil

# Set a random seed to ensure the shuffle is reproducible if you need to run it again
random.seed(42)

def merge_and_split_data(class_name, source_dirs, target_root, split_ratios=(0.70, 0.15, 0.15)):
    """
    Pools images from multiple demographic sources, shuffles them to remove bias, 
    and copies them into a strict train/val/test directory structure.
    
    """
    all_image_paths = []
    
    # Pool all files from both the dark skin and light skin directories
    for source_dir in source_dirs:
        class_dir = os.path.join(source_dir, class_name)
        if os.path.exists(class_dir):
            # Extract only valid image files
            files = [os.path.join(class_dir, f) for f in os.listdir(class_dir) 
                     if f.lower().endswith(('.png', '.jpg', '.jpeg'))]
            all_image_paths.extend(files)

    # Shuffle the pooled list to ensure demographic mixing in every batch
    random.shuffle(all_image_paths)

    # Calculate the exact mathematical split indices based on the total file count
    total_images = len(all_image_paths)
    train_end = int(total_images * split_ratios[0])
    val_end = train_end + int(total_images * split_ratios[1])

    # Slice the array into the three distinct datasets
    train_files = all_image_paths[:train_end]
    val_files = all_image_paths[train_end:val_end]
    test_files = all_image_paths[val_end:]

    # Helper function to create directories and copy the files safely
    def copy_files(file_list, split_name):
        dest_dir = os.path.join(target_root, split_name, class_name)
        # Automatically create the target folder if it does not exist
        os.makedirs(dest_dir, exist_ok=True)
        
        for file_path in file_list:
            shutil.copy(file_path, dest_dir)

    # Execute the physical copy operations
    copy_files(train_files, 'train')
    copy_files(val_files, 'val')
    copy_files(test_files, 'test')

    print(f"[{class_name.upper()}] Processing complete.")
    print(f"Total: {total_images} | Train: {len(train_files)} | Val: {len(val_files)} | Test: {len(test_files)}\n")


if __name__ == "__main__":
    
    # Define the locations of your raw demographic datasets
    source_directories = [
        r"D:\3rd sem\Research Ideas\Resnet Dataset\Raw_Fitzpatrick",
        r"D:\3rd sem\Research Ideas\Resnet Dataset\Raw_HAM10000"
    ]

    # Define where you want the final, highly structured dataset to be built
    target_directory = r"D:\3rd sem\Research Ideas\Skin_Cancer_Dataset"

    print("Initiating dataset demographic merge and structural split...\n")
    
    # Run the architectural split for both diagnostic classes
    merge_and_split_data("benign", source_directories, target_directory)
    merge_and_split_data("malignant", source_directories, target_directory)
    
    print("Operation finalized. The target directory is now ready for cloud compression.")