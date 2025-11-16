# THE BATCH (DOS)BOX(ER) (v1.0)
Programátor: AI  -----   PromptMaster: TomasKrs

<img width="834" height="447" alt="obrázok" src="https://github.com/user-attachments/assets/96c6a176-92a0-401c-bf7b-307b363a1ad0" />
<img width="759" height="447" alt="obrázok" src="https://github.com/user-attachments/assets/7c8273aa-9406-4e59-a067-b1bb08d7e870" />

## Účel programu

**The Batch (DOS)Box(er)** je skript určený na **automatizáciu konfigurácie a správy hier** emulovaných prostredníctvom DOSBoxu. Je navrhnutý špeciálne pre centralizované a **prenosné (portable)** kolekcie hier (napr. na USB disku) a pre spoluprácu s manažérmi profilov ako je DBGL (DOSBox Game Launcher).

Hlavnou úlohou je pretransformovať absolútne cesty v konfigurácii DBGL (ktoré sú viazané na konkrétny PC) na **relatívne cesty**. Tým sa zabezpečí, že hry budú spustiteľné priamo z ich priečinka prostredníctvom vlastného spúšťacieho skriptu (`!start.bat`) bez ohľadu na to, na akom disku alebo v akom adresári sa centrálny DOSBox nachádza.

Program pracuje v dvoch hlavných režimoch:
1.  **SINGLE:** Práca s aktuálnym priečinkom hry.
2.  **BATCH:** Hromadná práca so všetkými podadresármi (hrami) naraz.

---

## 💻 Štruktúra Menu a Funkcie

Program sa automaticky spustí v režime **SINGLE**, **BATCH** alebo **UNCERTAIN** (neurčený) v závislosti od obsahu aktuálneho priečinka (ak je zapnutá automatická detekcia).

### A. Globálne Nastavenia (Voľba A)

Nastavenia slúžia na definovanie kritických ciest a správania nástroja. Všetky cesty sú priebežne overované na existenciu.

| # | Nastavenie | Typ | Popis |
| :---: | :--- | :--- | :--- |
| **1** | Cesta k DOSBox.exe | Cesta k súboru | Absolútna cesta k centrálnemu DOSBox.exe. **Kľúčové pre výpočet relatívnej cesty v `!start.bat`.** |
| **2** | Cesta ku koreňu DBGL | Cesta k priečinku | Absolútna cesta k hlavnému priečinku DBGL, kde sa nachádza adresár `profiles/`. |
| **3** | Temp priečinok pre ZIP | Cesta k priečinku | Dočasný adresár, ktorý sa používa pri vytváraní ZIP archívov. |
| **4** | Cieľ ZIP archívov | Cesta k priečinku | Priečinok, kam sa ukladajú výsledné ZIP archívy. |
| **5** | Prepínač Mount C | ZAPNUTÉ/VYPNUTÉ | Ak je `VYPNUTÉ`, príkaz `MOUNT C` sa odstráni z `dosbox.conf`, čo je typické, ak chcete mať len `MOUNT D` (CD-ROM). |
| **6** | Automatická Detekcia Režimu | ZAPNUTÉ/VYPNUTÉ | Definuje, či program pri štarte automaticky určí režim (SINGLE/BATCH). |
| **7** | DOSBox ZIP štruktúra | FLAT/SUBDIR | Definuje, ako sa vloží centrálny DOSBox do prenosného ZIP archívu: `FLAT` (do koreňa hry) alebo `SUBDIR` (do podpriečinka `dosbox/`). |

### B. SINGLE Režim (Práca s aktuálnym priečinkom)

| # | Funkcia | Popis |
| :---: | :--- | :--- |
| **1** | Vytvoriť základné priečinky | Vytvorí štruktúru: `cd/`, `docs/`, `drives/c/`. |
| **2** | Vytvoriť/Aktualizovať len `!start.bat` | Vytvorí lokálny BAT súbor, ktorý volá centrálny DOSBox.exe pomocou **dynamickej relatívnej cesty**. |
| **3** | Vytvoriť/Aktualizovať len `dosbox.conf` | **Vyhľadá DBGL profil** podľa MOUNT C cesty, skopíruje ho ako `dosbox.conf` a **relativizuje všetky MOUNT a IMGMOUNT cesty** na základe lokálnej štruktúry. |
| **4** | Kompletné nastavenie | Kombinuje 1, 2 a 3. |
| **5** | Vymazať zálohy | Vymaže súbory s príponou `.bak`. |
| **6** | Vymazať konfiguráciu | Vymaže `!start.bat`, `dosbox.conf` a `.bak` súbory. |
| **7** | Vytvoriť PRENOSNÝ ZIP | Vytvorí archív s hrou **vrátane kópie DOSBoxu** (podľa štruktúry FLAT/SUBDIR) a upraveným `!start.bat`. |
| **8** | Vytvoriť ČISTÝ ZIP | Vytvorí archív s hrou **bez DOSBoxu** (určené pre spustenie cez asociáciu .conf). |
| **9** | HROMADNÉ OPERÁCIE (Len v UNCERTAIN režime) | Prepnutie do BATCH režimu. |

### C. BATCH Režim (Hromadné Operácie)

Všetky funkcie 1 až 8 vykonávajú rovnakú operáciu ako v SINGLE režime, ale aplikujú ju na **všetky podadresáre** (ktoré nie sú kľúčové pre nástroj) v aktuálnom priečinku.

V prípade chýb je generovaný logovací súbor `hromadne_operacie_log.txt`.

---

## 🎯 Príklady použitia na hrách

Predpokladajme, že máte tisíce profilov v DBGL a štruktúru hlavného priečinka:

Hry_DOS/ ├── Doom/ ├── Warcraft_II/ ├── Dungeons_and_Dragons/ └── dosbox_tool.py


### Príklad 1: Príprava jednej hry (SINGLE)

Chceme hru *Warcraft II* plne prenosnú na USB.

1.  **Prejdite do adresára hry:** `cd Warcraft_II`
2.  **Spustite program:** `python dosbox_tool.py` (Program sa spustí v SINGLE režime).
3.  **Nastavte všetko naraz:** Zvoľte **4 – Vytvoriť/Aktualizovať !start.bat a dosbox.conf (Kompletné)**.
    * *Výsledok:* V priečinku `Warcraft_II` sa vytvorí `drives/c/`, `!start.bat` s relatívnou cestou k centrálnemu DOSBoxu a `dosbox.conf` s relativizovanými cestami MOUNT/IMGMOUNT.

### Príklad 2: Hromadná konverzia na Portable (BATCH)

Chceme všetky hry v priečinku `Hry_DOS` konvertovať na prenosné jedným príkazom.

1.  **Prejdite do koreňového adresára:** `cd Hry_DOS`
2.  **Spustite program:** `python dosbox_tool.py` (Program sa spustí v BATCH režime, ak má 2+ podadresáre).
3.  **Spustite hromadnú akciu:** Zvoľte **4 – Vytvoriť/Aktualizovať !start.bat a dosbox.conf (Kompletné)**.
    * *Výsledok:* Program prejde do adresárov `Doom/`, `Warcraft_II/` a `Dungeons_and_Dragons/` a v každom z nich vykoná **kompletné nastavenie**, čím ich pripraví na spustenie cez lokálny `!start.bat`.

### Príklad 3: Vytvorenie Prenosného ZIP pre distribúciu

Chceme hru *Doom* zdieľať aj s kópiou DOSBoxu, aby ju mohol spustiť ktokoľvek.

1.  **Prejdite do adresára hry:** `cd Doom`
2.  **Spustite program a zvoľte:** **7 – Vytvoriť PRENOSNÝ ZIP archív Hry (S DOSBoxom)**.
    * *Výsledok:* V cieľovom ZIP priečinku (`cesta_k_zip_dest_dir` z Nastavení) vznikne `Doom.zip`, ktorý
