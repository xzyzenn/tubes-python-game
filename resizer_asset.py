import os
from PIL import Image

input_root = "assets/images/palu"
output_root = "assets/images/turrets"

new_size = (96, 96)

for dirpath, dirnames, filenames in os.walk(input_root):
    for filename in filenames:
        if filename.endswith(".png"):
            input_path = os.path.join(dirpath, filename)

            # Hitung path relatif terhadap input_root
            relative_path = os.path.relpath(input_path, input_root)

            # Buat path output berdasarkan struktur yang sama
            output_path = os.path.join(output_root, relative_path)
            output_dir = os.path.dirname(output_path)
            os.makedirs(output_dir, exist_ok=True)

            # Resize dan simpan
            img = Image.open(input_path)
            img = img.resize(new_size, Image.NEAREST)
            img.save(output_path)

print("resized!")
