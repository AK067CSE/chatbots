import zipfile
import os

zip_path = r"C:\Users\abhik\Downloads\sales\salesbot\gemma3-text2sql.zip"
extract_path = r"C:\Users\abhik\Downloads\sales\salesbot"

print(f"Unzipping {zip_path}...")
with zipfile.ZipFile(zip_path, 'r') as zip_ref:
    zip_ref.extractall(extract_path)

print("Unzip complete. Exploring structure...")
for root, dirs, files in os.walk(extract_path):
    level = root.replace(extract_path, '').count(os.sep)
    indent = ' ' * 2 * level
    print(f'{indent}{os.path.basename(root)}/')
    if level < 2:
        subindent = ' ' * 2 * (level + 1)
        for file in files[:10]:
            print(f'{subindent}{file}')
