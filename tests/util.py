import os
import hashlib

def get_all_src_py_files_hash():
    hash_sha256 = hashlib.sha256()
    for root, dirs, files in os.walk("src"):
        for file in sorted(files):
            if file.endswith(".py"):
                file_path = os.path.join(root, file)
                with open(file_path, "rb") as f:
                    while chunk := f.read(8192):
                        hash_sha256.update(chunk)
    return hash_sha256.hexdigest()

