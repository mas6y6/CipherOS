import importlib, progressbar, requests, os, tarfile, shutil, zipfile
from wheel.wheelfile import WheelFile

class PackageManager():
    def __init__(self,api):
        self.resolved_dependencies = set()
        self.api = api
    
    def _is_compatible_whl(self, filename):
        """
        Check if a .whl file is compatible with the current system and Python version.
        """
        import sysconfig

        python_version = sysconfig.get_python_version()
        python_tag = f"cp{python_version.replace('.', '')}"
        platform_tag = sysconfig.get_platform().replace("-", "_").replace(".", "_")

        parts = filename.split("-")
        if len(parts) < 4 or not filename.endswith(".whl"):
            return False

        wheel_python_tag, wheel_platform_tag = parts[-3], parts[-1].replace(".whl", "")

        python_compatible = (
            python_tag in wheel_python_tag or
            "py3" in wheel_python_tag or
            "any" in wheel_python_tag
        )

        platform_compatible = (
            platform_tag in wheel_platform_tag or
            "any" in wheel_platform_tag
        )

        return python_compatible and platform_compatible



    def download_package(self, package_name, version=None):
        """
        Downloads the specified package from PyPI, resolving dependencies recursively.

        :param package_name: Name of the PyPI package.
        :param version: Optional version of the package to download.
        """
        base_url = "https://pypi.org/pypi"
        version_part = f"/{version}" if version else ""
        url = f"{base_url}/{package_name}{version_part}/json"
        download_dir = os.path.join(self.api.starterdir, "data", "cache", "packageswhl")
        packages_dir = os.path.join(self.api.starterdir, "data", "cache", "packages")

        try:
            response = requests.get(url)
            response.raise_for_status()
            data = response.json()

            dependencies = data.get("info", {}).get("requires_dist", [])
            if dependencies:
                self.api.console.print(f"Resolving dependencies for "+ package_name+ ": "+ f"{dependencies}",style="bold bright_yellow")
                for dep in dependencies:
                    dep_name, dep_version = self._parse_dependency(dep)
                    if dep_name and not self.is_package_installed(
                        dep_name, dep_version
                    ):
                        self.download_package(dep_name, dep_version)
            releases = data.get("releases", {})
            if version:
                files = releases.get(version, [])
            else:
                latest_version = data.get("info", {}).get("version")
                files = releases.get(latest_version, [])

            compatible_files = sorted(
                [
                    file_info["url"]
                    for file_info in files
                    if (
                        file_info["url"].endswith(".whl") and self._is_compatible_whl(file_info["filename"])
                    ) or file_info["url"].endswith(".tar.gz")
                ],
                key=lambda url: (
                    "win" in url,
                    "macosx" in url,
                    "manylinux" in url,
                    "any" in url
                ),
                reverse=True
            )

            if self.api.debug:
                self.api.console.print(f"Available files for {package_name}: {[file_info['filename'] for file_info in files]}")
            
            if self.api.debug:
                self.api.console.print(f"Available files for {package_name} that works on this system: {compatible_files}")
            if not compatible_files:
                self.api.console.print("No compatible .whl files. Falling back to .tar.gz.")
                tar_gz_files = [
                    file_info["url"]
                    for file_info in files
                    if file_info["url"].endswith(".tar.gz")
                ]
                if tar_gz_files:
                    download_url = tar_gz_files[0]
                else:
                    self.api.console.print("No valid files found.")
                    return
            
            download_url = compatible_files[0]
            filename = download_url.split("/")[-1]

            os.makedirs(download_dir, exist_ok=True)
            file_path = os.path.join(download_dir, filename)

            print(f"Downloading {package_name} from {download_url}...")
            with requests.get(download_url, stream=True) as r:
                r.raise_for_status()
                total_size = int(r.headers.get("Content-Length", 0))
                with open(file_path, "wb") as f:
                    bar = progressbar.ProgressBar(
                        maxval=total_size,
                        widgets=[
                            "Downloading: ",
                            progressbar.Percentage(),
                            " [",
                            progressbar.Bar(),
                            " ]",
                            progressbar.ETA(),
                        ],
                    )
                    bar.start()
                    downloaded = 0
                    for chunk in r.iter_content(chunk_size=8192):
                        f.write(chunk)
                        downloaded += len(chunk)
                        bar.update(downloaded)
                    bar.finish()

            if filename.endswith(".zip"):
                os.makedirs(packages_dir, exist_ok=True)
                with zipfile.ZipFile(file_path, "r") as zip_ref:
                    zip_ref.extractall(packages_dir)

            elif filename.endswith(".whl"):
                with WheelFile(file_path, "r") as whl_ref:
                    whl_ref.extractall(packages_dir)
            
            elif filename.endswith(".tar.gz"):
                try:
                    temp_dir = os.path.join(download_dir, "temp_extract")
                    os.makedirs(temp_dir, exist_ok=True)

                    with tarfile.open(file_path, "r:gz") as tar_ref:
                        tar_ref.extractall(temp_dir)

                    setup_py = os.path.join(temp_dir, 'setup.py')
                    package_dir = None

                    if os.path.exists(setup_py):
                        print(f"Found setup.py in {setup_py}. Attempting to find the main package...")
                        from setuptools import find_packages
                        found_packages = find_packages(where=temp_dir)
                        if found_packages:
                            package_dir = os.path.join(temp_dir, found_packages[0])

                    if not package_dir:
                        extracted_folders = [f for f in os.listdir(temp_dir) if os.path.isdir(os.path.join(temp_dir, f))]
                        if extracted_folders:
                            package_dir = os.path.join(temp_dir, extracted_folders[0])

                    if package_dir:
                        print(f"Found main package directory: {package_dir}")
                        for item in os.listdir(package_dir):
                            s = os.path.join(package_dir, item)
                            d = os.path.join(packages_dir, item)
                            if os.path.isdir(s):
                                shutil.copytree(s, d, dirs_exist_ok=True)
                            else:
                                shutil.copy2(s, d)

                        print(f"Package {package_name} extracted and moved to {packages_dir}")
                except (tarfile.TarError, IOError) as e:
                    RuntimeError(f"Error extracting {filename}: {e}")
                finally:
                    if os.path.exists(temp_dir):
                        shutil.rmtree(temp_dir)

            else:
                raise TypeError("File format is invalid to the extractor")
        except requests.RequestException as e:
            self.api.console.print(f"Failed to download package '{package_name}':\n {e}",style="bold bright_red")
        
        except Exception as e:
            self.api.console.print(f"An error occurred while extracting/downloading '{package_name}':\n {e}",style="bold bright_red")

    def _parse_dependency(self, dependency_string):
        """
        Parse a dependency string from requires_dist into name and version.

        :param dependency_string: A dependency string from requires_dist.
        :return: A tuple of (name, version) or (name, None).
        """
        import re

        match = re.match(r"([a-zA-Z0-9_\-\.]+)(?:\[.*\])?(?:\s*\(([^)]+)\))?", dependency_string)
        if match:
            dep_name = match.group(1).strip()
            dep_version = match.group(2)
            return dep_name, dep_version.strip() if dep_version else None

        return dependency_string, None

    def is_package_installed(self, package_name, version=None):
        """
        Checks if a package is already downloaded and installed.

        :param package_name: Name of the package.
        :param version: Optional version of the package.
        :return: True if installed, False otherwise.
        """
        try:
            importlib.import_module(package_name)
            return True
        except ImportError:
            installed_dir = os.path.join(self.starterdir, "data", "cache", "packages")
            if version:
                package_path = os.path.join(installed_dir, f"{package_name}-{version}")
            else:
                package_path = os.path.join(installed_dir, package_name)
            return os.path.exists(package_path)