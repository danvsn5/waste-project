import zipfile
import os

# Folder to zip
folder_path = "timber_images"

# Output zip file path
zip_filename = os.path.join(os.path.dirname(folder_path), "timber_images.zip")

# Create zip file
with zipfile.ZipFile(zip_filename, 'w', zipfile.ZIP_DEFLATED) as zipf:
    for root, dirs, files in os.walk(folder_path):
        for file in files:
            file_path = os.path.join(root, file)
            # Keep folder structure inside zip relative to folder_path
            arcname = os.path.relpath(file_path, start=folder_path)
            zipf.write(file_path, arcname)

print(f"Zipped '{folder_path}' into '{zip_filename}'")
