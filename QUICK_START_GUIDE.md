# 🐄 Cow Farm Analytics - Quick Start Guide

## For First-Time Users

### Step 1: Install and Run (One-Time Setup)

1. Open **Command Prompt** (Windows key + R, type `cmd`, press Enter)

2. Navigate to the app folder:
   ```cmd
   cd "c:\Users\mundr\Downloads\cow_farm_analytics_app (1)\cow_farm_app"
   ```

3. Install required software:
   ```cmd
   pip install -r requirements.txt
   ```
   _(This takes 2-3 minutes the first time)_

4. Start the app:
   ```cmd
   streamlit run app.py
   ```

5. Your web browser will open automatically showing the dashboard

**Note:** If you see warnings about NumPy in the console, ignore them — the app works fine. Or see `SETUP_VENV.md` for a cleaner solution.

---

## Daily Workflow

### Every Day - Upload Your Records

1. **Start the app** (if not already running):
   ```cmd
   cd "c:\Users\mundr\Downloads\cow_farm_analytics_app (1)\cow_farm_app"
   streamlit run app.py
   ```

2. **Click "📤 Upload Data"** in the sidebar

3. **Choose your file:**
   - PDF (must be text-based, not scanned photo)
   - Excel (.xlsx or .xls)
   - CSV

4. **Check the column mapping:**
   - The app guesses which columns are Date, Cow No, Morning, Evening, etc.
   - If wrong, fix using the dropdown menus

5. **Review the data table:**
   - Look for typos, missing values, unusual numbers
   - **You can edit cells directly** by clicking on them
   - Add or delete rows using the buttons

6. **Click "💾 Save to database"**
   - Green success message = saved correctly
   - Yellow warnings = data issues fixed automatically (negative values, etc.)
   - Red errors = fix the problems shown before saving

7. **Done!** Your data is now in the system. Navigate to other pages to see charts and alerts.

---

## Understanding the 5 Pages

### 📤 Upload Data
**When to use:** Every day when you have new milk records

**What you can do:**
- Upload files (PDF/Excel/CSV)
- Map columns if file format is different
- Edit values before saving
- Manually add a single row (bottom of page)

**Tips:**
- If you re-upload the same day's data (e.g., to fix a mistake), the app updates the existing rows — it won't duplicate them
- The app tells you: "X new rows, Y updated rows"

---

### 📊 Dashboard
**When to use:** To see farm-wide performance overview

**What you see:**
- **Top cards:** Total cows, today's yield, average per cow, remark count
- **Farm trend chart:** Daily totals with 7-day and 15-day rolling averages
- **Top 5 / Bottom 5 cows:** Who's producing the most and least
- **Weekly/Monthly summaries:** Total production by week or month (in tabs at bottom)

**Tips:**
- Use the **date range filter** at top to zoom into specific weeks/months
- The rolling averages smooth out daily fluctuations to show real trends
- Bottom 5 cows may need health checks or be nearing dry period

---

### 🐄 Per-Cow Analysis
**When to use:** To investigate a specific cow's performance

**What you see:**
- **Metrics:** Latest total, 7-day average, 15-day average
- **Chart:** Morning, Evening, Total, and both rolling averages over time
- **History table:** Every day's data for this cow with all calculated averages

**Tips:**
- Pick a cow from the dropdown at top
- Watch for sudden drops in the chart — may indicate health issues
- Compare Total (green line) to 7-day average (orange dashed) — if Total drops far below average, check the cow

---

### ⚠️ Health Alerts
**When to use:** Check this page daily to catch problems early

**What you see:**
- **Remark-logged alerts:** Any day you wrote a note (e.g., "mastitis", "limping")
- **Sudden yield drop alerts:** Any day a cow's total fell below 70% of its own 7-day average

**Why it matters:**
- Cows often reduce milk production **before** visible symptoms appear
- Catching mastitis, lameness, or other issues early saves treatment costs
- The 70% threshold is based on research — it catches real problems while avoiding false alarms from normal variation

**Tips:**
- Check this page every morning after uploading data
- Most serious issues show up here 1-2 days before you'd notice them physically

---

### 📁 Data Table & Export
**When to use:** To see all your data, download backups, or update Power BI

**What you see:**
- Full table of every record (sorted newest first)
- **⬇️ Download CSV** button — saves a backup file
- **🔄 Refresh Power BI export file** button — for Power BI users

**Tips:**
- Download CSV backups weekly/monthly as insurance
- If you use Power BI, click "Refresh Power BI export file" after uploading new data, then click "Refresh" in Power BI Desktop

---

## Common Questions

### Q: My PDF file shows "No table detected"
**A:** Your PDF is probably a scanned photo. The app can only read text-based PDFs (e.g., exported from Excel with "Print to PDF"). Solution: Export your sheet as Excel or CSV instead, or use the manual entry form.

### Q: I uploaded wrong data — how do I fix it?
**A:** 
1. Fix your source file (Excel/CSV)
2. Re-upload it
3. The app will **update** the existing rows (not duplicate them)
4. Success message will show "0 new, X updated"

### Q: Can I delete a row?
**A:** Not directly in the web interface (by design, to prevent accidental data loss). Solution:
- Re-upload the file without that row, OR
- Use a SQLite database viewer to edit `cow_farm.db` directly (advanced)

### Q: What if I enter a typo in Cow No — like 15 instead of 1?
**A:** Upload again with the correct cow number. The app sees it as a different cow (since the primary key is Date + Cow No). You can then identify the wrong cow number in the Data Table page and note it's not a real cow.

### Q: How accurate are the rolling averages?
**A:** Very accurate. The 7-day average uses the most recent 7 days of data for that specific cow. The 15-day average uses 15 days. Early in a cow's history (first few days), it uses whatever data exists (minimum 1 day).

### Q: I see NumPy warnings when starting the app
**A:** That's a conflict in your Python environment. The app works fine despite the warnings. For a cleaner experience, see `SETUP_VENV.md` to run the app in its own isolated environment.

---

## Data Entry Tips

### Keep these columns consistent:

- **Date:** Any format works (DD-MM-YYYY, YYYY-MM-DD, etc.) — the app auto-converts
- **Cow No:** Use the same number for the same cow every day
- **Code 1 / Code 2:** Ear tag codes — useful to cross-reference if Cow No changes
- **Morning / Evening:** Litres (decimals are fine: 3.5, 2.7, etc.)
- **Remark:** Optional — write notes like "mastitis", "limping", "not eating" when you see issues

### What the app checks for you:

✅ Negative Morning/Evening values → auto-corrected to 0 with warning  
✅ Non-numeric Morning/Evening → defaults to 0 with error message  
✅ Suspiciously high values (>30L) → warning to double-check  
✅ Missing Cow No → rejected (you must have a cow number)  
✅ Invalid dates → skipped with notification  

---

## Stopping the App

When you're done for the day:

1. Go to the **Command Prompt** where you ran `streamlit run app.py`
2. Press **Ctrl+C** (this stops the app)
3. Close the browser tab
4. Your data is saved in `cow_farm.db` — it will be there next time you start the app

---

## Getting Help

1. **Blank page / app crash:** Check the Command Prompt window for red error messages
2. **Data not showing:** Make sure you clicked "💾 Save to database" after uploading
3. **Charts are empty:** You need at least 1 day of data uploaded first
4. **Technical issues:** See `README.md` or `CHANGELOG.md` for detailed troubleshooting

---

## Sample Data (For Testing)

The app includes sample data in `sample_data/sample_test_data.csv` — 20 cows, 1 day of records, including one with a "mastitis" remark. Use this to test the app before entering your real data.

To load it:
1. Go to **📤 Upload Data**
2. Click the file uploader
3. Select `sample_data\sample_test_data.csv`
4. Review the mapping (should auto-detect correctly)
5. Click **💾 Save to database**
6. Navigate to other pages to see charts and alerts populated

---

**Need more help?** See the full README.md or CHANGELOG.md files in the app folder.

**Happy farming! 🐄🥛**
