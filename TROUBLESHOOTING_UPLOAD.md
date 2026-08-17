# 🔧 Upload Troubleshooting Guide

## Issue: "No data yet" showing on Dashboard

This is **NORMAL** if you haven't uploaded any data yet. Follow these steps:

---

## ✅ Step-by-Step Upload Process

### Step 1: Navigate to Upload Data Page

Look at the **left sidebar** (the navigation menu). You should see:

```
🐄 Farm Analytics
○ 📤 Upload Data
● 📊 Dashboard         ← You are here
○ 🐄 Per-Cow Analysis
○ ⚠️ Health Alerts
○ 📁 Data Table & Export
```

**Click on "📤 Upload Data"** (the first option in the list)

---

### Step 2: Upload a File

You should now see a page titled **"Upload Daily Records"** with:

1. A file uploader button that says **"Browse files"** or **"Drag and drop file here"**
2. Text explaining what file types are accepted (PDF, XLSX, XLS, CSV)

**Click "Browse files"** and select one of these:
- Your actual data file (Excel, CSV, or PDF)
- **OR** the sample file at: `sample_data\sample_test_data.csv` (to test first)

---

### Step 3: Map Columns

After selecting a file, you should see:

1. **"1. Check column mapping"** section with 7 dropdown menus:
   - Date
   - Cow No
   - Code 1
   - Code 2
   - Morning
   - Evening
   - Remark

2. **"2. Review & fix before saving"** section with a data table showing your uploaded data

3. A green button: **"💾 Save to database"**

**Click "💾 Save to database"** to save the data.

---

### Step 4: Verify Success

After clicking Save, you should see a **green success message**:
```
✅ Saved: 20 new rows. Power BI export refreshed.
```

The page will refresh automatically.

---

### Step 5: View Dashboard

Now click **"📊 Dashboard"** in the sidebar.

You should see:
- KPI cards with numbers (Total cows, Total yield, etc.)
- Charts showing milk production trends
- Top 5 and Bottom 5 cows

---

## 🚨 Common Issues & Solutions

### Issue 1: Upload Data page is blank or not showing file uploader

**Cause:** App might have crashed during startup

**Solution:**
1. Check the terminal/command prompt where you ran `streamlit run app.py`
2. Look for any red error messages
3. Press `Ctrl+C` to stop the app
4. Run `streamlit run app.py` again

---

### Issue 2: File uploader shows but nothing happens when I select a file

**Cause:** File might be too large, corrupt, or in wrong format

**Solution:**
1. Try the sample file first: `sample_data\sample_test_data.csv`
2. If sample works but your file doesn't, check your file:
   - Is it actually a CSV/Excel/PDF? (not a Word doc or image)
   - Is the file size < 200MB?
   - Can you open it normally in Excel/Notepad?

---

### Issue 3: I click "Save to database" but nothing happens

**Possible causes:**

**A) No data in the table to save**
- Check if the data table in step 2 has rows
- If empty, your file might not have been parsed correctly

**B) Validation errors**
- Look for **yellow warning messages** or **red error messages** above the Save button
- Fix the issues mentioned (e.g., missing Cow No, negative values)
- Try clicking Save again

**C) App is still processing**
- You should see a spinner that says "Saving..."
- Wait a few seconds
- If it's stuck for >10 seconds, check the terminal for errors

---

### Issue 4: I saved data but Dashboard still shows "No data yet"

**Solutions:**

**Try 1:** Hard refresh the browser
- Press `Ctrl+Shift+R` (Windows)
- Or `Ctrl+F5`

**Try 2:** Check if data was actually saved
1. Go to "📁 Data Table & Export" page
2. If you see data there, the Dashboard should also show it
3. If Data Table is also empty, the save didn't work (see Issue 3)

**Try 3:** Check the database file
1. Close the app (`Ctrl+C` in terminal)
2. Check if `cow_farm.db` file exists in the app folder
3. Check file size (should be > 0 bytes if data was saved)
4. Restart app: `streamlit run app.py`

---

### Issue 5: Error message when uploading

**Common error messages and fixes:**

**"Could not parse file: ..."**
- Your file format isn't readable by the app
- Try exporting your data as CSV instead
- If it's a PDF, make sure it's text-based (not a scanned image)

**"No table detected"**
- For PDFs: Your PDF is likely a scanned image (app can't read those)
- Solution: Export to Excel or CSV instead

**"Validation issues found: Row X Cow Y: ..."**
- These are warnings about data quality
- The app will still save the data (with corrections)
- Review the warnings and fix your source file if needed

---

## 🧪 Test with Sample Data

If you're not sure if the problem is your file or the app, test with the included sample:

1. Click **"📤 Upload Data"**
2. Click **"Browse files"**
3. Navigate to the **`sample_data`** folder inside your `cow_farm_app` folder
4. Select **`sample_test_data.csv`**
5. Click **"💾 Save to database"**

If the sample works:
- ✅ The app is working correctly
- ❌ Your data file has an issue (wrong format, corruption, etc.)

If the sample doesn't work:
- ❌ The app installation has an issue
- Check the terminal for error messages
- Try reinstalling: `pip install --force-reinstall -r requirements.txt`

---

## 🖼️ What You Should See (Visual Checklist)

### On Upload Data Page:

```
┌─────────────────────────────────────┐
│ Upload Daily Records                │
│                                     │
│ Accepts PDF, Excel (.xlsx/.xls)    │
│ or CSV...                           │
│                                     │
│ ┌─────────────────────────────┐   │
│ │  📄 Drag and drop file here │   │
│ │     or Browse files          │   │
│ └─────────────────────────────┘   │
└─────────────────────────────────────┘
```

### After Selecting a File:

```
┌─────────────────────────────────────┐
│ 1. Check column mapping             │
│                                     │
│ Date ▼    Cow No ▼   Code 1 ▼  ... │
└─────────────────────────────────────┘

┌─────────────────────────────────────┐
│ 2. Review & fix before saving       │
│                                     │
│ [Data table with your uploaded data]│
└─────────────────────────────────────┘

┌─────────────────────────────────────┐
│   💾 Save to database               │
└─────────────────────────────────────┘
```

### After Clicking Save:

```
✅ Saved: 20 new rows. Power BI export refreshed.

[Page automatically refreshes and you see the file uploader again]
```

---

## 📞 Still Having Issues?

If none of the above helps, please provide:

1. **Screenshot of the Upload Data page** (so I can see what you're seeing)
2. **Terminal output** (copy the text from the command prompt where you ran the app)
3. **File type** you're trying to upload (CSV? Excel? PDF?)
4. **What happens** when you click the file uploader button

---

## 🔄 Complete Reset (Last Resort)

If nothing works, try a complete reset:

1. **Stop the app:** Press `Ctrl+C` in the terminal
2. **Delete the database:** Delete the file `cow_farm.db` (your data will be lost)
3. **Restart the app:** `streamlit run app.py`
4. **Try uploading sample data** to verify it works

---

**Quick Answer to Your Question:**

The message "No data yet — go to 'Upload Data' first" is correct — it means the database is empty. You need to:

1. Click "📤 Upload Data" in the sidebar
2. Upload a file
3. Click "💾 Save to database"
4. Then go back to Dashboard

The Dashboard **will** show this message until you upload and save data. That's expected behavior for a fresh installation.
