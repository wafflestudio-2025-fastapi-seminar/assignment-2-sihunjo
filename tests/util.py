import os
import hashlib

def get_all_src_py_files_hash():
    hash_sha256 = hashlib.sha256()

    script_dir = os.path.dirname(os.path.abspath(__file__))
    project_root = os.path.dirname(script_dir)
    src_dir = os.path.join(project_root, "src")

    py_files = []
    for root, dirs, files in os.walk(src_dir):
        for file in files:
            if file.endswith(".py"):
                file_path = os.path.join(root, file)
                rel_path = os.path.relpath(file_path, src_dir)
                py_files.append((rel_path, file_path))

    py_files.sort(key=lambda x: x[0])

    for rel_path, file_path in py_files:
        print(rel_path)
        with open(file_path, "rb") as f:
            while chunk := f.read(8192):
                hash_sha256.update(chunk)

    return hash_sha256.hexdigest()
