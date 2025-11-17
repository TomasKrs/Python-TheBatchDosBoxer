# THE BATCH (DOS)BOX(ER) (v1.0)
Programátor: AI  -----   PromptMaster: TomasKrs

The Batch (DOS)Box(er) is a script designed to automate the configuration and management of games emulated through DOSBox. 
It is specifically intended for centralized and portable game collections (e.g., stored on a USB drive) and for use alongside profile manager DBGL (DOSBox Game Launcher).

## 💻 Features & Capabilities
✔ Path Conversion
Transforms absolute DBGL paths into relative ones, ensuring true portability across different systems.

✔ Configuration Export
Automatically generates a clean, standalone dosbox.conf file based on the game’s DBGL profile.

✔ Archive Creation
Supports creating ZIP packages (dosbox.conf and !start with DOSBox or without it)

## 💻 Features & Functionality
The tool operates in two main modes:
1. SINGLE Mode - Processes only the current game directory.
2. BATCH Mode - Processes all subdirectories (games) within the working directory at once.

## 💻 Requirements
Before using The Batch (DOS)Box(er), make sure the following components are installed and properly configured:

✔ DBGL (DOSBox Game Launcher)
Required for generating or managing the initial configuration profiles. The script extracts settings from DBGL-generated configuration files to create the final dosbox.conf.

✔ Python (3.x)
The script is written in Python and requires a functioning Python installation. Make sure Python is available in your system’s PATH so it can be executed from any directory.


## 💻 Getting started
**✔ Step 1: Copy the Script **

Before running the tool, decide how you intend to work with your game collection. The placement of the script determines which mode will be used.

**Option A** — Working with a Single Game - If you want to modify or prepare one specific game, copy the script directly into that game’s directory. The script will automatically operate in SINGLE mode.

**Option B** — Working with Multiple Games at Once - If you want to process several games in bulk, copy the script into the parent directory containing all game folders. Each subfolder will be treated as a separate game, and the script will run in BATCH mode.

**✔ Step 2: Running the Script**

In some cases, the script may not be able to determine the correct operating mode immediately after launch. This usually occurs when the script is placed in an empty or newly created directory, where it is not yet clear whether this folder is meant to hold a single game, or multiple game subdirectories. 

When this happens, the script will show, that it is on UNCERTAIN mode and ask you to choose manually between SINGLE mode or BATCH mode. Continue based on your selection.

<img width="663" height="294" alt="obrázok" src="https://github.com/user-attachments/assets/e17dd882-6c89-4a48-b537-5c5f05621cc9" />

**✔ Step 3: The Global Settings**  
Before choosing between SINGLE or BATCH mode, the script first requires you to configure the Global Settings.

<img width="905" height="404" alt="obrázok" src="https://github.com/user-attachments/assets/5f017039-77ff-4384-aa94-ea1e85052d89" />

Lets talk about the Global settings a bit (and why are they immportant)

✅ 1. Emulator Path (ABS for calculation/copy) - This will be used for running games (in single mode), creating !start.bat with relatives path and zipped games (with DOSBox inside). You need to add the path also with dosbox.exe file. Example: C:\dosbox\dosbox.exe

✅ 2. DBGL Root Path (ABS): This will be a path to DBGL root. There will a profile directory, where all the confs files are stored. Example: D:\

✅ 3. Temp Folder for ZIP (ABS) - a folder for where zipped games will be prepared. Example: C:\Temp\Final\TMP

✅ 4. ZIP Archives Destination (ABS) - a folder, where zipped games will be placed (in final zip form). Ecample: C:\Temp\Final

✅ 5. Preserve Mount C: ENABLED - this parameter can be omited by DOSBOX Stagging. If there is a directory structure, where drives/c is, he automaticly mount C to this directory (if enabled, dosbox.conf will not ommited mount C)

✅ 6. Auto Mode Detection: ENABLED - script will try to guest in which mode you will be in (single/uncertain or batch) If disabled, you always need to select single or batch mode). 

✅ 7. DOSBox ZIP Structure: SUBDIR - this will affect zipped games - there are two choises - SUBDIR (games will have DOSBox directory) or FLAT (DOSBox will be copyied inside directory where !start.bat and dosbox.conf resist).

✅ Q - will bring you back to SINGLE or BATCH mode


## 💻 Structure of MENU and Fumctions - SINGLE MODE
This guide explains the functions available in the SINGLE mode, which operates specifically on the currently active game folder.

<img width="733" height="488" alt="obrázok" src="https://github.com/user-attachments/assets/bf48f4e7-0e6d-40d1-994b-d01bf850fe83" />

    **📝 Configuration**

📝 1.	Create Base Folders - Creates the essential subdirectories for a standardized DOSBox game structure: cd, docs, and drives/c.

📝 2.	Create/Update !start.bat - Generates or updates the !start.bat file. This batch file contains a dynamically calculated relative path to your centralized DOSBox executable, ensuring portability (e.g., when run from a USB drive).

📝 3.	Create/Update dosbox.conf - Searches the DBGL profile directory for the matching configuration (.conf) based on the game folder name. It then copies the profile and automatically converts all absolute paths (MOUNT/IMGMOUNT) to relative paths (.\drives\c, .\cd\image.iso).

📝 4.	Create/Update !start.bat & dosbox.conf	- Runs options 1, 2, and 3 sequentially, performing a complete setup of the current game folder.

    **🚀 Execution & Deletion**

🚀 R	RUN Game	Executes the - !start.bat file in a non-blocking way (opens in a new window/process), allowing the tool's menu to remain instantly accessible.

🚀 5.	Delete only BACKUP files - Deletes all backup files created by the tool (files ending with .bak) within the current game folder.

🚀 6.	Delete CONFIGURATION files - Deletes all generated configuration files: !start.bat, dosbox.conf, and any associated .bak files.
    
    **💾 Archiving**

💾 7.	Create PORTABLE ZIP - Creates a ZIP archive containing the entire game folder plus a copy of the DOSBox emulator files (either in a subdirectory or flat structure, as defined in settings).

💾 8.	Create CLEAN ZIP - Creates a ZIP archive containing only the game and configuration files (dosbox.conf), excluding the DOSBox executable and the !start.bat file. This is intended for systems where DOSBox is launched via .conf file association.

    **⚙️ System Functions**

⚙️ A	Global SETTINGS -	Accesses the configuration menu to adjust global paths (DOSBox EXE, DBGL Root, Temp/ZIP Destination) and toggle operational switches (e.g., preserve MOUNT C).

⚙️ X	CLEAN UP AND EXIT TOOL - Deletes all tool-related system files (theBatchDosBoxer.ini, profiles_cache.ini, batch_operations_log.txt) from the root directory and immediately closes the program.

⚙️ Q	Return to Main Menu - Exits the SINGLE mode menu and returns to the main menu for mode selection (or exits the program if entered directly).

## 💻 Structure of MENU and Fumctions - BATCH MODE
This guide explains the functions available in the BATCH mode, which executes the selected operation on every game subdirectory found within the current directory.

<img width="769" height="440" alt="obrázok" src="https://github.com/user-attachments/assets/d3d6cb30-ec45-4d67-b922-6bffeb44cb23" />

    **📝 Configuration

📝 1.	Create Base Folders - Creates the essential subdirectories (cd, docs, drives/c) inside every game folder.

📝 2.	Create/Update !start.bat only - Generates or updates the portable !start.bat file in every game folder, calculating the relative path to the centralized DOSBox executable.

📝 3.	Create/Update dosbox.conf only - For every game folder, it finds the corresponding DBGL profile, copies it, and automatically converts all absolute paths to relative paths. This step uses the profiles_cache.ini for faster execution.

📝 4.	Create/Update !start.bat & dosbox.conf - Performs a Complete Setup on all game folders (runs options 1, 2, and 3 sequentially).

    **💣 Deletion

💣 5.	Delete only BACKUP files - Deletes all backup files (.bak) in all game folders.

💣 6.	Delete CONFIGURATION files - Deletes !start.bat, dosbox.conf, and any associated .bak files in all game folders.

    **📦 Archiving

📦 7.	Create PORTABLE ZIP - Creates a ZIP archive for every game, including the game files, configuration, and a copy of the DOSBox emulator itself.

📦 8.	Create CLEAN ZIP - Creates a ZIP archive for every game, including only the game files and dosbox.conf, suitable for systems using .conf file association.

    **⚙️ System Functions

⚙️ A	Global SETTINGS - Accesses the configuration menu to adjust global paths and toggle operational switches.

⚙️ X	CLEAN UP AND EXIT TOOL - Deletes all tool-related system files (.ini, .cache, .log) from the root directory and immediately closes the program.

⚙️ Q	Return to Main Menu - Exits the BATCH mode menu and returns to the main menu for mode selection (or exits the program if entered directly).

## About the Author
This program was programmed by AI. It was a test, if it will be possible to create this little utility. Its up to you decide if it is good or not. 
The prompting was done 100% by Me (TomasKrs).
