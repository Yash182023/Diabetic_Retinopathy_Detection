import os
import cv2
import numpy as np
from tqdm import tqdm

def ben_graham_preprocessing(image_path=None, img=None, target_size=(299, 299)):
    """
    Ben Graham preprocessing pipeline for diabetic retinopathy:
    1. Scale radius to a standard size (300 pixels)
    2. Subtract local average color (equal to applying high-pass filter)
    3. Clip the negative values to 0
    4. Scale to [0,1] range
    
    Can accept either an image path or a pre-loaded image
    """
    if image_path is not None:
        img = cv2.imread(image_path)
        if img is None:
            print(f"Warning: Could not read image at {image_path}")
            return None
    
    if img is None:
        return None
    
    # Convert BGR to RGB
    img_rgb = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
    
    # Step 1: Detect and scale radius
    # First convert to grayscale for easier circle detection
    gray = cv2.cvtColor(img_rgb, cv2.COLOR_RGB2GRAY)
    
    # Detect circle (radius) of the retina
    circles = None
    rows = gray.shape[0]
    
    # Get the radius by approximation (in case circle detection fails)
    # The retina is usually centered and takes up most of the image
    radius = min(gray.shape[0], gray.shape[1]) // 2
    center_x = gray.shape[1] // 2
    center_y = gray.shape[0] // 2
    
    # Create a circular mask
    mask = np.zeros(gray.shape, dtype=np.uint8)
    cv2.circle(mask, (center_x, center_y), int(radius * 0.9), 1, -1)
    
    # Apply mask to original image
    masked_img = img_rgb.copy()
    for c in range(3):
        masked_img[:,:,c] = masked_img[:,:,c] * mask
    
    # Step 2: Subtract local average color (high-pass filter)
    # Apply Gaussian blur to get the local average
    smoothed = cv2.GaussianBlur(masked_img, (0, 0), 30)
    # Subtract local average from original image
    high_pass = cv2.addWeighted(masked_img, 4, smoothed, -4, 128)
    
    # Step 3: Clip negative values to 0
    high_pass = np.maximum(high_pass, 0)
    
    # Step 4: Scale to [0,1] range for model input
    high_pass = high_pass.astype(np.float32) / 255.0
    
    # Resize to target size
    if high_pass.shape[0] != target_size[0] or high_pass.shape[1] != target_size[1]:
        high_pass = cv2.resize(high_pass, target_size)
    
    return high_pass

def save_preprocessed_images(input_dir, output_dir, target_size=(299, 299)):
    """
    Apply Ben Graham preprocessing to all images in the input directory tree
    and save them with the same structure in the output directory.
    """
    # Create output directory if it doesn't exist
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)
    
    # Get a list of all image files
    image_files = []
    subfolders = ["Mild", "Moderate", "No_DR", "Proliferate_DR", "Severe"]
    
    for subfolder in subfolders:
        subfolder_path = os.path.join(input_dir, subfolder)
        if os.path.exists(subfolder_path):
            # Create corresponding output subfolder
            output_subfolder = os.path.join(output_dir, subfolder)
            if not os.path.exists(output_subfolder):
                os.makedirs(output_subfolder)
            
            # Add all images from this subfolder to the list
            for filename in os.listdir(subfolder_path):
                if filename.lower().endswith(('.png', '.jpg', '.jpeg', '.tif', '.tiff')):
                    image_files.append((
                        os.path.join(subfolder_path, filename),
                        os.path.join(output_subfolder, filename)
                    ))
    
    print(f"Found {len(image_files)} images to process")
    
    # Process all images with progress bar
    for input_path, output_path in tqdm(image_files):
        # Preprocess the image
        preprocessed = ben_graham_preprocessing(input_path, target_size=target_size)
        
        if preprocessed is not None:
            # Convert back to 0-255 range for saving
            preprocessed_255 = (preprocessed * 255).astype(np.uint8)
            # Convert back to BGR for OpenCV saving
            preprocessed_bgr = cv2.cvtColor(preprocessed_255, cv2.COLOR_RGB2BGR)
            # Save the preprocessed image
            cv2.imwrite(output_path, preprocessed_bgr)
        else:
            print(f"Failed to process {input_path}")

if __name__ == "__main__":
    # Define input and output directories directly
    input_dir = "G:/NEW_DATASET_DIABETIC_EYES/colored_images/"
    output_dir = "G:/BELL_GRAHAM_FILTERDATA"
    
    print(f"Preprocessing images and saving to {output_dir}")
    save_preprocessed_images(input_dir, output_dir)
    print("Processing complete!")