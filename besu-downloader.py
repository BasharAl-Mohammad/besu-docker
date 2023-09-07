import requests
import re
import zipfile
import tarfile
import os
import shutil

def get_tag_release(repo_owner, repo_name, tag_name):
    url = f"https://api.github.com/repos/{repo_owner}/{repo_name}/releases/tags/{tag_name}"
    response = requests.get(url)

    if response.status_code == 200:
        release_data = response.json()
        return release_data["body"]
    else:
        raise Exception(f"Failed to fetch release for tag {tag_name}. Status code: {response.status_code}")

def extract_download_links(body):
    download_links = re.findall(r"(https?://\S+\.(?:tar\.gz|zip))", body)
    return download_links

def download_release_archive(archive_url, save_path):
    response = requests.get(archive_url)
    
    if response.status_code == 200:
        with open(save_path, "wb") as f:
            f.write(response.content)
    else:
        raise Exception(f"Failed to download release archive. Status code: {response.status_code}")

def extract_archive(archive_path, extract_path):
    if archive_path.endswith(".zip"):
        with zipfile.ZipFile(archive_path, "r") as zip_ref:
            zip_ref.extractall(extract_path)
    elif archive_path.endswith(".tar.gz"):
        with tarfile.open(archive_path, "r:gz") as tar_ref:
            tar_ref.extractall(extract_path)
    elif archive_path.endswith(".tar"):
        with tarfile.open(archive_path, "r") as tar_ref:
            tar_ref.extractall(extract_path)
    else:
        raise Exception("Unsupported archive format. Only ZIP and TAR archives are supported.")

def move_contents_to_parent_directory(source_dir, dest_dir):
    for item in os.listdir(source_dir):
        source_item = os.path.join(source_dir, item)
        dest_item = os.path.join(dest_dir, item)
        shutil.move(source_item, dest_item)

if __name__ == "__main__":
    repo_owner = "hyperledger"
    repo_name = "besu"

    try:
        tag_name = input("Enter the tag name you want to download: ")
        body = get_tag_release(repo_owner, repo_name, tag_name)

        print(f"Release for tag {tag_name}:")
        download_links = extract_download_links(body)
        print("Available download links:")
        for i, link in enumerate(download_links, start=1):
            print(f"{i}. {link}")

        choice = int(input("Enter the number of the link you want to download: ")) - 1
        if 0 <= choice < len(download_links):
            download_url = download_links[choice]
        else:
            raise Exception("Invalid choice.")

        extension = "tar.gz" if download_url.endswith(".tar.gz") else "zip"
        save_path = f"{repo_name}_{tag_name}.{extension}"
        download_release_archive(download_url, save_path)
        print(f"Downloaded release archive to: {save_path}")

        extract_dir = "besu"
        os.makedirs(extract_dir, exist_ok=True)
        extract_archive(save_path, extract_dir)
        move_contents_to_parent_directory(os.path.join(extract_dir, f"{repo_name}-{tag_name}"), extract_dir)
        shutil.rmtree(os.path.join(extract_dir, f"{repo_name}-{tag_name}"))
        print(f"Extracted archive to: {extract_dir}")

        os.remove(save_path)
        print(f"Removed downloaded archive: {save_path}")

    except Exception as e:
        print(f"Error: {str(e)}")
