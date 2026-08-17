# Setting Up a Virtual Environment (Recommended)

If you're seeing NumPy version conflicts or import errors with bottleneck/xarray/numexpr, the cleanest solution is to run this app in its own isolated Python environment.

## Why Use a Virtual Environment?

Your Anaconda base environment has NumPy 2.x installed, but some packages (bottleneck, numexpr, xarray) were compiled for NumPy 1.x. This causes import-time crashes. A virtual environment gives this app its own clean set of packages that won't conflict with your Anaconda setup.

## Setup Steps (Windows)

### 1. Open Command Prompt or PowerShell

Navigate to the cow_farm_app folder:

```cmd
cd "c:\Users\mundr\Downloads\cow_farm_analytics_app (1)\cow_farm_app"
```

### 2. Create a virtual environment

```cmd
python -m venv venv
```

This creates a `venv` folder with a fresh Python installation.

### 3. Activate the virtual environment

**In Command Prompt:**
```cmd
venv\Scripts\activate.bat
```

**In PowerShell:**
```powershell
venv\Scripts\Activate.ps1
```

Your prompt should now show `(venv)` at the beginning.

### 4. Install dependencies

```cmd
pip install -r requirements.txt
```

This installs the exact versions specified in requirements.txt, including NumPy < 2.0.

### 5. Run the app

```cmd
streamlit run app.py
```

Your browser will open at http://localhost:8501

## Daily Usage

Every time you want to run the app:

1. Open Command Prompt/PowerShell
2. Navigate to the app folder
3. Activate the virtual environment: `venv\Scripts\activate.bat` (or `.ps1` for PowerShell)
4. Run: `streamlit run app.py`

## Deactivating

When you're done, type:

```cmd
deactivate
```

This returns you to your normal Anaconda environment.

## Alternative: Continue Using Anaconda Base

If you prefer not to use a virtual environment, the app will still run despite the NumPy warnings. The warnings appear during import but don't actually break functionality (we removed the plotly.express dependency that was pulling in xarray). The app works fine with the warnings printed to console.

## Troubleshooting

**PowerShell execution policy error:**
If activating in PowerShell gives a script execution error, run this once:
```powershell
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
```

**"python not found":**
Your Anaconda Python is accessible, so this shouldn't happen. If it does, use:
```cmd
C:\Users\mundr\anaconda3\python.exe -m venv venv
```
