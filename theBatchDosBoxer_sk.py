import os
import sys
import shutil
import configparser
import re
import datetime
import os.path 

# --- KONŠTANTY ---
INI_FILE = 'theBatchDosBoxer.ini' # NOVÝ NÁZOV INI SÚBORU
PROFILES_CACHE_FILE = 'profiles_cache.ini' 
LOG_FILE = 'hromadne_operacie_log.txt' 
KLUC_SUBORY = ['!start.bat', 'dosbox.conf']
KLUC_PRIECINKY = ['cd', 'docs', 'drives']
BAK_FILE_EXT = '.bak'
MOUNT_C_REGEX = re.compile(r'mount C\s+"(.*?)"', re.IGNORECASE)
VERZIA = 'v1.0' 
NAZOV_PROGRAMU = 'The Batch (DOS)Box(er)' 

# --- MANIPULÁCIA S NASTAVENIAMI (INI) ---

def nacitat_nastavenia():
    """Načíta nastavenia alebo nastaví predvolené hodnoty."""
    config = configparser.ConfigParser()
    # Používa INI_FILE = 'theBatchDosBoxer.ini'
    config.read(INI_FILE)

    if 'GLOBAL' not in config:
        config['GLOBAL'] = {}

    # Nastavenia ciest
    config['GLOBAL']['cesta_k_dosbox_exe'] = config['GLOBAL'].get('cesta_k_dosbox_exe', 'F:\\emulators\\dosbox_staging\\dosbox.exe')
    config['GLOBAL']['cesta_k_DBGL_root'] = config['GLOBAL'].get('cesta_k_DBGL_root', 'F:\\DBGL\\')
    config['GLOBAL']['cesta_k_temp_dir'] = config['GLOBAL'].get('cesta_k_temp_dir', 'C:\\Temp\\DBTemp\\')
    config['GLOBAL']['cesta_k_zip_dest_dir'] = config['GLOBAL'].get('cesta_k_zip_dest_dir', 'C:\\Temp\\')

    # Nastavenia prepínačov
    config['GLOBAL']['zachovat_mount_c'] = config['GLOBAL'].get('zachovat_mount_c', 'ZAPNUTÉ')
    config['GLOBAL']['automaticka_detekcia_rezimu'] = config['GLOBAL'].get('automaticka_detekcia_rezimu', 'VYPNUTÉ')
    
    # Nastavenia ZIP
    config['GLOBAL']['zip_dosbox_structure'] = config['GLOBAL'].get('zip_dosbox_structure', 'FLAT') 
    
    # Zápis do nového súboru theBatchDosBoxer.ini
    with open(INI_FILE, 'w') as configfile:
        config.write(configfile)

    return config['GLOBAL']

def ulozit_nastavenie(kluc, hodnota):
    """Zapíše konkrétnu hodnotu do INI súboru."""
    config = configparser.ConfigParser()
    # Používa INI_FILE = 'theBatchDosBoxer.ini'
    config.read(INI_FILE)
    
    if 'GLOBAL' not in config:
        config['GLOBAL'] = {}
        
    config['GLOBAL'][kluc] = hodnota

    try:
        # Zápis do nového súboru theBatchDosBoxer.ini
        with open(INI_FILE, 'w') as configfile:
            config.write(configfile)
        print(f"| ✅ Nastavenie '{kluc}' aktualizované na: {hodnota}")
    except Exception as e:
        print(f"| ❌ CHYBA PRI ZÁPISE NASTAVENIA: {e}")


# --- FUNKCIA ČISTENIA NÁSTROJA (aktualizovaná pre nový INI) ---

def vycistit_nastroj():
    """Vymaže pomocné súbory nástroja (INI, cache, log) a ukončí program."""
    print("\n| 🧹 Vyčistenie nástroja...")
    # Aktualizovaný zoznam súborov na vymazanie
    súbory_na_vymazanie = [INI_FILE, PROFILES_CACHE_FILE, LOG_FILE] 
    
    for subor in súbory_na_vymazanie:
        if os.path.exists(subor):
            try:
                os.remove(subor)
                print(f"| ✅ Vymazaný súbor: {subor}")
            except Exception as e:
                print(f"| ⚠️ Nepodarilo sa vymazať {subor}: {e}")

    print("\n| Program bol ukončený.")
    sys.exit()

# ... (Všetky ostatné funkcie zostávajú nezmenené, pretože používajú konštantu INI_FILE) ...


def detekovat_rezim_prace(cesta='.'):
    """
    Analyzuje aktuálny priečinok a určuje režim práce: 'SINGLE', 'BATCH', 'UNCERTAIN'.
    """
    obsah = os.listdir(cesta)
    
    je_priečinok_hry = any(
        (os.path.isdir(item) and item.lower() in KLUC_PRIECINKY) or 
        (os.path.isfile(item) and item.lower() in KLUC_SUBORY)
        for item in obsah
    )
    if je_priečinok_hry:
        return 'SINGLE'
    
    pocet_podadresárov_hier = sum(
        1 for item in obsah 
        if os.path.isdir(item) and item.lower() not in KLUC_PRIECINKY and not item.startswith('.')
    )
    
    if pocet_podadresárov_hier >= 2:
        return 'BATCH'
        
    return 'UNCERTAIN'

def over_existenciu(cesta, typ='dir'):
    """Overí existenciu cesty a vráti stavový symbol."""
    if not cesta:
        return "[⚠️ Nezadané]"
    
    exists = os.path.exists(cesta)
    
    if not exists:
        return "[❌ Nenájdené]"
    
    if typ == 'file':
        return "[✅ Súbor OK]" if os.path.isfile(cesta) else "[⚠️ Nie je súbor]"
    elif typ == 'dir':
        return "[✅ Priečinok OK]" if os.path.isdir(cesta) else "[⚠️ Nie je priečinok]"
    return "[✅ OK]"


def over_a_uloz_cestu(kluc, nova_cesta, typ='dir'):
    """Overí existenciu, ak je to možné, a uloží cestu."""
    if not nova_cesta:
        print("| ⚠️ Cesta nemôže byť prázdna. Nastavenie neuložené.")
        return

    exists = os.path.exists(nova_cesta)

    if exists:
        if typ == 'file' and not os.path.isfile(nova_cesta):
            print(f"| ❌ CHYBA: Cesta '{nova_cesta}' existuje, ale nie je to súbor.")
            return
        elif typ == 'dir' and not os.path.isdir(nova_cesta):
            print(f"| ❌ CHYBA: Cesta '{nova_cesta}' existuje, ale nie je to priečinok.")
            return
        
        ulozit_nastavenie(kluc, nova_cesta)
        print(f"| ✅ Cesta overená a uložená.")
    else:
        # Pre priečinky povoľujeme vytvorenie (napr. temp priečinok), ale upozorníme.
        if typ == 'dir':
            try:
                os.makedirs(nova_cesta, exist_ok=True)
                ulozit_nastavenie(kluc, nova_cesta)
                print(f"| ⚠️ Priečinok neexistoval, bol vytvorený a uložený.")
            except Exception as e:
                print(f"| ❌ CHYBA: Priečinok neexistuje a nepodarilo sa ho vytvoriť: {e}")
        else:
            print(f"| ❌ CHYBA: Súbor alebo priečinok nebol nájdený na adrese: {nova_cesta}")
            print("| Nastavenie neuložené.")

def vytvorit_zakladne_priecinky(nastavenia, cesta='.'):
    """Vytvorí základnú štruktúru priečinkov pre hru."""
    print(f"\n| 🛠️ Vytváram základné priečinky")
    try:
        os.makedirs(os.path.join(cesta, 'cd'), exist_ok=True)
        os.makedirs(os.path.join(cesta, 'docs'), exist_ok=True)
        os.makedirs(os.path.join(cesta, 'drives', 'c'), exist_ok=True)
        print("| ✅ Štruktúra priečinkov vytvorená: cd, docs, drives/c")
    except Exception as e:
        raise Exception(f"Chyba pri vytváraní priečinkov: {e}")

def vytvorit_start_bat(nastavenia, cesta='.'):
    """
    Vytvorí alebo aktualizuje !start.bat. 
    Dynamicky vypočíta RELATÍVNU cestu z aktuálneho adresára hry do centrálneho DOSBox.exe.
    Tento BAT je určený pre LOKÁLNE spustenie v portabilnom (USB) prostredí.
    """
    print(f"\n| 🛠️ Vytváram/Aktualizujem !start.bat (Dynamická relatívna cesta)")
    
    dosbox_exe_abs_path = nastavenia.get('cesta_k_dosbox_exe')
    
    if not os.path.exists(dosbox_exe_abs_path):
        raise Exception("Absolútna cesta k DOSBox.exe v nastaveniach je neplatná. Pre dynamický výpočet cesty musí existovať.")

    # Vypočítame relatívnu cestu z aktuálneho priečinka (cesta) k cieľovému súboru (dosbox_exe_abs_path)
    try:
        cielova_cesta_pre_bat = os.path.relpath(dosbox_exe_abs_path, os.path.abspath(cesta))
    except ValueError as e:
        raise Exception(f"Chyba pri výpočte relatívnej cesty (sú na rôznych diskoch?): {e}")

    # Normalizácia cesty pre kompatibilitu s Windows BAT
    cielova_cesta_pre_bat = cielova_cesta_pre_bat.replace('/', '\\')

    print(f"| ⚠️ Použitá RELATÍVNA cesta: {cielova_cesta_pre_bat}")

    bat_obsah = f"""
@echo off
rem Spusti DOSBox s konfiguráciou pre aktuálny adresár
rem Relatívna cesta dynamicky vypočítaná pre portabilnú centralizovanú instaláciu DOSBoxu na USB.
"{cielova_cesta_pre_bat}" -conf dosbox.conf
    """
    
    try:
        súbor_cesta = os.path.join(cesta, '!start.bat')
        with open(súbor_cesta, 'w') as f:
            f.write(bat_obsah.strip())
        print(f"| ✅ Súbor !start.bat vytvorený/aktualizovaný. Volá: {cielova_cesta_pre_bat}")
    except Exception as e:
        raise Exception(f"Chyba pri vytváraní !start.bat: {e}")


def najst_profil_podla_mount_c(nastavenia, nazov_hry_priečinok):
    """
    Hľadá správny DBGL profil v profiles/ podľa obsahu MOUNT C príkazu.
    Používa cache pre zrýchlenie opakovaných operácií.
    """
    dbgl_profiles_dir = os.path.join(nastavenia.get('cesta_k_DBGL_root'), 'profiles')
    
    # --- 1. KROK: Hľadať v CACHE ---
    cache = configparser.ConfigParser()
    cache.read(PROFILES_CACHE_FILE)
    
    if 'PROFILES_MAP' in cache:
        for profil_file, mapped_game_dir in cache['PROFILES_MAP'].items():
            if nazov_hry_priečinok.lower() == mapped_game_dir.lower():
                profil_cesta = os.path.join(dbgl_profiles_dir, profil_file)
                if os.path.exists(profil_cesta):
                    print(f"| ✅ Profil nájdený v CACHE: {profil_file}")
                    return profil_cesta
                else:
                    del cache['PROFILES_MAP'][profil_file]
                    print(f"| ⚠️ Záznam '{profil_file}' odstránený z cache.")
        
        with open(PROFILES_CACHE_FILE, 'w') as cachefile:
            cache.write(cachefile)

    # --- 2. KROK: ITERÁCIA A HĽADANIE OBSAHU ---
    
    if not os.path.isdir(dbgl_profiles_dir):
         print(f"| ❌ Adresár profilov DBGL nebol nájdený: {dbgl_profiles_dir}")
         return None
         
    print(f"| 🔍 Hľadám profil v {os.path.basename(dbgl_profiles_dir)} podľa obsahu (pomalé)...")
    
    for filename in os.listdir(dbgl_profiles_dir):
        if filename.endswith('.conf'):
            profil_cesta = os.path.join(dbgl_profiles_dir, filename)
            
            try:
                with open(profil_cesta, 'r', encoding='utf-8') as f:
                    content = f.read()
                
                autoexec_match = re.search(r'\[autoexec\](.*)', content, re.DOTALL | re.IGNORECASE)
                
                if autoexec_match:
                    autoexec_content = autoexec_match.group(1)
                    mount_match = MOUNT_C_REGEX.search(autoexec_content)
                    
                    if mount_match:
                        mount_path = mount_match.group(1).replace('/', '\\')
                        hladany_vzor = rf'\\{re.escape(nazov_hry_priečinok)}(\\drives\\c)?$'
                        
                        if re.search(hladany_vzor, mount_path, re.IGNORECASE):
                            print(f"| ✅ Profil nájdený: {filename}")
                            
                            if 'PROFILES_MAP' not in cache:
                                cache['PROFILES_MAP'] = {}
                            cache['PROFILES_MAP'][filename] = nazov_hry_priečinok
                            
                            with open(PROFILES_CACHE_FILE, 'w') as cachefile:
                                cache.write(cachefile)
                                
                            return profil_cesta
                            
            except Exception as e:
                pass
                
    print("| ❌ Profil nebol nájdený podľa MOUNT C príkazu.")
    return None


def vytvorit_dosbox_conf(nastavenia, cesta='.'):
    """
    Nájde DBGL profil, kopíruje ho a upravuje absolútne cesty na relatívne.
    Zabezpečuje správnu relativizáciu pre MOUNT a pre viacnásobné IMGMOUNT cesty.
    """
    print(f"\n| 🛠️ Hľadám, kopírujem a upravujem dosbox.conf")
    
    nazov_priečinka = os.path.basename(os.path.abspath(cesta))
    cil_cesta = os.path.join(cesta, 'dosbox.conf')
    
    profil_cesta = najst_profil_podla_mount_c(nastavenia, nazov_priečinka)

    if not profil_cesta:
        raise Exception(f"Nepodarilo sa nájsť DBGL profil pre hru '{nazov_priečinka}'.")
        
    try:
        if os.path.exists(cil_cesta):
            shutil.copy2(cil_cesta, cil_cesta + BAK_FILE_EXT)
            print(f"| 📁 Existujúci {os.path.basename(cil_cesta)} zálohovaný.")

        shutil.copy2(profil_cesta, cil_cesta)
        print(f"| 💾 Profil skopírovaný: {os.path.basename(profil_cesta)}")

        with open(cil_cesta, 'r', encoding='utf-8') as f:
            lines = f.readlines()
            
        novy_obsah_lines = []
        nazov_priečinka_lower = nazov_priečinka.lower().replace('/', '\\')
        
        v_capture_sekcii = False
        capture_removed = False
        mount_c_removed = False
        imgmount_relativized = False
        
        def relativizuj_imgmount_cestu(match):
            """Nahradí absolútnu cestu v úvodzovkách relatívnou, ak patrí k aktuálnej hre."""
            abs_path_raw = match.group(1) 
            abs_path_to_check = abs_path_raw.lower().replace('/', '\\') 
            
            if f'\\{nazov_priečinka_lower}\\' in abs_path_to_check and '\\cd\\' in abs_path_to_check:
                
                try:
                    idx = abs_path_to_check.find(nazov_priečinka_lower)
                    relativna_podcesta_raw = abs_path_to_check[idx + len(nazov_priečinka_lower):]
                    relativna_podcesta_cleaned = relativna_podcesta_raw.strip('\\/').replace('/', '\\')
                    
                except ValueError:
                    relativna_podcesta_cleaned = 'cd' 
                
                return f'".\\{relativna_podcesta_cleaned}"'
            else:
                return match.group(0)
                
        path_in_quotes_regex = re.compile(r'"([^"]+)"')
        
        for line in lines:
            
            normalized_line = line.strip().lower()

            if normalized_line == '[capture]':
                v_capture_sekcii = True
                capture_removed = True 
                continue
            
            if v_capture_sekcii:
                if normalized_line.startswith('['):
                    v_capture_sekcii = False
                else:
                    continue
            
            mount_match = re.search(r'^(?P<prefix>mount\s+[a-z]\s+")(?P<abs_path>.*?)(?P<suffix>"[\s\t]*.*)$', line, re.IGNORECASE)
            
            if mount_match:
                prefix = mount_match.group('prefix') 
                abs_path_raw = mount_match.group('abs_path') 
                abs_path_to_check = abs_path_raw.lower().replace('/', '\\') 
                suffix = mount_match.group('suffix').rstrip('\r\n') 
                
                if f'\\{nazov_priečinka_lower}\\' in abs_path_to_check or abs_path_to_check.endswith(nazov_priečinka_lower):
                    
                    mount_letter = re.search(r'mount\s+([a-z])', normalized_line).group(1).upper()

                    try:
                        idx = abs_path_to_check.find(nazov_priečinka_lower)
                        relativna_podcesta_raw = abs_path_to_check[idx + len(nazov_priečinka_lower):]
                        relativna_podcesta_cleaned = relativna_podcesta_raw.strip('\\/').replace('/', '\\')
                    except ValueError:
                        relativna_podcesta_cleaned = ''
                    
                    if relativna_podcesta_cleaned:
                         relativna_cilova_cesta = f'.\\{relativna_podcesta_cleaned}'
                    else:
                         relativna_cilova_cesta = '.' 

                    if mount_letter == 'C' and nastavenia.get('zachovat_mount_c') == 'VYPNUTÉ':
                        if not mount_c_removed:
                             print("| ✨ MOUNT C odstránený (Nastavenie VYPNUTÉ).")
                             mount_c_removed = True
                        continue 

                    new_line = f'{prefix}{relativna_cilova_cesta}{suffix}\n'
                    novy_obsah_lines.append(new_line)
                    continue
            
            
            imgmount_match = re.search(r'^(?P<prefix>imgmount\s+[a-z]\s+)(?P<rest>.*)$', line, re.IGNORECASE)

            if imgmount_match:
                
                prefix = imgmount_match.group('prefix') 
                rest_of_line = imgmount_match.group('rest').rstrip('\r\n') 
                
                nova_rest_of_line = path_in_quotes_regex.sub(relativizuj_imgmount_cestu, rest_of_line)
                
                if nova_rest_of_line != rest_of_line:
                    new_line = f'{prefix}{nova_rest_of_line}\n'
                    novy_obsah_lines.append(new_line)
                    if not imgmount_relativized:
                         print("| ✨ Úpravy IMGMOUNT dokončené (vrátane viacerých CD).")
                         imgmount_relativized = True
                    continue
                    
            novy_obsah_lines.append(line)
            
        if capture_removed:
            print("| ✨ Sekcia [capture] odstránená.")
        
        if mount_c_removed or imgmount_relativized:
             print("| ✨ Úpravy MOUNT/IMGMOUNT dokončené.")
        elif not mount_c_removed and not imgmount_relativized:
             print("| ⚠️ Žiadne MOUNT/IMGMOUNT úpravy neboli potrebné.")
        
        with open(cil_cesta, 'w', encoding='utf-8') as f:
            f.writelines(novy_obsah_lines)
            
        print("| ✅ dosbox.conf úspešne upravený a uložený.")
        
    except Exception as e:
        raise Exception(f"Chyba pri spracovaní obsahu súboru: {e}")

def kompletne_nastavenie(nastavenia, cesta='.'):
    """Spustí základné priečinky, konfiguráciu a BAT súbor."""
    vytvorit_zakladne_priecinky(nastavenia, cesta)
    vytvorit_dosbox_conf(nastavenia, cesta)
    vytvorit_start_bat(nastavenia, cesta)

def vytvorit_zip_archiv(nastavenia, cesta='.', s_dosboxom=False):
    """Vytvorí ZIP archív hry (s alebo bez DOSBoxu) s korektným filtrovaním."""
    nazov_hry = os.path.basename(os.path.abspath(cesta))
    cil_dir = nastavenia.get('cesta_k_zip_dest_dir')
    
    print(f"\n| 📦 Pripravujem archív pre hru: {nazov_hry}")
    
    temp_dir = nastavenia.get('cesta_k_temp_dir')
    zip_štruktúra = nastavenia.get('zip_dosbox_structure', 'FLAT')

    # Filtre pre ZIP
    VYLÚČIŤ = {os.path.basename(__file__).lower(), INI_FILE.lower(), PROFILES_CACHE_FILE.lower(), LOG_FILE.lower()}
    if not s_dosboxom:
        # Pre ČISTÝ ZIP vylúčime !start.bat (spúšťa sa cez asociáciu .conf)
        VYLÚČIŤ.add('!start.bat'.lower()) 
        print("| ⚙️ Vytváram ČISTÝ ZIP. Súbor '!start.bat' bude VYLÚČENÝ.")
    
    temp_unique_root = None
    
    try:
        temp_unique_root = os.path.join(temp_dir, f'zip_tmp_{os.getpid()}')
        if os.path.exists(temp_unique_root): shutil.rmtree(temp_unique_root)
        os.makedirs(temp_unique_root, exist_ok=True)
        
        zip_base_dir = os.path.join(temp_unique_root, nazov_hry)
        os.makedirs(zip_base_dir, exist_ok=True)
        
        print("| ⚙️ Kopírujem súbory (Filtrujem súbory nástroja a zálohy)...")
        for item in os.listdir(cesta):
            
            item_lower = item.lower()
            
            if item_lower in VYLÚČIŤ or item_lower.endswith(BAK_FILE_EXT):
                continue
            
            s = os.path.join(cesta, item)
            d = os.path.join(zip_base_dir, item)
            
            if os.path.isdir(s):
                shutil.copytree(s, d, dirs_exist_ok=True)
            elif os.path.isfile(s):
                shutil.copy2(s, d)

        # Logika pre PRENOSNÝ ZIP (s_dosboxom = True)
        if s_dosboxom:
            dosbox_exe_path = nastavenia.get('cesta_k_dosbox_exe')
            dosbox_exe_filename = os.path.basename(dosbox_exe_path)
            
            if not os.path.exists(dosbox_exe_path):
                raise Exception("Cesta k DOSBox.exe je neplatná, nemôžem vytvoriť prenosný ZIP.")
            
            dosbox_dir = os.path.dirname(dosbox_exe_path)
            
            if zip_štruktúra == 'SUBDIR':
                cilovy_dosbox_dir = os.path.join(zip_base_dir, 'dosbox')
                shutil.copytree(dosbox_dir, cilovy_dosbox_dir, dirs_exist_ok=True) 
                print(f"| ⚙️ Pridaný DOSBox do priečinka 'dosbox' (SUBDIR štruktúra).")
            else: # FLAT
                shutil.copytree(dosbox_dir, zip_base_dir, dirs_exist_ok=True) 
                print(f"| ⚙️ Pridaný DOSBox priamo do koreňa hry (FLAT štruktúra).")
                
            # Overenie a oprava !start.bat 
            bat_cesta_v_zip = os.path.join(zip_base_dir, '!start.bat')
            
            if zip_štruktúra == 'SUBDIR':
                cielova_cesta_pre_bat_v_zip = f'.\\dosbox\\{dosbox_exe_filename}'
            else:
                cielova_cesta_pre_bat_v_zip = f'.\\{dosbox_exe_filename}'
            
            if os.path.exists(bat_cesta_v_zip):
                bat_obsah_zip = f"""
@echo off
rem Spusti DOSBox s konfiguráciou pre aktuálny adresár
rem Cesta k DOSBox.exe je relatívna v rámci archívu (prenosný archív).
"{cielova_cesta_pre_bat_v_zip}" -conf dosbox.conf
                """
                with open(bat_cesta_v_zip, 'w') as f:
                    f.write(bat_obsah_zip.strip())
                print(f"| ⚙️ !start.bat v archíve upravený (cesta: {cielova_cesta_pre_bat_v_zip}).")
            else:
                 print(f"| ⚠️ !start.bat nebol nájdený v archíve. Preskakujem úpravu.")


        # 3. Vytvorenie finálneho archívu
        shutil.make_archive(
            os.path.join(cil_dir, nazov_hry), 
            'zip', 
            root_dir=temp_unique_root, 
            base_dir=nazov_hry 
        )
        print(f"| ✅ Archív vytvorený v: {cil_dir}\\{nazov_hry}.zip")

    except Exception as e:
        raise Exception(f"Chyba pri vytváraní archívu: {e}")
    finally:
        if os.path.exists(temp_unique_root):
             shutil.rmtree(temp_unique_root)


def vymazat_zalohy(nastavenia, cesta='.'):
    """Vymaže len záložné súbory .bak."""
    print(f"\n| 🗑️ Mažem zálohy ({BAK_FILE_EXT})")
    pocet_vymazanych = 0
    for item in os.listdir(cesta):
        if item.endswith(BAK_FILE_EXT):
            try:
                os.remove(os.path.join(cesta, item))
                print(f"| ✅ Vymazaná záloha: {item}")
                pocet_vymazanych += 1
            except Exception as e:
                 raise Exception(f"Chyba pri mazaní zálohy {item}: {e}")
                 
    if pocet_vymazanych == 0:
        print("| ℹ️ Nenašli sa žiadne súbory *.bak na vymazanie.")

def vymazat_konfiguracne_subory(nastavenia, cesta='.'):
    """Vymaže !start.bat, dosbox.conf a zálohy."""
    subory_na_vymazanie = ['!start.bat', 'dosbox.conf']
    
    print(f"\n| 💣 Mažem konfiguráciu")
    
    vymazat_zalohy(nastavenia, cesta)
    
    pocet_vymazanych_konf = 0
    for subor in subory_na_vymazanie:
        cesta_k_suboru = os.path.join(cesta, subor)
        if os.path.exists(cesta_k_suboru):
            try:
                os.remove(cesta_k_suboru)
                print(f"| ✅ Vymazaný súbor: {subor}")
                pocet_vymazanych_konf += 1
            except Exception as e:
                raise Exception(f"Chyba pri mazaní konfiguračného súboru {subor}: {e}")
                
    if pocet_vymazanych_konf == 0:
        print("| ℹ️ Žiadne konfiguračné súbory neboli nájdené na vymazanie.")


# --- MENU FUNKCIE (zostávajú nezmenené) ---

def menu_nastavenia_A(nastavenia):
    """Zobrazuje a spracováva nastavenia ciest a prepínačov s overovaním a novým číslovaním."""
    while True:
        os.system('cls' if os.name == 'nt' else 'clear')
        nastavenia = nacitat_nastavenia() 
        print("\n# NASTAVENIA CIEST A REŽIMOV #")
        print("=============================")
        
        # Zjednotený výpis a kontrola existencie
        status_exe = over_existenciu(nastavenia.get('cesta_k_dosbox_exe'), 'file')
        status_dbgl = over_existenciu(nastavenia.get('cesta_k_DBGL_root'), 'dir')
        status_temp = over_existenciu(nastavenia.get('cesta_k_temp_dir'), 'dir')
        status_zip_dest = over_existenciu(nastavenia.get('cesta_k_zip_dest_dir'), 'dir')
        
        print(f"1. Cesta Emulátora (ABS pre výpočet/kopírovanie) {status_exe}: {nastavenia.get('cesta_k_dosbox_exe')}")
        print(f"2. Cesta DBGL (ABS) {status_dbgl}: {nastavenia.get('cesta_k_DBGL_root')}")
        print(f"3. Temp priečinok pre ZIP (ABS) {status_temp}: {nastavenia.get('cesta_k_temp_dir')}")
        print(f"4. Cieľ ZIP archívov (ABS) {status_zip_dest}: {nastavenia.get('cesta_k_zip_dest_dir')}")
        print(f"5. Prepínač Mount C: {nastavenia.get('zachovat_mount_c')}")
        print(f"6. Režim detekcie: {nastavenia.get('automaticka_detekcia_rezimu')}")
        print(f"7. DOSBox ZIP štruktúra: {nastavenia.get('zip_dosbox_structure')}")
        print("---")
        
        print("1 – Zadajte novú ABSOLÚTNU cestu k DOSBox.exe")
        print("2 – Zadajte novú ABSOLÚTNU cestu ku koreňu DBGL")
        print("3 – Zadajte novú ABSOLÚTNU cestu k TEMP priečinku pre ZIP")
        print("4 – Zadajte novú ABSOLÚTNU cestu k CIEĽOVÉMU priečinku pre ZIP archívy")
        print("5 – Prepínač: Zachovať príkaz MOUNT C ({})".format(nastavenia.get('zachovat_mount_c')))
        print("6 – Prepínač: Automatická Detekcia Režimu ({})".format(nastavenia.get('automaticka_detekcia_rezimu')))
        print("7 – Prepínač: DOSBox ZIP štruktúra ({})".format(nastavenia.get('zip_dosbox_structure')))
        print("Q – Návrat do hlavného menu")
        
        volba = input("\nZadajte voľbu (1-7, Q): ").upper()
        
        if volba == 'Q':
            break
        elif volba == '1':
            nová_cesta = input(f"Zadajte novú ABSOLÚTNU cestu pre DOSBox.exe: ")
            over_a_uloz_cestu('cesta_k_dosbox_exe', nová_cesta, typ='file')
            input("Stlačte Enter pre pokračovanie...")
        elif volba == '2':
            nová_cesta = input(f"Zadajte novú ABSOLÚTNU cestu pre DBGL root: ")
            over_a_uloz_cestu('cesta_k_DBGL_root', nová_cesta, typ='dir')
            input("Stlačte Enter pre pokračovanie...")
        elif volba == '3':
            nová_cesta = input(f"Zadajte novú ABSOLÚTNU cestu pre TEMP priečinok: ")
            over_a_uloz_cestu('cesta_k_temp_dir', nová_cesta, typ='dir')
            input("Stlačte Enter pre pokračovanie...")
        elif volba == '4':
            nová_cesta = input(f"Zadajte novú ABSOLÚTNU cestu pre CIEĽOVÝ ZIP priečinok: ")
            over_a_uloz_cestu('cesta_k_zip_dest_dir', nová_cesta, typ='dir')
            input("Stlačte Enter pre pokračovanie...")
        elif volba == '5':
            nova_hodnota = 'VYPNUTÉ' if nastavenia.get('zachovat_mount_c') == 'ZAPNUTÉ' else 'ZAPNUTÉ'
            ulozit_nastavenie('zachovat_mount_c', nova_hodnota)
            input("Stlačte Enter pre pokračovanie...")
        elif volba == '6':
            nova_hodnota = 'VYPNUTÉ' if nastavenia.get('automaticka_detekcia_rezimu') == 'ZAPNUTÉ' else 'ZAPNUTÉ'
            ulozit_nastavenie('automaticka_detekcia_rezimu', nova_hodnota)
            input("Stlačte Enter pre pokračovanie...")
        elif volba == '7':
            nova_hodnota = 'SUBDIR' if nastavenia.get('zip_dosbox_structure') == 'FLAT' else 'FLAT'
            ulozit_nastavenie('zip_dosbox_structure', nova_hodnota)
            input("Stlačte Enter pre pokračovanie...")
        else:
            print("| ⚠️ Neplatná voľba.")
            input("Stlačte Enter pre pokračovanie...")


def menu_hromadne_operacie(nastavenia, vstup_z_hlavneho_menu=False):
    """
    Spracováva hromadné operácie pre všetky podadresáre.
    """
    
    if os.path.exists(LOG_FILE):
        try:
            os.remove(LOG_FILE)
        except Exception as e:
            print(f"| ⚠️ CHYBA: Nepodarilo sa vymazať starý logovací súbor {LOG_FILE}: {e}")

    def vykonaj_hromadnu_operaciu(funkcia, s_dosboxom=None):
        """Pomocná funkcia pre iteráciu cez podadresáre s logovaním chýb."""
        
        cas_spustenia = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        print(f"\n| 🚀 Spúšťam hromadnú operáciu: {funkcia.__name__} (Čas: {cas_spustenia})")
        
        podadresare = [d for d in os.listdir('.') if os.path.isdir(d) and d.lower() not in KLUC_PRIECINKY and not d.startswith('.')]
        
        if not podadresare:
            print("| ⚠️ Žiadne podadresáre hier na spracovanie.")
            input("Pre návrat stlačte Enter...")
            return

        pocet_chyb = 0
        
        for adr in podadresare:
            print(f"\n--- Práca v adresári: {adr} ---")
            try:
                os.chdir(adr) 
                if s_dosboxom is not None:
                    funkcia(nastavenia, '.', s_dosboxom)
                else:
                    funkcia(nastavenia, '.')
            except Exception as e:
                pocet_chyb += 1
                chyba_sprava = f"KRITICKÁ CHYBA v adresári '{adr}' pri funkcii '{funkcia.__name__}': {e}"
                print(f"| ❌ {chyba_sprava}. Viac info v logu: {LOG_FILE}")
                
                try:
                    s_chybou = f"[{datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] ADRESÁR: {adr}\n  FUNKCIA: {funkcia.__name__}\n  CHYBA: {e}\n{'-'*60}\n"
                    with open(LOG_FILE, 'a', encoding='utf-8') as f:
                        f.write(s_chybou)
                except Exception as log_e:
                    print(f"| ⚠️ CHYBA pri zápise logu: {log_e}")
            finally:
                os.chdir('..') 
                
        print("\n| ✅ Hromadná operácia dokončená.")
        if pocet_chyb > 0:
            print(f"| ⚠️ Nájdite detaily o {pocet_chyb} chybách v súbore {LOG_FILE}.")
        input("Pre návrat stlačte Enter...")


    while True:
        os.system('cls' if os.name == 'nt' else 'clear')
        nastavenia = nacitat_nastavenia() 
        # Zmena názvu programu v hlavičke
        print(f"\n# {NAZOV_PROGRAMU} ({VERZIA}) - REŽIM: BATCH #")
        print("======================================================")
        
        print("| Konfigurácia |")
        print("1 – Vytvoriť základné priečinky (cd, docs, drives/c)")
        print("2 – Vytvoriť/Aktualizovať len !start.bat (Dynamicky relatívna cesta pre USB)")
        print("3 – Vytvoriť/Aktualizovať len dosbox.conf (.conf)")
        print("4 – Vytvoriť/Aktualizovať !start.bat a dosbox.conf (Kompletné)")
        print("---")
        
        print("| Mazanie |")
        print("5 – Vymazať len ZÁLOŽNÉ súbory (.bak)")
        print("6 – Vymazať KONFIGURAČNÉ súbory (!start.bat, dosbox.conf, zálohy)")
        print("---")

        print("| Archivácia |")
        print("7 – Vytvoriť PRENOSNÝ ZIP (S DOSBoxom - Vlastná štruktúra)")
        print("8 – Vytvoriť ČISTÝ ZIP (Bez DOSBoxu - Pre spustenie cez asociáciu .conf)")
        print("---")
        
        print("| Systémové funkcie |")
        print("A – Globálne NASTAVENIA (Cesty, Prepínače)")
        print("X – UKONČIŤ A VYČISTIŤ NÁSTROJ")
        
        if vstup_z_hlavneho_menu:
             print("Q – Návrat do hlavného menu")
        else:
             print("Q – Ukončiť program")
        
        volba = input("\nZadajte voľbu (1-8, A, X, Q): ").upper()

        if volba == 'Q':
            if vstup_z_hlavneho_menu:
                break 
            else:
                sys.exit() 
        elif volba == 'X':
            vycistit_nastroj()
        elif volba == 'A':
            menu_nastavenia_A(nastavenia)
        elif volba == '1':
            vykonaj_hromadnu_operaciu(vytvorit_zakladne_priecinky)
        elif volba == '2':
            vykonaj_hromadnu_operaciu(vytvorit_start_bat)
        elif volba == '3':
            vykonaj_hromadnu_operaciu(vytvorit_dosbox_conf)
        elif volba == '4':
            vykonaj_hromadnu_operaciu(kompletne_nastavenie)
        elif volba == '5':
            vykonaj_hromadnu_operaciu(vymazat_zalohy)
        elif volba == '6':
            vykonaj_hromadnu_operaciu(vymazat_konfiguracne_subory)
        elif volba == '7':
            vykonaj_hromadnu_operaciu(vytvorit_zip_archiv, s_dosboxom=True)
        elif volba == '8':
            vykonaj_hromadnu_operaciu(vytvorit_zip_archiv, s_dosboxom=False)
        else:
            print("| ⚠️ Neplatná voľba.")


def hlavne_menu():
    """Hlavná slučka programu s dynamickou detekciou režimu."""
    while True:
        nastavenia = nacitat_nastavenia()
        
        rezim = 'UNCERTAIN'
        if nastavenia.get('automaticka_detekcia_rezimu') == 'ZAPNUTÉ':
            rezim = detekovat_rezim_prace()

        os.system('cls' if os.name == 'nt' else 'clear')
        
        if rezim == 'BATCH':
            menu_hromadne_operacie(nastavenia, vstup_z_hlavneho_menu=False)
            continue 

        # Zmena názvu programu v hlavičke
        print(f"\n# {NAZOV_PROGRAMU} ({VERZIA}) - REŽIM: {rezim} #")
        print("=======================================================")
        
        if rezim == 'UNCERTAIN':
             print("\n| Režim: Neurčený |")
             print("Tento priečinok neobsahuje konfiguračné súbory hry (SINGLE).")
             print("Ak pracujete so skupinou hier (BATCH), vyberte možnosť 9.")
             print("----------------------------------------------------------------")
        else:
             print("\n| Režim: Práca s aktuálnym priečinkom Hry (SINGLE) |")
             print("----------------------------------------------------------------")


        print("| Konfigurácia |")
        print("1 – Vytvoriť základné priečinky (cd, docs, drives/c)")
        print("2 – Vytvoriť/Aktualizovať len !start.bat (Dynamicky relatívny odkaz pre USB)")
        print("3 – Vytvoriť/Aktualizovať len dosbox.conf (Profil + Úprava)")
        print("4 – Vytvoriť/Aktualizovať !start.bat a dosbox.conf (Kompletné)")
        print("---")
        
        print("| Mazanie |")
        print("5 – Vymazať len ZÁLOŽNÉ súbory (.bak)")
        print("6 – Vymazať KONFIGURAČNÉ súbory (!start.bat, dosbox.conf, zálohy)")
        print("---")
        
        print("| Archivácia |")
        print("7 – Vytvoriť PRENOSNÝ ZIP archív Hry (S DOSBoxom)")
        print("8 – Vytvoriť ČISTÝ ZIP archív Hry (Bez DOSBoxu, pre spustenie cez asociáciu .conf)")
        print("---")

        if rezim == 'UNCERTAIN':
            print("| Systémové funkcie |")
            print("9 – HROMADNÉ OPERÁCIE pre VŠETKY PODADRESÁRE >>")
            print("A – NASTAVENIA: Cesta k emulátoru / Profily / Režimy / ZIP štruktúra")
            print("X – UKONČIŤ A VYČISTIŤ NÁSTROJ")
            print("Q – Ukončiť program")
            volba = input("\nZadajte číslo/písmeno (1-9, A, X, Q): ").upper()
        else:
            print("| Systémové funkcie |")
            print("A – NASTAVENIA: Cesta k emulátoru / Profily / Režimy / ZIP štruktúra")
            print("X – UKONČIŤ A VYČISTIŤ NÁSTROJ")
            print("Q – Ukončiť program")
            volba = input("\nZadajte číslo/písmeno (1-8, A, X, Q): ").upper()

        if volba == 'Q':
            sys.exit()
        elif volba == 'X':
            vycistit_nastroj()
        elif volba == 'A':
            menu_nastavenia_A(nastavenia)
        elif volba == '1':
            try: vytvorit_zakladne_priecinky(nastavenia)
            except Exception as e: print(f"| ❌ CHYBA: {e}")
            input("Pre návrat stlačte Enter...")
        elif volba == '2':
            try: vytvorit_start_bat(nastavenia)
            except Exception as e: print(f"| ❌ CHYBA: {e}")
            input("Pre návrat stlačte Enter...")
        elif volba == '3':
            try: vytvorit_dosbox_conf(nastavenia)
            except Exception as e: print(f"| ❌ CHYBA: {e}")
            input("Pre návrat stlačte Enter...")
        elif volba == '4':
            try: kompletne_nastavenie(nastavenia)
            except Exception as e: print(f"| ❌ CHYBA: {e}")
            input("Pre návrat stlačte Enter...")
        elif volba == '5':
            try: vymazat_zalohy(nastavenia)
            except Exception as e: print(f"| ❌ CHYBA: {e}")
            input("Pre návrat stlačte Enter...")
        elif volba == '6':
            try: vymazat_konfiguracne_subory(nastavenia)
            except Exception as e: print(f"| ❌ CHYBA: {e}")
            input("Pre návrat stlačte Enter...")
        elif volba == '7':
            try: vytvorit_zip_archiv(nastavenia, s_dosboxom=True)
            except Exception as e: print(f"| ❌ CHYBA: {e}")
            input("Pre návrat stlačte Enter...")
        elif volba == '8':
            try: vytvorit_zip_archiv(nastavenia, s_dosboxom=False)
            except Exception as e: print(f"| ❌ CHYBA: {e}")
            input("Pre návrat stlačte Enter...")
        elif volba == '9' and rezim == 'UNCERTAIN':
            # Vstup cez voľbu 9: Q by malo v BATCH menu vrátiť sem
            menu_hromadne_operacie(nastavenia, vstup_z_hlavneho_menu=True)
        else:
            print("| ⚠️ Neplatná voľba. Skúste znova.")
            input("Pre návrat stlačte Enter...")

if __name__ == '__main__':
    hlavne_menu()