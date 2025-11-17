import os
import sys
import shutil
import configparser
import re
import datetime
import os.path
import subprocess 

# --- CONSTANTS ---
# VŠETKY SYSTÉMOVÉ SÚBORY BUDÚ ODKAZOVAŤ NA KOREŇOVÝ ADRESÁR SKRIPTU
TOOL_ROOT_DIR = os.path.dirname(os.path.abspath(__file__)) 

INI_FILE = 'theBatchDosBoxer.ini'
PROFILES_CACHE_FILE = 'profiles_cache.ini'
LOG_FILE = 'batch_operations_log.txt' 

KEY_FILES = ['!start.bat', 'dosbox.conf']
KEY_FOLDERS = ['cd', 'docs', 'drives']
BAK_FILE_EXT = '.bak'
MOUNT_C_REGEX = re.compile(r'mount C\s+"(.*?)"', re.IGNORECASE)
VERSION = 'v1.0'
PROGRAM_NAME = 'The Batch (DOS)Box(er)'

# --- CONFIGURATION MANAGEMENT (INI) ---

def load_settings():
    """Loads settings or sets default values."""
    config = configparser.ConfigParser()
    ini_path = os.path.join(TOOL_ROOT_DIR, INI_FILE) # POUŽITIE KOREŇOVEJ CESTY
    config.read(ini_path)

    if 'GLOBAL' not in config:
        config['GLOBAL'] = {}

    # Path settings 
    config['GLOBAL']['path_to_dosbox_exe'] = config['GLOBAL'].get('path_to_dosbox_exe', 'D:\\emulators\\dosbox\\dosbox.exe')
    config['GLOBAL']['path_to_DBGL_root'] = config['GLOBAL'].get('path_to_DBGL_root', 'D:\\')
    config['GLOBAL']['path_to_temp_dir'] = config['GLOBAL'].get('path_to_temp_dir', 'D:\\Temp\\')
    config['GLOBAL']['path_to_zip_dest_dir'] = config['GLOBAL'].get('path_to_zip_dest_dir', 'D:\\ZippedGames\\')

    # Switch settings 
    config['GLOBAL']['preserve_mount_c'] = config['GLOBAL'].get('preserve_mount_c', 'ENABLED')
    config['GLOBAL']['automatic_mode_detection'] = config['GLOBAL'].get('automatic_mode_detection', 'ENABLED') 
    
    # ZIP settings
    config['GLOBAL']['zip_dosbox_structure'] = config['GLOBAL'].get('zip_dosbox_structure', 'SUBDIR') 
    
    try:
        with open(ini_path, 'w') as configfile:
            config.write(configfile)
    except Exception as e:
         print(f"| ❌ CRITICAL ERROR: Cannot write to {INI_FILE}: {e}")

    return config['GLOBAL']

def save_setting(key, value):
    """Writes a specific value to the INI file."""
    config = configparser.ConfigParser()
    ini_path = os.path.join(TOOL_ROOT_DIR, INI_FILE) # POUŽITIE KOREŇOVEJ CESTY
    config.read(ini_path)
    
    if 'GLOBAL' not in config:
        config['GLOBAL'] = {}
        
    config['GLOBAL'][key] = value

    try:
        with open(ini_path, 'w') as configfile:
            config.write(configfile)
        print(f"| ✅ Setting '{key}' updated to: {value}")
    except Exception as e:
        print(f"| ❌ ERROR WRITING SETTING: {e}")


# --- MODE DETECTION AND HELPER FUNCTIONS ---

def detect_working_mode(path='.'):
    """
    Analyzes the current folder and determines the working mode: 'SINGLE', 'BATCH', 'UNCERTAIN'.
    """
    content = os.listdir(path)
    
    # Check for single game folder elements
    is_game_folder = any(
        (os.path.isdir(item) and item.lower() in KEY_FOLDERS) or 
        (os.path.isfile(item) and item.lower() in KEY_FILES)
        for item in content
    )
    if is_game_folder:
        return 'SINGLE'
    
    # Check for multiple subfolders (potential batch root)
    num_game_subdirs = sum(
        1 for item in content 
        if os.path.isdir(item) and item.lower() not in KEY_FOLDERS and not item.startswith('.')
    )
    
    if num_game_subdirs >= 2:
        return 'BATCH'
        
    return 'UNCERTAIN'

def check_existence(path, item_type='dir'):
    """Checks path existence and returns a status symbol."""
    if not path:
        return "[⚠️ Not Set]"
    
    exists = os.path.exists(path)
    
    if not exists:
        return "[❌ Not Found]"
    
    if item_type == 'file':
        return "[✅ File OK]" if os.path.isfile(path) else "[⚠️ Not a file]"
    elif item_type == 'dir':
        return "[✅ Folder OK]" if os.path.isdir(path) else "[⚠️ Not a folder]"
    return "[✅ OK]"


def validate_and_save_path(key, new_path, item_type='dir'):
    """Validates existence, creates if necessary (for dirs), and saves the path."""
    if not new_path:
        print("| ⚠️ Path cannot be empty. Setting not saved.")
        return

    exists = os.path.exists(new_path)

    if exists:
        if item_type == 'file' and not os.path.isfile(new_path):
            print(f"| ❌ ERROR: Path '{new_path}' exists, but is not a file.")
            return
        elif item_type == 'dir' and not os.path.isdir(new_path):
            print(f"| ❌ ERROR: Path '{new_path}' exists, but is not a folder.")
            return
        
        save_setting(key, new_path)
        print(f"| ✅ Path verified and saved.")
    else:
        # Allow creation for directories (e.g., temp folder)
        if item_type == 'dir':
            try:
                os.makedirs(new_path, exist_ok=True)
                save_setting(key, new_path)
                print(f"| ⚠️ Folder did not exist, created and saved.")
            except Exception as e:
                print(f"| ❌ ERROR: Folder does not exist and could not be created: {e}")
        else:
            print(f"| ❌ ERROR: File or folder not found at: {new_path}")
            print("| Setting not saved.")

def run_start_bat(path='.'):
    """Tries to execute the !start.bat file in the current directory, ensuring it runs non-blocking."""
    bat_path = os.path.join(path, '!start.bat')
    print(f"\n| 🚀 Attempting to run: {bat_path}")

    if not os.path.exists(bat_path):
        raise FileNotFoundError(f"File '!start.bat' not found in: {os.path.abspath(path)}")

    try:
        if os.name == 'nt':
            # Pre Windows použijeme príkaz 'start' na vynútenie neblokujúceho spustenia v novom okne.
            # Shell=True je nutné pre spracovanie príkazu 'start'.
            # Prázdne "" za 'start' je titulok nového okna (zabráni použitiu cesty ako titulku).
            subprocess.Popen(f'start "" "{bat_path}"', cwd=path, shell=True)
            print("| ✅ !start.bat launched successfully (non-blocking, new window).")
        else:
            # Pre Linux/macOS necháme pôvodné neblokujúce spustenie
            subprocess.Popen([bat_path], cwd=path, shell=True)
            print("| ✅ !start.bat launched successfully (non-blocking).")
            
    except Exception as e:
        raise Exception(f"Error launching !start.bat: {e}")


# --- GAME OPERATIONS (SINGLE & BATCH) ---

def create_base_folders(settings, path='.'):
    """Creates the basic folder structure for the game."""
    print(f"\n| 🛠️ Creating base folders")
    try:
        os.makedirs(os.path.join(path, 'cd'), exist_ok=True)
        os.makedirs(os.path.join(path, 'docs'), exist_ok=True)
        os.makedirs(os.path.join(path, 'drives', 'c'), exist_ok=True)
        print("| ✅ Folder structure created: cd, docs, drives/c")
    except Exception as e:
        raise Exception(f"Error creating folders: {e}")

def create_start_bat(settings, path='.'):
    """
    Creates or updates !start.bat. 
    Dynamically calculates the RELATIVE path from the current game directory to the central DOSBox.exe.
    This BAT is for LOCAL execution in a portable (USB) environment.
    """
    print(f"\n| 🛠️ Creating/Updating !start.bat (Dynamic relative path)")
    
    dosbox_exe_abs_path = settings.get('path_to_dosbox_exe')
    
    if not os.path.exists(dosbox_exe_abs_path):
        raise Exception("Absolute path to DOSBox.exe in settings is invalid. It must exist for dynamic path calculation.")

    # Calculate relative path from the current folder (path) to the target file (dosbox_exe_abs_path)
    try:
        # Používame os.path.abspath(path) aby sme získali správny referenčný bod (adresár hry)
        target_path_for_bat = os.path.relpath(dosbox_exe_abs_path, os.path.abspath(path))
    except ValueError as e:
        raise Exception(f"Error calculating relative path (are they on different drives?): {e}")

    # Normalize path for Windows BAT compatibility
    target_path_for_bat = target_path_for_bat.replace('/', '\\')

    print(f"| ⚠️ Used RELATIVE path: {target_path_for_bat}")

    bat_content = f"""
@echo off
rem Launch DOSBox with the configuration for the current directory
rem Relative path dynamically calculated for a portable centralized DOSBox installation on USB.
"{target_path_for_bat}" -conf dosbox.conf
    """
    
    try:
        file_path = os.path.join(path, '!start.bat')
        with open(file_path, 'w') as f:
            f.write(bat_content.strip())
        print(f"| ✅ File !start.bat created/updated. Calls: {target_path_for_bat}")
    except Exception as e:
        raise Exception(f"Error creating !start.bat: {e}")


def find_profile_by_mount_c(settings, game_folder_name):
    """
    Searches for the correct DBGL profile in profiles/ based on the MOUNT C command content.
    Uses cache for faster repeated operations.
    """
    dbgl_profiles_dir = os.path.join(settings.get('path_to_DBGL_root'), 'profiles')
    
    # --- 1. STEP: Search in CACHE ---
    cache_path = os.path.join(TOOL_ROOT_DIR, PROFILES_CACHE_FILE) # POUŽITIE KOREŇOVEJ CESTY
    cache = configparser.ConfigParser()
    cache.read(cache_path)
    
    if 'PROFILES_MAP' in cache:
        for profile_file, mapped_game_dir in cache['PROFILES_MAP'].items():
            if game_folder_name.lower() == mapped_game_dir.lower():
                profile_path = os.path.join(dbgl_profiles_dir, profile_file)
                if os.path.exists(profile_path):
                    print(f"| ✅ Profile found in CACHE: {profile_file}")
                    return profile_path
                else:
                    del cache['PROFILES_MAP'][profile_file]
                    print(f"| ⚠️ Record '{profile_file}' removed from cache.")
        
        try:
            with open(cache_path, 'w') as cachefile: # Uloženie upravenej cache na KOREŇOVEJ CESTE
                cache.write(cachefile)
        except Exception:
            pass # Ignorujeme chyby zápisu cache
            
    # --- 2. STEP: ITERATE AND SEARCH CONTENT ---
    
    if not os.path.isdir(dbgl_profiles_dir):
          print(f"| ❌ DBGL profiles directory not found: {dbgl_profiles_dir}")
          return None
          
    print(f"| 🔍 Searching for profile in {os.path.basename(dbgl_profiles_dir)} by content (slow)...")
    
    for filename in os.listdir(dbgl_profiles_dir):
        if filename.endswith('.conf'):
            profile_path = os.path.join(dbgl_profiles_dir, filename)
            
            try:
                with open(profile_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                
                autoexec_match = re.search(r'\[autoexec\](.*)', content, re.DOTALL | re.IGNORECASE)
                
                if autoexec_match:
                    autoexec_content = autoexec_match.group(1)
                    mount_match = MOUNT_C_REGEX.search(autoexec_content)
                    
                    if mount_match:
                        mount_path = mount_match.group(1).replace('/', '\\')
                        # Check if the path ends with the game folder name (potentially followed by drives\c)
                        search_pattern = rf'\\{re.escape(game_folder_name)}(\\drives\\c)?$'
                        
                        if re.search(search_pattern, mount_path, re.IGNORECASE):
                            print(f"| ✅ Profile found: {filename}")
                            
                            if 'PROFILES_MAP' not in cache:
                                cache['PROFILES_MAP'] = {}
                            cache['PROFILES_MAP'][filename] = game_folder_name
                            
                            try:
                                with open(cache_path, 'w') as cachefile: # Zápis novej hodnoty do cache na KOREŇOVEJ CESTE
                                    cache.write(cachefile)
                            except Exception:
                                pass # Ignorujeme chyby zápisu cache
                                
                            return profile_path
                            
            except Exception as e:
                pass
                
    print("| ❌ Profile not found based on MOUNT C command.")
    return None


def create_dosbox_conf(settings, path='.'):
    """
    Finds the DBGL profile, copies it, and adjusts absolute paths to relative.
    Ensures correct relativization for MOUNT and multiple IMGMOUNT paths.
    """
    print(f"\n| 🛠️ Searching, copying, and modifying dosbox.conf")
    
    folder_name = os.path.basename(os.path.abspath(path))
    target_path = os.path.join(path, 'dosbox.conf')
    
    profile_path = find_profile_by_mount_c(settings, folder_name)

    if not profile_path:
        raise Exception(f"Could not find DBGL profile for game '{folder_name}'.")
        
    try:
        # Backup existing .conf
        if os.path.exists(target_path):
            shutil.copy2(target_path, target_path + BAK_FILE_EXT)
            print(f"| 📁 Existing {os.path.basename(target_path)} backed up.")

        # Copy profile
        shutil.copy2(profile_path, target_path)
        print(f"| 💾 Profile copied: {os.path.basename(profile_path)}")

        with open(target_path, 'r', encoding='utf-8') as f:
            lines = f.readlines()
            
        new_content_lines = []
        folder_name_lower = folder_name.lower().replace('/', '\\')
        
        # Flags for modifications
        in_capture_section = False
        capture_removed = False
        mount_c_removed = False
        imgmount_relativized = False
        
        def relativize_imgmount_path(match):
            """Replaces the absolute path in quotes with a relative one if it belongs to the current game."""
            abs_path_raw = match.group(1) 
            abs_path_to_check = abs_path_raw.lower().replace('/', '\\') 
            
            # Check for the pattern '.../GameFolder/cd/...'
            if f'\\{folder_name_lower}\\' in abs_path_to_check and '\\cd\\' in abs_path_to_check:
                
                try:
                    # Find the index right after the game folder name
                    idx = abs_path_to_check.find(folder_name_lower)
                    # Extract the subpath, e.g., '\cd\image.iso'
                    relative_subpath_raw = abs_path_to_check[idx + len(folder_name_lower):]
                    # Clean the subpath: remove leading/trailing slashes, normalize separators
                    relative_subpath_cleaned = relative_subpath_raw.strip('\\/').replace('/', '\\')
                    
                except ValueError:
                    # Fallback
                    relative_subpath_cleaned = 'cd' 
                
                # Return the new relative path
                return f'".\\{relative_subpath_cleaned}"'
            else:
                return match.group(0) # No change
                
        path_in_quotes_regex = re.compile(r'"([^"]+)"')
        
        for line in lines:
            
            normalized_line = line.strip().lower()

            # 1. Remove [capture] section (as it typically uses absolute paths)
            if normalized_line == '[capture]':
                in_capture_section = True
                capture_removed = True 
                continue
            
            if in_capture_section:
                if normalized_line.startswith('['):
                    in_capture_section = False
                else:
                    continue
            
            # 2. Relativize MOUNT paths
            mount_match = re.search(r'^(?P<prefix>mount\s+[a-z]\s+")(?P<abs_path>.*?)(?P<suffix>"[\s\t]*.*)$', line, re.IGNORECASE)
            
            if mount_match:
                prefix = mount_match.group('prefix') 
                abs_path_raw = mount_match.group('abs_path') 
                abs_path_to_check = abs_path_raw.lower().replace('/', '\\') 
                suffix = mount_match.group('suffix').rstrip('\r\n') 
                
                # Check if the MOUNT path points to the current game folder structure
                if f'\\{folder_name_lower}\\' in abs_path_to_check or abs_path_to_check.endswith(folder_name_lower):
                    
                    mount_letter = re.search(r'mount\s+([a-z])', normalized_line).group(1).upper()

                    # Calculate relative subpath (e.g., drives\c)
                    try:
                        idx = abs_path_to_check.find(folder_name_lower)
                        relative_subpath_raw = abs_path_to_check[idx + len(folder_name_lower):]
                        relative_subpath_cleaned = relative_subpath_raw.strip('\\/').replace('/', '\\')
                    except ValueError:
                        relative_subpath_cleaned = ''
                    
                    if relative_subpath_cleaned:
                         relative_target_path = f'.\\{relative_subpath_cleaned}'
                    else:
                         relative_target_path = '.' 

                    # Check for MOUNT C preservation setting
                    if mount_letter == 'C' and settings.get('preserve_mount_c') == 'DISABLED':
                        if not mount_c_removed:
                             print("| ✨ MOUNT C removed (Setting DISABLED).")
                             mount_c_removed = True
                        continue # Skip adding the line

                    new_line = f'{prefix}{relative_target_path}{suffix}\n'
                    new_content_lines.append(new_line)
                    continue
            
            
            # 3. Relativize IMGMOUNT paths
            imgmount_match = re.search(r'^(?P<prefix>imgmount\s+[a-z]\s+)(?P<rest>.*)$', line, re.IGNORECASE)

            if imgmount_match:
                
                prefix = imgmount_match.group('prefix') 
                rest_of_line = imgmount_match.group('rest').rstrip('\r\n') 
                
                # Use the helper function to replace paths within the line
                new_rest_of_line = path_in_quotes_regex.sub(relativize_imgmount_path, rest_of_line)
                
                if new_rest_of_line != rest_of_line:
                    new_line = f'{prefix}{new_rest_of_line}\n'
                    new_content_lines.append(new_line)
                    if not imgmount_relativized:
                         print("| ✨ IMGMOUNT modifications completed (including multiple CDs).")
                         imgmount_relativized = True
                    continue
                    
            new_content_lines.append(line)
            
        if capture_removed:
            pass # Message printed above
        
        if mount_c_removed or imgmount_relativized:
              print("| ✨ MOUNT/IMGMOUNT modifications completed.")
        elif not mount_c_removed and not imgmount_relativized:
              print("| ⚠️ No MOUNT/IMGMOUNT modifications were necessary.")
        
        with open(target_path, 'w', encoding='utf-8') as f:
            f.writelines(new_content_lines)
            
        print("| ✅ dosbox.conf successfully modified and saved.")
        
    except Exception as e:
        raise Exception(f"Error processing file content: {e}")

def run_complete_setup(settings, path='.'):
    """Runs base folders, configuration, and BAT file creation."""
    create_base_folders(settings, path)
    create_dosbox_conf(settings, path)
    create_start_bat(settings, path)

def create_zip_archive(settings, path='.', with_dosbox=False):
    """Creates a ZIP archive of the game (with or without DOSBox) with correct filtering."""
    game_name = os.path.basename(os.path.abspath(path))
    target_dir = settings.get('path_to_zip_dest_dir')
    
    print(f"\n| 📦 Preparing archive for game: {game_name}")
    
    temp_dir = settings.get('path_to_temp_dir')
    zip_structure = settings.get('zip_dosbox_structure', 'SUBDIR') 

    # Filters for ZIP
    # Systémové súbory sú v TOOL_ROOT_DIR, takže ich filter je redundantný, ak nie sú v adresári hry
    # ale necháme ho tu pre istotu:
    EXCLUDE = {os.path.basename(__file__).lower(), INI_FILE.lower(), PROFILES_CACHE_FILE.lower(), LOG_FILE.lower()}
    if not with_dosbox:
        # For CLEAN ZIP, exclude !start.bat (it launches via .conf association)
        EXCLUDE.add('!start.bat'.lower()) 
        print("| ⚙️ Creating CLEAN ZIP. File '!start.bat' will be EXCLUDED.")
    
    temp_unique_root = None
    
    try:
        temp_unique_root = os.path.join(temp_dir, f'zip_tmp_{os.getpid()}')
        if os.path.exists(temp_unique_root): shutil.rmtree(temp_unique_root)
        os.makedirs(temp_unique_root, exist_ok=True)
        
        zip_base_dir = os.path.join(temp_unique_root, game_name)
        os.makedirs(zip_base_dir, exist_ok=True)
        
        print("| ⚙️ Copying files (Filtering tool files and backups)...")
        for item in os.listdir(path):
            
            item_lower = item.lower()
            
            if item_lower in EXCLUDE or item_lower.endswith(BAK_FILE_EXT):
                continue
            
            s = os.path.join(path, item)
            d = os.path.join(zip_base_dir, item)
            
            if os.path.isdir(s):
                shutil.copytree(s, d, dirs_exist_ok=True)
            elif os.path.isfile(s):
                shutil.copy2(s, d)

        # Logic for PORTABLE ZIP (with_dosbox = True)
        if with_dosbox:
            dosbox_exe_path = settings.get('path_to_dosbox_exe')
            dosbox_exe_filename = os.path.basename(dosbox_exe_path)
            
            if not os.path.exists(dosbox_exe_path):
                raise Exception("Path to DOSBox.exe is invalid, cannot create portable ZIP.")
            
            dosbox_dir = os.path.dirname(dosbox_exe_path)
            
            if zip_structure == 'SUBDIR':
                target_dosbox_dir = os.path.join(zip_base_dir, 'dosbox')
                shutil.copytree(dosbox_dir, target_dosbox_dir, dirs_exist_ok=True) 
                print(f"| ⚙️ DOSBox added to 'dosbox' folder (SUBDIR structure).")
            else: # FLAT
                shutil.copytree(dosbox_dir, zip_base_dir, dirs_exist_ok=True) 
                print(f"| ⚙️ DOSBox added directly to the game root (FLAT structure).")
                
            # Verify and fix !start.bat 
            bat_path_in_zip = os.path.join(zip_base_dir, '!start.bat')
            
            if zip_structure == 'SUBDIR':
                target_path_for_bat_in_zip = f'.\\dosbox\\{dosbox_exe_filename}'
            else:
                target_path_for_bat_in_zip = f'.\\{dosbox_exe_filename}'
            
            if os.path.exists(bat_path_in_zip):
                zip_bat_content = f"""
@echo off
rem Launch DOSBox with the configuration for the current directory
rem Path to DOSBox.exe is relative within the archive (portable archive).
"{target_path_for_bat_in_zip}" -conf dosbox.conf
                """
                with open(bat_path_in_zip, 'w') as f:
                    f.write(zip_bat_content.strip())
                print(f"| ⚙️ !start.bat in archive modified (path: {target_path_for_bat_in_zip}).")
            else:
                 print(f"| ⚠️ !start.bat not found in archive. Skipping modification.")


        # 3. Create final archive
        shutil.make_archive(
            os.path.join(target_dir, game_name), 
            'zip', 
            root_dir=temp_unique_root, 
            base_dir=game_name 
        )
        print(f"| ✅ Archive created in: {target_dir}\\{game_name}.zip")

    except Exception as e:
        raise Exception(f"Error creating archive: {e}")
    finally:
        if os.path.exists(temp_unique_root):
             shutil.rmtree(temp_unique_root)


def delete_backups(settings, path='.'):
    """Deletes only .bak backup files."""
    print(f"\n| 🗑️ Deleting backups ({BAK_FILE_EXT})")
    deleted_count = 0
    for item in os.listdir(path):
        if item.endswith(BAK_FILE_EXT):
            try:
                os.remove(os.path.join(path, item))
                print(f"| ✅ Deleted backup: {item}")
                deleted_count += 1
            except Exception as e:
                 raise Exception(f"Error deleting backup {item}: {e}")
                 
    if deleted_count == 0:
        print("| ℹ️ No *.bak files found for deletion.")

def delete_config_files(settings, path='.'):
    """Deletes !start.bat, dosbox.conf, and backups."""
    files_to_delete = ['!start.bat', 'dosbox.conf']
    
    print(f"\n| 💣 Deleting configuration")
    
    # Najprv zmazeme .bak subory cez volanie funkcie
    delete_backups(settings, path)
    
    deleted_config_count = 0
    for file in files_to_delete:
        file_path = os.path.join(path, file)
        if os.path.exists(file_path):
            try:
                os.remove(file_path)
                print(f"| ✅ Deleted file: {file}")
                deleted_config_count += 1
            except Exception as e:
                raise Exception(f"Error deleting configuration file {file}: {e}")
                
    if deleted_config_count == 0:
        print("| ℹ️ No configuration files found for deletion.")


def clean_up_and_exit():
    """Deletes the tool's helper files (INI, cache, log) and exits the program."""
    print("\n| 🧹 Cleaning up tool files...")
    files_to_delete = [INI_FILE, PROFILES_CACHE_FILE, LOG_FILE] 
    
    for file in files_to_delete:
        file_path = os.path.join(TOOL_ROOT_DIR, file) # POUŽITIE KOREŇOVEJ CESTY
        if os.path.exists(file_path):
            try:
                os.remove(file_path)
            except Exception as e:
                print(f"| ⚠️ Failed to delete {file} from root: {e}")
            else:
                 print(f"| ✅ Deleted file: {file}")

    print("\n| Program terminated.")
    sys.exit()


# --- SETTINGS MENU ---

def settings_menu_A(settings):
    """Displays and handles settings for paths and switches."""
    while True:
        os.system('cls' if os.name == 'nt' else 'clear')
        settings = load_settings() 
        print("\n# PATHS AND MODE SETTINGS #")
        print("=============================")
        
        # Unified display and existence check
        status_exe = check_existence(settings.get('path_to_dosbox_exe'), 'file')
        status_dbgl = check_existence(settings.get('path_to_DBGL_root'), 'dir')
        status_temp = check_existence(settings.get('path_to_temp_dir'), 'dir')
        status_zip_dest = check_existence(settings.get('path_to_zip_dest_dir'), 'dir')
        
        print(f"1. Emulator Path (ABS for calculation/copy) {status_exe}: {settings.get('path_to_dosbox_exe')}")
        print(f"2. DBGL Root Path (ABS) {status_dbgl}: {settings.get('path_to_DBGL_root')}")
        print(f"3. Temp Folder for ZIP (ABS) {status_temp}: {settings.get('path_to_temp_dir')}")
        print(f"4. ZIP Archives Destination (ABS) {status_zip_dest}: {settings.get('path_to_zip_dest_dir')}")
        print(f"5. Preserve Mount C: {settings.get('preserve_mount_c')}")
        print(f"6. Auto Mode Detection: {settings.get('automatic_mode_detection')}")
        print(f"7. DOSBox ZIP Structure: {settings.get('zip_dosbox_structure')}")
        print("---")
        
        print("1 – Enter new ABSOLUTE path for DOSBox.exe")
        print("2 – Enter new ABSOLUTE path for DBGL root")
        print("3 – Enter new ABSOLUTE path for TEMP folder for ZIP")
        print("4 – Enter new ABSOLUTE path for ZIP Archives DESTINATION folder")
        print("5 – Switch: Preserve MOUNT C command ({})".format(settings.get('preserve_mount_c')))
        print("6 – Switch: Automatic Mode Detection ({})".format(settings.get('automatic_mode_detection')))
        print("7 – Switch: DOSBox ZIP Structure ({})".format(settings.get('zip_dosbox_structure')))
        print("Q – Return to Main Menu")
        
        choice = input("\nEnter choice (1-7, Q): ").upper()
        
        if choice == 'Q':
            break
        elif choice == '1':
            new_path = input(f"Enter new ABSOLUTE path for DOSBox.exe: ")
            validate_and_save_path('path_to_dosbox_exe', new_path, item_type='file')
            input("Press Enter to continue...")
        elif choice == '2':
            new_path = input(f"Enter new ABSOLUTE path for DBGL root: ")
            validate_and_save_path('path_to_DBGL_root', new_path, item_type='dir')
            input("Press Enter to continue...")
        elif choice == '3':
            new_path = input(f"Enter new ABSOLUTE path for TEMP folder: ")
            validate_and_save_path('path_to_temp_dir', new_path, item_type='dir')
            input("Press Enter to continue...")
        elif choice == '4':
            new_path = input(f"Enter new ABSOLUTE path for ZIP destination: ")
            validate_and_save_path('path_to_zip_dest_dir', new_path, item_type='dir')
            input("Press Enter to continue...")
        elif choice == '5':
            new_value = 'DISABLED' if settings.get('preserve_mount_c') == 'ENABLED' else 'ENABLED'
            save_setting('preserve_mount_c', new_value)
            input("Press Enter to continue...")
        elif choice == '6':
            new_value = 'DISABLED' if settings.get('automatic_mode_detection') == 'ENABLED' else 'ENABLED'
            save_setting('automatic_mode_detection', new_value)
            input("Press Enter to continue...")
        elif choice == '7':
            new_value = 'SUBDIR' if settings.get('zip_dosbox_structure') == 'FLAT' else 'FLAT'
            save_setting('zip_dosbox_structure', new_value)
            input("Press Enter to continue...")
        else:
            print("| ⚠️ Invalid choice.")
            input("Press Enter to continue...")


# --- BATCH OPERATIONS MENU ---

def batch_operations_menu(settings, came_from_main_menu=False):
    """
    Handles batch operations for all subfolders.
    """
    
    # Pri štarte BATCH operácie vždy zabezpečíme zmazanie logu z predchádzajúcej session.
    log_file_abs_path = os.path.join(TOOL_ROOT_DIR, LOG_FILE)
    if os.path.exists(log_file_abs_path):
        try:
            os.remove(log_file_abs_path)
            print(f"| ℹ️ Old log file {LOG_FILE} cleaned up.")
        except Exception as e:
            print(f"| ⚠️ ERROR: Failed to delete old log file {LOG_FILE}: {e}")

    def execute_batch_operation(function, with_dosbox=None):
        """Helper function for iterating through subfolders with error logging."""
        
        # Uložíme si absolútnu cestu ku koreňovému adresáru BATCH (kde beží menu)
        batch_root_dir = os.getcwd() 
        
        start_time = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        print(f"\n| 🚀 Starting batch operation: {function.__name__} (Time: {start_time})")
        
        subfolders = [d for d in os.listdir('.') if os.path.isdir(d) and d.lower() not in KEY_FOLDERS and not d.startswith('.')]
        
        if not subfolders:
            print("| ⚠️ No game subfolders to process.")
            input("Press Enter to return...")
            return

        error_count = 0
        
        for folder in subfolders:
            print(f"\n--- Working in directory: {folder} ---")
            try:
                os.chdir(folder) # Vstup do podadresára
                if with_dosbox is not None:
                    function(settings, '.', with_dosbox)
                else:
                    function(settings, '.')
            except Exception as e:
                error_count += 1
                error_message = f"CRITICAL ERROR in directory '{folder}' during function '{function.__name__}': {e}"
                print(f"| ❌ {error_message}. More info in log: {LOG_FILE}")
                
                try:
                    log_entry = f"[{datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] FOLDER: {folder}\n  FUNCTION: {function.__name__}\n  ERROR: {e}\n{'-'*60}\n"
                    # Zápis do logu na ABSOLÚTNEJ CESTE (v koreni)
                    with open(log_file_abs_path, 'a', encoding='utf-8') as f:
                        f.write(log_entry)
                except Exception as log_e:
                    print(f"| ⚠️ ERROR writing to log: {log_e}")
            finally:
                os.chdir(batch_root_dir) # Dôležité: Vrátime sa späť do koreňového adresára
                
        print("\n| ✅ Batch operation completed.")
        if error_count > 0:
            print(f"| ⚠️ Find details about {error_count} errors in file {LOG_FILE}.")
        input("Press Enter to return...")


    while True:
        os.system('cls' if os.name == 'nt' else 'clear')
        settings = load_settings() 
        # Program name in the header
        print(f"\n# {PROGRAM_NAME} ({VERSION}) - MODE: BATCH #")
        print("======================================================")
        
        print("| Configuration |")
        print("1 – Create Base Folders (cd, docs, drives/c)")
        print("2 – Create/Update !start.bat only (Dynamic relative path for USB)")
        print("3 – Create/Update dosbox.conf only (.conf)")
        print("4 – Create/Update !start.bat & dosbox.conf (Complete Setup)")
        print("---")
        
        print("| Deletion |")
        print("5 – Delete only BACKUP files (.bak)") # Maže iba .bak v podadresároch
        print("6 – Delete CONFIGURATION files (!start.bat, dosbox.conf, backups)")
        print("---")

        print("| Archiving |")
        print("7 – Create PORTABLE ZIP (With DOSBox - Custom structure)")
        print("8 – Create CLEAN ZIP (Without DOSBox - For .conf association launch)")
        print("---")
        
        print("| System Functions |")
        print("A – Global SETTINGS (Paths, Switches)")
        print("X – CLEAN UP AND EXIT TOOL") # Toto vymaže aj LOG_FILE, INI, CACHE z koreňa
        
        if came_from_main_menu:
              print("Q – Return to Main Menu")
        else:
              print("Q – Exit Program")
        
        choice = input("\nEnter choice (1-8, A, X, Q): ").upper()

        if choice == 'Q':
            if came_from_main_menu:
                break 
            else:
                sys.exit() 
        elif choice == 'X':
            clean_up_and_exit()
        elif choice == 'A':
            settings_menu_A(settings)
        elif choice == '1':
            execute_batch_operation(create_base_folders)
        elif choice == '2':
            execute_batch_operation(create_start_bat)
        elif choice == '3':
            execute_batch_operation(create_dosbox_conf)
        elif choice == '4':
            execute_batch_operation(run_complete_setup)
        elif choice == '5':
            # Táto funkcia maže iba .bak v podadresároch
            execute_batch_operation(delete_backups) 
        elif choice == '6':
            execute_batch_operation(delete_config_files)
        elif choice == '7':
            # with_dosbox=True for PORTABLE ZIP
            execute_batch_operation(create_zip_archive, with_dosbox=True)
        elif choice == '8':
            # with_dosbox=False for CLEAN ZIP
            execute_batch_operation(create_zip_archive, with_dosbox=False)
        else:
            print("| ⚠️ Invalid choice.")
            input("Press Enter to continue...")


# --- SINGLE OPERATIONS MENU ---

def single_operations_menu(settings, came_from_main_menu=False):
    """
    Handles operations for the current (single game) folder.
    All functions use default path='.'.
    """
    game_name = os.path.basename(os.getcwd())
    while True:
        os.system('cls' if os.name == 'nt' else 'clear')
        settings = load_settings()
        print(f"\n# {PROGRAM_NAME} ({VERSION}) - MODE: SINGLE #")
        print(f"## Current Game Folder: {game_name}")
        print("======================================================")

        print("| Configuration |")
        print("1 – Create Base Folders (cd, docs, drives/c)")
        print("2 – Create/Update !start.bat only (Dynamic relative path for USB)")
        print("3 – Create/Update dosbox.conf only (.conf)")
        print("4 – Create/Update !start.bat & dosbox.conf (Complete Setup)")
        print("---")
        
        print("| Execution & Deletion |")
        print("R – RUN Game (!start.bat)")
        print("5 – Delete only BACKUP files (.bak)")
        print("6 – Delete CONFIGURATION files (!start.bat, dosbox.conf, backups)")
        print("---")

        print("| Archiving |")
        print("7 – Create PORTABLE ZIP (With DOSBox - Custom structure)")
        print("8 – Create CLEAN ZIP (Without DOSBox - For .conf association launch)")
        print("---")
        
        print("| System Functions |")
        print("A – Global SETTINGS (Paths, Switches)")
        print("X – CLEAN UP AND EXIT TOOL")
        
        if came_from_main_menu:
            print("Q – Return to Main Menu")
        else:
            print("Q – Exit Program")
        
        choice = input("\nEnter choice (1-8, R, A, X, Q): ").upper()

        try:
            if choice == 'Q':
                if came_from_main_menu:
                    break
                else:
                    sys.exit()
            elif choice == 'X':
                clean_up_and_exit()
            elif choice == 'A':
                settings_menu_A(settings)
            elif choice == '1':
                create_base_folders(settings)
            elif choice == '2':
                create_start_bat(settings)
            elif choice == '3':
                create_dosbox_conf(settings)
            elif choice == '4':
                run_complete_setup(settings)
            elif choice == 'R':
                run_start_bat()
                # Po spustení sa už nečaká na Enter, ale vrátime sa priamo do menu
                continue 
            elif choice == '5':
                delete_backups(settings)
            elif choice == '6':
                delete_config_files(settings)
            elif choice == '7':
                create_zip_archive(settings, with_dosbox=True)
            elif choice == '8':
                create_zip_archive(settings, with_dosbox=False)
            else:
                print("| ⚠️ Invalid choice.")
                
        except Exception as e:
            print(f"\n| ❌ CRITICAL ERROR during operation: {e}")
        
        # Ostatné operácie (konfigurácia, mazanie, ZIP) čakajú na Enter
        input("Press Enter to continue...")


# --- MAIN MENU AND EXECUTION ---

def main_menu():
    """
    Displays the main menu and handles the primary logic flow.
    """
    os.system('cls' if os.name == 'nt' else 'clear')
    print(f"# {PROGRAM_NAME} ({VERSION}) #")
    print("================================")

    settings = load_settings()
    
    detected_mode = detect_working_mode()
    automatic_mode = settings.get('automatic_mode_detection') == 'ENABLED'
    current_path = os.getcwd()
    
    print(f"| 🏠 Current Folder: {current_path}")
    print(f"| 🧠 Detected Mode: {detected_mode}")
    print(f"| ⚙️ Automatic Mode: {settings.get('automatic_mode_detection')}")
    print("---")

    if automatic_mode and detected_mode in ('SINGLE', 'BATCH'):
        print(f"| 🚀 Starting in {detected_mode} mode (Automatic Mode ON)...")
        if detected_mode == 'SINGLE':
            single_operations_menu(settings)
        elif detected_mode == 'BATCH':
            batch_operations_menu(settings)
            
    while not automatic_mode or detected_mode == 'UNCERTAIN':
        os.system('cls' if os.name == 'nt' else 'clear')
        settings = load_settings()
        print(f"\n# {PROGRAM_NAME} ({VERSION}) - MAIN MENU #")
        print("=========================================")
        print(f"| 🏠 Current Folder: {current_path}")
        print(f"| 🧠 Detected Mode: {detected_mode}")
        print(f"| ⚙️ Automatic Mode: {settings.get('automatic_mode_detection')}")
        print("---")
        print("1 – SINGLE-Game Operations (Current Folder)")
        print("2 – BATCH Operations (All Subfolders)")
        print("A – Global SETTINGS (Paths, Switches)")
        print("X – CLEAN UP AND EXIT TOOL")
        print("Q – Exit Program")
        print("---")
        
        choice = input("\nEnter choice (1, 2, A, X, Q): ").upper()
        
        if choice == 'Q':
            sys.exit()
        elif choice == 'X':
            clean_up_and_exit()
        elif choice == 'A':
            settings_menu_A(settings)
        elif choice == '1':
            single_operations_menu(settings, came_from_main_menu=True)
        elif choice == '2':
            batch_operations_menu(settings, came_from_main_menu=True)
        else:
            print("| ⚠️ Invalid choice.")
            input("Press Enter to continue...")


if __name__ == '__main__':
    try:
        main_menu()
    except KeyboardInterrupt:
        print("\n| Program terminated by user (Ctrl+C).")
        sys.exit()