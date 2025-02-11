import re
import time
import unicodedata
from pathlib import Path
from typing import Optional

import httpx
import orjson

CWD = Path(__file__).parent


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
    with open(file_path, "wb") as f:
        f.write(orjson.dumps(data, option=orjson.OPT_INDENT_2))


def read_servant_json_file_as_list(data) -> list[dict]:
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
    processed_data = []

    for servant in data:
        processed_servant = {
            "servant_id": servant["servant_id"],
            "name": servant["name"],
            "assets": servant["assets"],
        }

        processed_data.append(processed_servant)

    return processed_data


def download_image_and_save(name: str, id: int, url: str):
    file_name_from_url = url.split("/")[-1]

    # Sanitize the 'name' to ensure it's a valid Windows directory name
    invalid_chars_pattern = r'[<>:"/\\|?*\x00-\x1f]|\.$'
    sanitized_name = re.sub(invalid_chars_pattern, " ", name)

    image_dir_path = CWD / "input" / f"{id:03d}_{sanitized_name}"

    image_file_path = image_dir_path / file_name_from_url

    image_dir_path.mkdir(parents=True, exist_ok=True)

    print(f"Downloading image: {file_name_from_url}")

    retry = 3
    for i in range(retry):
        try:
            with httpx.stream("GET", url) as response:
                with open(image_file_path, "wb") as f:
                    for chunk in response.iter_bytes():
                        f.write(chunk)
        except Exception as e:
            print(f"Error downloading image {retry - i} retries left. {e}")
            time.sleep(1)
            continue

    # To prevent spamming the server
    time.sleep(0.5)

    file_name_text_path = image_dir_path / f"{id:03d}_{sanitized_name}.txt"
    file_name_text_path.touch(exist_ok=True)


def compare_and_update(old_data: list[dict], new_data: list[dict]):
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
                            )

                is_new_servant = False
                break

        if is_new_servant:
            print(f"New servant found: {new_servant['name']}")

            for key, value in new_servant_assets.items():
                download_image_and_save(
                    name=new_servant_name,
                    id=new_servant_id,
                    url=value,
                )

    write_json(CWD / "servant_data.json", new_data)


def read_the_old_data() -> list[dict]:
    file_path = CWD / "servant_data.json"
    if not file_path.exists():
        print("Old data not found.")
        return []

    try:
        data = read_json(file_path)
        return data
    except Exception as e:
        print(f"Error reading old data: {e}")
        return []


def download_from_atlas() -> Optional[Path]:
    url = "https://api.atlasacademy.io/export/JP/nice_servant_lang_en.json"

    atlas_file_path = CWD / "nice_servant_lang_en.json"

    if atlas_file_path.exists():
        return atlas_file_path

    retry = 3

    for i in range(retry):
        try:
            with httpx.stream("GET", url) as response:
                with open(atlas_file_path, "wb") as f:
                    for chunk in response.iter_bytes():
                        f.write(chunk)
            return atlas_file_path
        except Exception as e:
            print(f"Error downloading from Atlas {retry - i} retries left.\t{e}.")
            time.sleep(1)
            continue
    return None


def process_data():
    start_time = time.perf_counter()

    file_path = download_from_atlas()
    if not file_path:
        print("Exiting...")
        exit()
    data = read_json(file_path)
    new_data = read_servant_json_file_as_list(data)

    old_data = read_the_old_data()

    compare_and_update(old_data, new_data)

    end_time = time.perf_counter()

    print(f"Time taken: {end_time - start_time:.2f} seconds")
