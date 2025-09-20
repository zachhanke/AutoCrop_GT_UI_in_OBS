# README – OBS Auto-Cropper Thingy

### 1. Sarcastic Summary
Take widescreen and make skinny screen. Basically sorcery, but with Python.

---

### 2. Project Title & Description
**Project Name:** OBS Scene Auto-Cropper with Batch Wizardry  

This project combines a **Python script** (`live_shorts_score.py`) and a **Windows Batch file** (`run_shorts_stats.bat`) to automatically:  
- Watch your OBS scene for specific colors in specific spots.  
- If the color matches, crop parts of the scene and save them as updated PNGs.  
- Refresh those images in OBS in real time.  

Translation: It keeps your overlays current without you having to click anything.

---

### 3. Table of Contents
1. [Requirements & Prerequisites](#4-requirements--prerequisites)  
2. [Installation & Setup](#5-installation--setup)  
3. [Usage Instructions](#6-usage-instructions)  
4. [Customization](#7-customization)  
5. [Troubleshooting](#8-troubleshooting)  
6. [Disclaimer](#9-disclaimer)

---

### 4. Requirements & Prerequisites

1. **Python 3.9 or newer**  
   - Download from: [python.org/downloads](https://www.python.org/downloads/)  
   - During installation, **check the box** that says **“Add Python to PATH”**.  
   - Verify install:  
     ```cmd
     python --version
     ```
     Should print something like `Python 3.10.7`.

2. **OBS Studio**  
   - Download from: [obsproject.com](https://obsproject.com/)  
   - Make sure it’s installed and you can open it.

3. **OBS WebSocket**  
   - Built into OBS 28+. If you’re on an older version, install the [obs-websocket plugin](https://github.com/obsproject/obs-websocket).  
   - Go to **Tools → WebSocket Server Settings** in OBS:  
     - Enable it.  
     - Choose a strong password. Write it down.

4. **Python Libraries**  
   Open Command Prompt and run:  
   ```cmd
   pip install obsws-python pillow
   ```

---

### 5. Installation & Setup

1. **Download this project**  
   - Get all files: `live_shorts_score.py`, `run_shorts_stats.bat`, `crop_config_true.txt`, `crop_config_false.txt`.  

2. **Make a folder**  
   Example:  
   ```text
   C:\Users\YourName\Documents\OBS_Scripts
   ```
   Put all the files into that folder.

3. **Navigate to the folder in Command Prompt**  
   ```cmd
   cd C:\Users\YourName\Documents\OBS_Scripts
   ```

4. **Configure OBS WebSocket**  
   - Open OBS → **Tools → WebSocket Server Settings**.  
   - Enable WebSocket server.  
   - Default port is `4455`. Keep that.  
   - Set a password. Use this password in the batch file later.

---

### 6. Usage Instructions

1. **Run the Batch file**  
   - Don’t touch the Python script directly unless you like typing walls of nonsense.  
   - Double-click `run_shorts_stats.bat`.  

2. **Inside the Batch file**  
   Example:
   ```bat
   @echo off
   python live_shorts_score.py --password <obs_websocke_password_here> --source "Golden Tee" --interval 1 --check_x 286 --check_y 125 --check_color 5d1520 --color_tolerance 25 --subcheck_x 1330 --subcheck_y 125 --subcheck_color 123456
   pause
   ```
   - `python live_shorts_score.py`: runs the script.  
   - `--password`: your OBS WebSocket password. This is where you'll enter the password you created earlier.  
   - `--source "Golden Tee"`: the exact name of your OBS source.  
   - `pause`: keeps the window open so you can see error messages.  

3. **What happens**  
   - Script takes a screenshot of your source every 0.25 seconds.  
   - If a certain pixel is the right color → crops defined in `crop_config_true.txt` are saved.  
   - If not, but a secondary check matches → crops in `crop_config_false.txt` are saved.  
   - OBS auto-refreshes those images live.

---

### 7. Customization

1. **Crop Config Files**  
   Format:  
   ```text
   x,y,width,height,output_filename[,image_source_name]
   ```
   Example (`crop_config_true.txt`):  
   ```text
   279,44,355,78,live_score.png,score
   ```
   - Crops a rectangle and saves it to `live_score.png`.  
   - If you include `score` as the 6th value, OBS will update that source automatically.

2. **Python Script Variables** (`live_shorts_score.py`)  
   - `--check_x`, `--check_y`: coordinates of pixel to test.  
   - `--check_color`: hex color code (e.g., `5d1520`).  
   - `--color_tolerance`: wiggle room for color matching (higher = less strict).  
   - `--interval`: how often to check (seconds).  

3. **Batch File**  
   Change command-line arguments to fit your OBS scene names and passwords.

---

### 8. Troubleshooting

- **Error: `python is not recognized`**  
  → You didn’t check “Add Python to PATH.” Reinstall Python or manually add Python to PATH.

- **Error: `No module named 'obsws_python'`**  
  → You skipped the install step. Run:  
  ```cmd
  pip install obsws-python pillow
  ```

- **OBS Connection Failed**  
  - Is OBS running?  
  - Did you enable WebSocket in OBS?  
  - Did you type the right password?  
  - Is the port 4455?  

---

### 9. OBS Settings for Circular Shot Shape
Once you get everything set up, you may want to make your shotshape cutout a circle. To do so, follow these steps in OBS:
  - In OBS, right click on your "shot_shape" source and select 'Filters'  
  - Click the '+' button in the lower-left, and add an "Image Mask/Blend"
  - For the type, select "Alpha Mask (Color Channel)
  - Under path, navigate to the shotshape_crop.png file I made available with the other repo files
  - Leave everything else with the defaults
  - To get everything to fit right, you may need to add a "3D Effect" filter, too
  - Use the various X, Y, and Z sliders to adjust the shape objecct so it fits perfectly within your mask  

---

### 10. Disclaimer
This is provided *as is*. If it sets your computer on fire, makes OBS explode, or causes your dog to start narrating your stream, that’s on you.  
