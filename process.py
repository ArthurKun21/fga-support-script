import re
import time
import unicodedata
from pathlib import Path
from typing import Optional

import httpx
import orjson

CWD = Path(__file__).parent

# Sanitize the 'name' to ensure it's a valid Windows directory name
INVALID_CHARS_PATTERN = r'[<>:"/\\|?*\x00-\x1f]|\.$'


def preprocess_name(input_str) -> str:
    """Removes accents from a string using unicode normalization.

    Args:
        input_str: The string to process.

    Returns:
        The string with accents removed.
    """
    nfkd_form = unicodedata.normalize("NFKD", input_str)
    only_ascii = "".join([c for c in nfkd_form if not unicodedata.combining(c)])
    return only_ascii


def read_json(file_path: Path):
    with open(file_path, "r", encoding="utf-8") as f:
        data = orjson.loads(f.read())

    return data


def write_json(file_path: Path, data):
    try:
        with open(file_path, "wb") as f:
            f.write(orjson.dumps(data, option=orjson.OPT_INDENT_2))
    except FileNotFoundError as e:
        print(f"Error writing JSON file: {e}")
    except Exception as e:
        print(f"Error writing JSON file: {e}")


def read_servant_json_file_as_list(data) -> list[dict]:
    """Process and transform servant JSON data into a standardized list format.
    This function takes raw servant data, sorts it by collection number, and processes
    each servant entry to create a standardized format with specific naming conventions
    and asset organization.
    Args:
        data (list[dict]): Raw servant data as a list of dictionaries.
    Returns:
        list[dict]: A list of processed servant dictionaries containing:
            - servant_id (int): Collection number of the servant
            - name (str): Processed name of the servant
            - className (str): Capitalized class name
            - rarity (int): Servant rarity
            - assets (dict): Dictionary of servant face assets
    Notes:
        - Filters out non-playable servant types
        - Handles special cases for certain servants (BB, Hakuno, Ereshkigal)
        - Standardizes class names (Moon Cancer, Alter Ego)
        - Adds class name to servant name if duplicate exists
        - Writes processed data to 'incoming.json'
    """
    sorted_data = sorted(data, key=lambda x: x["collectionNo"])

    append_list = []

    # To prevent duplicate names
    name_cache = []

    playable_type = ["heroine", "normal"]

    json_dict: dict
    for json_dict in sorted_data:
        # print(json_dict)
        new_json_dict = {}

        # Skip if not a playable servant
        servant_type = json_dict.get("type", None)
        if servant_type not in playable_type:
            continue

        collectionNo = json_dict.get("collectionNo", 0)
        if collectionNo == 0:
            continue

        name = json_dict.get("name", "")

        name = preprocess_name(name)

        if "Altria" in name:
            name = name.replace("Altria", "Artoria")

        gender = json_dict.get("gender", "")

        class_name = json_dict.get("className", "")
        rarity = json_dict.get("rarity", 1)

        # Conditionals for special cases

        if name == "BB" and rarity == 5:
            name = "BB (Summer)"

        if name == "Kishinami Hakuno" and gender == "female":
            name = "Kishinami Hakunon"

        if name == "Ereshkigal" and class_name == "beastEresh":
            name = "Ereshkigal (Summer)"
            class_name = "Beast"

        if class_name.lower() == "mooncancer":
            class_name = "Moon Cancer"

        if class_name.lower() == "alterego":
            class_name = "Alter Ego"

        class_name = " ".join([word.capitalize() for word in class_name.split()])

        if name in name_cache:
            name = f"{name} ({class_name})"
        name_cache.append(name)

        assets = {}

        extraAssets = json_dict.get("extraAssets", {})

        faces = extraAssets.get("faces", {})
        for face_keys, face_values in faces.items():
            for key, value in face_values.items():
                assets.update({f"{face_keys}_{key}": value})

        new_json_dict.update(
            {
                "servant_id": collectionNo,
                "name": name,
                "className": class_name,
                "rarity": rarity,
                "assets": assets,
            }
        )

        append_list.append(new_json_dict)

    write_json(CWD / "incoming.json", append_list)

    return append_list


def process_data_for_comparison(data: list[dict]) -> list[dict]:
    """
    Processes a list of servant dictionaries to extract specific fields for comparison.
    Args:
        data (list[dict]): List of dictionaries containing servant data with at least
                           'servant_id', 'name', and 'assets' fields.
    Returns:
        list[dict]: List of processed servant dictionaries containing only the
                    'servant_id', 'name', and 'assets' fields.
    Example:
        >>> servants = [{'servant_id': 1, 'name': 'Saber', 'assets': {...}, 'other': 'data'}]
        >>> process_data_for_comparison(servants)
        [{'servant_id': 1, 'name': 'Saber', 'assets': {...}}]
    """
    processed_data = []

    for servant in data:
        processed_servant = {
            "servant_id": servant["servant_id"],
            "name": servant["name"],
            "assets": servant["assets"],
        }

        processed_data.append(processed_servant)

    return processed_data


def download_image_and_save(name: str, id: int, url: str, dir_type: str):
    """Downloads an image from a URL and saves it to a local directory.
    This function downloads an image from a specified URL, creates a directory with the given name
    and ID, saves the image in that directory, and creates an accompanying text file. It includes
    retry logic for failed downloads and implements rate limiting to prevent server overload.
    Args:
        name (str): The name to be used for the directory (will be sanitized for Windows compatibility)
        id (int): Numerical identifier used in directory and file naming
        url (str): URL of the image to download
        dir_type (str): Type of directory to organize the downloaded content
    Raises:
        Exception: If download fails after all retry attempts
    Note:
        - Creates directory structure: CWD/input/dir_type/id_name/
        - Sanitizes directory names for Windows compatibility
        - Implements 3 retry attempts with 1 second delay between retries
        - Includes 0.5 second delay after successful download for rate limiting
        - Creates an empty text file alongside the downloaded image
    """
    file_name_from_url = url.split("/")[-1]

    sanitized_name = re.sub(INVALID_CHARS_PATTERN, " ", name)
    sanitized_name = sanitized_name.strip()

    if dir_type.lower() == "servant":
        final_name = f"{id:03d}_{sanitized_name}"
    else:
        final_name = f"{id:04d}_{sanitized_name}"

    image_dir_path = CWD / "input" / dir_type / final_name
    image_dir_path.mkdir(parents=True, exist_ok=True)

    image_file_path = image_dir_path / file_name_from_url

    file_name_text_path = image_dir_path / f"{final_name}.txt"
    file_name_text_path.touch(exist_ok=True)

    print(f"Downloading image: {id} {file_name_from_url}")

    retry = 3
    for i in range(retry):
        try:
            with httpx.stream("GET", url) as response:
                with open(image_file_path, "wb") as f:
                    for chunk in response.iter_bytes():
                        f.write(chunk)
            break
        except Exception as e:
            print(f"Error downloading image {retry - i} retries left. {e}")
            time.sleep(1)
            continue

    # To prevent spamming the server
    time.sleep(0.5)


def compare_and_update_servant(old_data: list[dict], new_data: list[dict]):
    """
    Compare old and new servant data to detect and process updates and additions.
    This function compares two lists of servant dictionaries to identify new servants
    and servants with new assets. For any changes found, it downloads and saves the
    new image assets.
    Args:
        old_data (list[dict]): List of dictionaries containing previous servant data
        new_data (list[dict]): List of dictionaries containing current servant data
    Each servant dictionary is expected to have the following structure:
        {
            "servant_id": int,
            "name": str,
            "assets": {
                "asset_key": "url_string"
            }
        }
    Side Effects:
        - Downloads and saves new servant images to filesystem
        - Updates servant_data.json with new data
        - Prints status messages to console for new servants and asset updates
    Note:
        This function relies on external functions:
        - process_data_for_comparison()
        - download_image_and_save()
        - write_json()
    """
    old_data_processed = process_data_for_comparison(old_data)
    new_data_processed = process_data_for_comparison(new_data)

    for new_servant in new_data_processed:
        is_new_servant = True

        new_servant_id = new_servant.get("servant_id", 0)
        new_servant_name = new_servant.get("name", "")
        new_servant_assets = new_servant.get("assets", {})

        for old_servant in old_data_processed:
            old_servant_id = old_servant.get("servant_id", 0)
            old_servant_assets = old_servant.get("assets", {})

            if new_servant_id == old_servant_id:
                if len(new_servant_assets) != len(old_servant_assets):
                    print(f"Servant {new_servant['name']} has new assets. Updating...")

                    # Find the new assets
                    for key, value in new_servant_assets.items():
                        if key not in old_servant_assets:
                            download_image_and_save(
                                name=new_servant_name,
                                id=new_servant_id,
                                url=value,
                                dir_type="servant",
                            )

                is_new_servant = False

                old_data_processed.remove(old_servant)

                break

        if is_new_servant:
            print(f"New servant found: {new_servant['name']}")

            for key, value in new_servant_assets.items():
                download_image_and_save(
                    name=new_servant_name,
                    id=new_servant_id,
                    url=value,
                    dir_type="servant",
                )

    write_json(CWD / "servant_data.json", new_data)


def read_the_old_data(file_path: Path) -> list[dict]:
    if not file_path.exists():
        print("Old data not found.")
        return []

    try:
        data = read_json(file_path)
        return data
    except Exception as e:
        print(f"Error reading old data: {e}")
        return []


def download_data_from_atlas(
    url: str,
    file_path: Path,
) -> Optional[Path]:
    if file_path.exists() and file_path.stat().st_size > 0:
        return file_path

    retry = 3

    for i in range(retry):
        try:
            with httpx.stream("GET", url) as response:
                with open(file_path, "wb") as f:
                    for chunk in response.iter_bytes():
                        f.write(chunk)
            return file_path
        except Exception as e:
            print(f"Error downloading from Atlas {retry - i} retries left.\t{e}.")
            time.sleep(1)
            continue
    return None


def process_servant_data():
    start_time = time.perf_counter()

    servant_file_path = download_data_from_atlas(
        url="https://api.atlasacademy.io/export/JP/nice_servant_lang_en.json",
        file_path=CWD / "nice_servant_lang_en.json",
    )
    if not servant_file_path:
        print("Exiting...")
        exit()
    new_servant_json = read_json(servant_file_path)
    new_servant_data = read_servant_json_file_as_list(new_servant_json)

    old_servant_data = read_the_old_data(file_path=CWD / "servant_data.json")

    compare_and_update_servant(old_servant_data, new_servant_data)

    end_time = time.perf_counter()

    print(f"Time takenfor Servant: {end_time - start_time:.2f} seconds")


def read_ce_json_file_as_list(data) -> list[dict]:
    """Process and transform CE (Craft Essence) JSON data into a standardized list format.
    This function takes raw CE data, sorts it by collection number, and processes each entry
    to create a simplified data structure with essential CE information.
    Args:
        data (list[dict]): Raw CE JSON data containing craft essence information.
                           Each dict should have 'collectionNo', 'name', 'face', and 'rarity' fields.
    Returns:
        list[dict]: List of processed CE dictionaries with the following structure:
                    - ce_id (int): Collection number/ID of the craft essence
                    - name (str): Processed name of the craft essence
                    - face (str): Face/image reference of the craft essence
                    - rarity (int): Rarity level of the craft essence
    Side Effects:
        - Writes the processed data to 'incoming_ce.json' in the current working directory
    Notes:
        - Entries with collectionNo = 0 are skipped
        - Names are preprocessed using the preprocess_name function
    """
    sorted_data = sorted(data, key=lambda x: x["collectionNo"])

    append_list = []

    json_dict: dict
    for json_dict in sorted_data:
        collectionNo = json_dict.get("collectionNo", 0)
        if collectionNo == 0:
            continue

        name = json_dict.get("name", "")

        name = preprocess_name(name)

        face = json_dict.get("face", "")

        rarity = json_dict.get("rarity", 1)

        new_data = {
            "ce_id": collectionNo,
            "name": name,
            "face": face,
            "rarity": rarity,
        }
        append_list.append(new_data)

    write_json(CWD / "incoming_ce.json", append_list)

    return append_list


def compare_and_update_ce(old_data: list[dict], new_data: list[dict]):
    """
    Compare old and new craft essence data and update the database with any new entries.
    This function compares two lists of craft essence dictionaries, identifies new entries,
    downloads associated images for new craft essences, and updates the database file.
    Args:
        old_data (list[dict]): List of dictionaries containing existing craft essence data
        new_data (list[dict]): List of dictionaries containing new craft essence data to compare against
    Each dictionary in the lists should contain:
        - ce_id (int): Unique identifier for the craft essence
        - name (str): Name of the craft essence
        - face (str): URL to the craft essence image
    The function will:
    1. Check for new craft essences by comparing IDs
    2. Download images for new craft essences
    3. Update the ce_data.json file with the new data
    Note:
        Requires the download_image_and_save function and write_json function to be defined
        Assumes CWD (current working directory) is defined as a Path object
    """
    old_data_copy = old_data.copy()
    new_data_copy = new_data.copy()

    for new_ce in new_data_copy:
        is_new_ce = True

        ce_id = new_ce.get("ce_id", 0)
        name = new_ce.get("name", "")

        face = new_ce.get("face", "")

        for old_ce in old_data_copy:
            if new_ce["ce_id"] == old_ce["ce_id"]:
                is_new_ce = False
                old_data_copy.remove(old_ce)
                break
        if is_new_ce and len(face) > 0:
            print(f"New craft essence found: {new_ce['name']}")

            download_image_and_save(
                name=name,
                id=ce_id,
                url=face,
                dir_type="craft_essence",
            )

    write_json(CWD / "ce_data.json", new_data)


def process_craft_essence_data():
    start_time = time.perf_counter()

    ce_file_path = download_data_from_atlas(
        url="https://api.atlasacademy.io/export/JP/basic_equip_lang_en.json",
        file_path=CWD / "basic_equip_lang_en.json",
    )
    if not ce_file_path:
        print("Exiting...")
        exit()
    new_ce_json = read_json(ce_file_path)
    new_ce_data = read_ce_json_file_as_list(new_ce_json)

    old_ce_data = read_the_old_data(file_path=CWD / "ce_data.json")

    compare_and_update_ce(old_ce_data, new_ce_data)

    end_time = time.perf_counter()

    print(f"Time taken for CE: {end_time - start_time:.2f} seconds")
