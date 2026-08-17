# Easy Setup Guide for Non-Technical Users

## For Windows Users

### Step 1: Install Python
1. Download Python from https://www.python.org/downloads/
2. Run the installer and **CHECK** the box that says "Add Python to PATH"
3. Click "Install Now"

### Step 2: Open Command Prompt
1. Press `Windows Key + R`
2. Type `cmd` and press Enter

### Step 3: Run These Commands (Copy and Paste)
```cmd
cd Desktop
git clone https://github.com/Adityamundra04/Cow_analyzer.git
cd Cow_analyzer
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
python app.py
```

### Step 4: Open the App
After running the commands, you'll see a message like:
```
Running on http://127.0.0.1:5000
```
Open your web browser and go to: **http://localhost:5000**

---

## For Mac/Linux Users

### Step 1: Install Python
- **Mac**: Python is usually pre-installed. If not, download from https://www.python.org/downloads/
- **Linux**: Run `sudo apt-get install python3 python3-pip python3-venv`

### Step 2: Open Terminal
- **Mac**: Press `Cmd + Space`, type "Terminal", press Enter
- **Linux**: Press `Ctrl + Alt + T`

### Step 3: Run These Commands (Copy and Paste)
```bash
cd Desktop
git clone https://github.com/Adityamundra04/Cow_analyzer.git
cd Cow_analyzer
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
python app.py
```

### Step 4: Open the App
Open your web browser and go to: **http://localhost:5000**

---

## To Run the App Again (After First Setup)

### Windows:
```cmd
cd Desktop\Cow_analyzer
venv\Scripts\activate
python app.py
```

### Mac/Linux:
```bash
cd Desktop/Cow_analyzer
source venv/bin/activate
python app.py
```

---

## Troubleshooting

**Problem**: "git is not recognized"
- **Solution**: Install Git from https://git-scm.com/downloads

**Problem**: "python is not recognized"
- **Solution**: Reinstall Python and make sure to check "Add Python to PATH"

**Problem**: Port 5000 already in use
- **Solution**: Close any other programs using port 5000, or edit `app.py` and change the port number

---

## What Does This App Do?
This is a Cow Farm Analytics Application that helps you:
- Upload and manage cow data from Excel files
- View analytics and statistics
- Track cow health and production
- Export data for Power BI reports
