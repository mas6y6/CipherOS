import tarfile
import os

def create_tar_gz(source_dir, output_filename):
    with tarfile.open(output_filename, "w:gz") as tar:
        tar.add(source_dir, arcname=os.path.basename(source_dir))

source_directory = "example_plugin"
output_file = "example_plugin.tar.gz"
create_tar_gz(source_directory, output_file)
