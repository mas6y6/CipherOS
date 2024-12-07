import importlib
import os
import progressbar
import requests
import shutil
import tarfile
import zipfile
from wheel.wheelfile import WheelFile
import rich.console

class PackageManager():
    def __init__(self, api):
        self.resolved_dependencies = set()
        self.api = api

    def _is_compatible_whl(self, filename):
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
        base_url = "https://pypi.org/pypi"
        version_part = f"/{version}" if version else ""
        url = f"{base_url}/{package_name}{version_part}/json"
        download_dir = os.path.join(self.api.starterdir, "data", "cache", "packageswhl")
        packages_dir = os.path.join(self.api.starterdir, "data", "cache", "packages")

        identifier = f"{package_name}=={version}" if version else package_name

        if identifier in self.resolved_dependencies:
            if self.api.debug:
                self.api.console.print(f"[DEBUG] Package already resolved: {identifier}", style="dim")
            return

        self.resolved_dependencies.add(identifier)

        try:
            response = requests.get(url)
            response.raise_for_status()
            data = response.json()

            dependencies = data.get("info", {}).get("requires_dist", [])
            if dependencies:
                self.api.console.print(f"Resolving dependencies for {package_name}: {dependencies}", style="bold bright_yellow")
                for dep in dependencies:
                    dep_name, dep_version = self._parse_dependency(dep)
                    if dep_name and not self.is_package_installed(dep_name, dep_version):
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
                self.api.console.print(f"[DEBUG] Compatible files for {package_name}: {compatible_files}")

            if not compatible_files:
                self.api.console.print(f"[ERROR] No compatible files found for {package_name}", style="bold red")
                return

            download_url = compatible_files[0]
            filename = download_url.split("/")[-1]

            os.makedirs(download_dir, exist_ok=True)
            file_path = os.path.join(download_dir, filename)

            self._download_file(download_url, file_path)
            self._extract_package(file_path, packages_dir, filename)

        except requests.RequestException as e:
            self.api.console.print(f"[ERROR] Failed to fetch package metadata for {package_name}: {e}", style="bold red")
        except Exception as e:
            self.api.console.print(f"[ERROR] An unexpected error occurred: {e}", style="bold red")

    def _download_file(self, url, path):
        with requests.get(url, stream=True) as r:
            r.raise_for_status()
            total_size = int(r.headers.get("Content-Length", 0))
            with open(path, "wb") as f:
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

    def _extract_package(self, file_path, target_dir, filename):
        os.makedirs(target_dir, exist_ok=True)
        if filename.endswith(".zip"):
            with zipfile.ZipFile(file_path, "r") as zip_ref:
                zip_ref.extractall(target_dir)
        elif filename.endswith(".whl"):
            with WheelFile(file_path, "r") as whl_ref:
                whl_ref.extractall(target_dir)
        elif filename.endswith(".tar.gz"):
            with tarfile.open(file_path, "r:gz") as tar_ref:
                tar_ref.extractall(target_dir)
        else:
            raise TypeError("Unsupported file format")

    def _parse_dependency(self, dependency_string):
        import re
        match = re.match(r"([a-zA-Z0-9_\-.]+)(?:\[.*\])?(?:\s+\((.+)\))?", dependency_string)
        if match:
            dep_name = match.group(1).strip()
            dep_version = match.group(2)
            return dep_name, dep_version
        return dependency_string, None

    def is_package_installed(self, package_name, version=None):
        try:
            importlib.import_module(package_name)
            return True
        except ImportError:
            installed_dir = os.path.join(self.api.starterdir, "data", "cache", "packages")
            package_path = os.path.join(installed_dir, package_name)
            return os.path.exists(package_path)
