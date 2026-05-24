from PIL import Image
import os

def remove_green_background(input_path, output_path):
    try:
        img = Image.open(input_path)
        img = img.convert("RGBA")
        datas = img.getdata()

        new_data = []
        for item in datas:
            # Check for green pixels (allowing some tolerance)
            # Pure green is (0, 255, 0)
            if item[0] < 50 and item[1] > 200 and item[2] < 50:
                new_data.append((255, 255, 255, 0)) # Transparent
            else:
                new_data.append(item)

        img.putdata(new_data)
        img.save(output_path, "PNG")
        print(f"Processed {input_path} -> {output_path}")
    except Exception as e:
        print(f"Error processing {input_path}: {e}")

# Paths
base_path = os.path.dirname(os.path.abspath(__file__))
assets_path = os.path.join(base_path, "assets")

# Ensure assets directory exists
if not os.path.exists(assets_path):
    os.makedirs(assets_path)

# Process images
remove_green_background(os.path.join(base_path, "dog_one_green_1763943893241.png"), os.path.join(assets_path, "dog_one.png"))
remove_green_background(os.path.join(base_path, "dog_two_green_1763943905733.png"), os.path.join(assets_path, "dog_two.png"))
