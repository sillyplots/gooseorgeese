from PIL import Image
import numpy as np
import os

def remove_green_background(input_path, output_path):
    try:
        img = Image.open(input_path)
        img = img.convert("RGBA")

        # Convert image to numpy array for faster processing
        data = np.array(img)

        # Extract color channels
        r, g, b, a = data.T

        # Find green pixels (allowing some tolerance)
        # Pure green is (0, 255, 0)
        green_areas = (r < 50) & (g > 200) & (b < 50)

        # Replace green pixels with transparent
        data[green_areas.T] = [255, 255, 255, 0]

        # Convert back to PIL Image and save
        img_out = Image.fromarray(data)
        img_out.save(output_path, "PNG")
        print(f"Processed {input_path} -> {output_path}")
    except Exception as e:
        print(f"Error processing {input_path}: {e}")

if __name__ == "__main__":
    # Paths
    base_path = "/Users/charliethompson/.gemini/antigravity/brain/3b99eb67-5ffe-4d25-b6c8-0a8ab33c2b84"
    assets_path = "/Users/charliethompson/.gemini/antigravity/scratch/goose-or-geese/assets"

    # Ensure assets directory exists
    try:
        if not os.path.exists(assets_path):
            os.makedirs(assets_path)

        # Process images
        remove_green_background(f"{base_path}/dog_one_green_1763943893241.png", f"{assets_path}/dog_one.png")
        remove_green_background(f"{base_path}/dog_two_green_1763943905733.png", f"{assets_path}/dog_two.png")
    except Exception as e:
        print(f"Skipping processing because: {e}")
