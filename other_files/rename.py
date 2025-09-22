import os

folder = "pipe_images"

for filename in os.listdir(folder):
    old_path = os.path.join(folder, filename)
    
    # Skip if it's not a file
    if not os.path.isfile(old_path):
        continue
    
    # Only rename if the name is at least 4 characters long
    if len(filename) >= 4:
        new_filename = "pipe" + filename[4:]
        new_path = os.path.join(folder, new_filename)
        os.rename(old_path, new_path)
        print(f"Renamed: {filename} -> {new_filename}")

print("Renaming complete.")
