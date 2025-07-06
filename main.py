import os
import configparser
import shutil

def get_valid_directory(prompt):
    while True:
        path = input(prompt).strip()
        if path.startswith('"') and path.endswith('"'):
            path = path[1:-1]
        if os.path.isdir(path):
            return path
        else:
            print("Invalid directory, try again.")

def find_rb3_folder():
    selected_dir = get_valid_directory("Enter path to Rock Band 3 folder: ")
    rb3_path = os.path.join(selected_dir, "rb3")
    if os.path.isdir(rb3_path):
        print("RB3 folder found.")
        return rb3_path
    else:
        print("RB3 folder not found, please install RB3Enhanced.")
        return None

def find_mod_type():
    mod_dir = get_valid_directory("Enter path to the mod folder: ")
    ini_path = os.path.join(mod_dir, "mod.ini")
    if not os.path.isfile(ini_path):
        print("mod.ini not found in that folder.")
        return None
    config = configparser.ConfigParser()
    config.optionxform = str
    try:
        config.read(ini_path, encoding="utf-8")
        if "Mod" not in config:
            print("No [Mod] section in mod.ini.")
            return None
        mod_type = config["Mod"].get("type", None)
        assets_dta = config["Mod"].get("assets_dta", None)
        item_name = config["Mod"].get("item_name", None)
        description = config["Mod"].get("description", None)
        print(f"Mod type found: {mod_type}")
        return {
            "type": mod_type,
            "assets_dta": assets_dta,
            "item_name": item_name,
            "description": description,
            "mod_dir": mod_dir
        }
    except configparser.Error as e:
        print(f"Error reading mod.ini: {e}")
        return None

def write_dta_files(mod_info, rb3_path):
    assets = mod_info.get("assets_dta")
    assets_path = os.path.join(rb3_path, "ui", "customize", "assets.dta")
    if assets:
        count = 0
        result = ""
        for char in assets:
            if char == "(":
                count += 1
                if count == 2:
                    result += "\n\t"
            result += char
        os.makedirs(os.path.dirname(assets_path), exist_ok=True)
        existing_assets = ""
        if os.path.isfile(assets_path):
            with open(assets_path, "r", encoding="utf-8") as f:
                existing_assets = f.read()
        if result not in existing_assets:
            with open(assets_path, "a", encoding="utf-8") as f:
                f.write("\n" + result)
            print(f"assets.dta appended to {assets_path}")
        else:
            print("Duplicate assets.dta entry skipped.")

    item_name = mod_info.get("item_name")
    description = mod_info.get("description")
    locale_path = os.path.join(rb3_path, "ui", "locale", "eng", "locale_updates_keep.dta")
    os.makedirs(os.path.dirname(locale_path), exist_ok=True)
    existing_locale = ""
    if os.path.isfile(locale_path):
        with open(locale_path, "r", encoding="utf-8") as f:
            existing_locale = f.read()

    lines_to_prepend = []
    for text in (item_name, description):
        if text:
            quote_index = text.find('"')
            if quote_index != -1:
                text = text[:quote_index] + "\n" + text[quote_index:]
            if text not in existing_locale:
                lines_to_prepend.append(text)
            else:
                print(f"Duplicate locale entry skipped: {text.strip()}")

    with open(locale_path, "w", encoding="utf-8") as f:
        f.write("\n".join(lines_to_prepend) + ("\n" if lines_to_prepend else "") + existing_locale)

    print(f"locale_updates_keep.dta updated at {locale_path}")

def copy_char_folder(mod_dir, rb3_path):
    src = os.path.join(mod_dir, "char")
    dst = os.path.join(rb3_path, "char")
    if os.path.isdir(src):
        shutil.copytree(src, dst, dirs_exist_ok=True)
        print(f"Copied 'char' folder from mod to {dst}")
    else:
        print("No 'char' folder found in the mod directory.")

if __name__ == "__main__":
    rb3_path = find_rb3_folder()
    if not rb3_path:
        exit(1)
    mod_info = find_mod_type()
    if mod_info and mod_info["type"]:
        print(f"Loaded mod of type: {mod_info['type']}")
        write_dta_files(mod_info, rb3_path)
        copy_char_folder(mod_info["mod_dir"], rb3_path)
