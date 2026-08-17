# Cow Farm Milk Analytics — Local Web App

A local dashboard for your daily milk record sheets (Date, Cow No, Code 1, Code 2,
Morning, Evening, Remark). Upload a PDF, Excel or CSV each day and it builds
trends, 7-day/15-day rolling averages per cow, farm totals, and health/yield
alerts (e.g. mastitis remarks, sudden drops in yield).

Everything runs **only on your computer** — no data leaves your machine.
Records accumulate in a local file `cow_farm.db` (SQLite) each time you upload.

---

## 🚀 Quick Start for Non-Technical Users

**Want to get started in 2 minutes?** See **[EASY_SETUP.md](EASY_SETUP.md)** for simple copy-paste commands!

### Super Easy Method (Windows):
1. Clone this repository
2. Double-click `setup_and_run.bat`
3. Open browser to http://localhost:5000

### Super Easy Method (Mac/Linux):
1. Clone this repository
2. Open Terminal, navigate to this folder
3. Run: `bash setup_and_run.sh`
4. Open browser to http://localhost:5000

---

## 📋 Complete Setup Instructions

### Quick Clone and Run Commands

**For Windows:**
```cmd
git clone https://github.com/Adityamundra04/Cow_analyzer.git
cd Cow_analyzer
setup_and_run.bat
```

**For Mac/Linux:**
```bash
git clone https://github.com/Adityamundra04/Cow_analyzer.git
cd Cow_analyzer
bash setup_and_run.sh
```

Then open your browser to **http://localhost:5000**

### Manual Setup (if you prefer)

You need **Python 3.9+** installed. Then, in this folder, run:

```bash
pip install -r requirements.txt
```

**Recommended:** Use a virtual environment to avoid package conflicts:

```bash
python -m venv venv
venv\Scripts\activate    # Windows
source venv/bin/activate # Mac/Linux
pip install -r requirements.txt
```

## 2. Run the app

```bash
python app.py
```

Your browser should open automatically at **http://localhost:5000**.
To stop the app, go back to the terminal and press `Ctrl+C`.
Run the same command again any day to reopen it — your saved data stays in `cow_farm.db`.

## 3. Using it

- **📤 Upload Data** — drop in a PDF/Excel/CSV of the day's sheet. If the file's
  column names don't exactly match, you'll get a quick dropdown to map each
  column (Date, Cow No, Code 1, Code 2, Morning, Evening, Remark) — then a
  table to review/fix values before saving. The app validates data and warns
  about negative values, missing cow numbers, or suspiciously high yields (>30L).
  You can also add a single row by hand from the same page.
  
- **📊 Dashboard** — farm-wide totals, 7-day/15-day trend line, best/worst
  performing cows, plus weekly/monthly summaries showing total production by
  period for the whole farm and individual cows.
  
- **🐄 Per-Cow Analysis** — pick a cow, see its morning/evening/total history
  with 7-day and 15-day rolling averages, full row-by-row table.
  
- **⚠️ Health Alerts** — auto-flags any day a cow's yield fell below 70% of its
  own 7-day average, plus every row that has a Remark (e.g. "mastitis").
  
- **📁 Data Table & Export** — full table, CSV download, and a button to
  refresh the Power BI export file (see below).

## 4. Data Validation

The app now validates your data before saving:
- **Missing Cow No**: Rows without a valid cow number are rejected
- **Negative values**: Morning/Evening values cannot be negative (auto-corrected to 0)
- **Suspiciously high values**: Values >30L trigger a warning to verify accuracy
- **Non-numeric values**: Text in Morning/Evening columns is flagged and defaults to 0
- **Update tracking**: When re-uploading data, the app shows how many rows were new vs updated

## 5. Notes on PDF uploads

PDF table extraction works well for **text-based PDFs** (e.g. exported from
Excel, a farm-management app, or "Print to PDF"). It will **not** read a
**scanned photo/image** turned into a PDF — for those, re-type or export the
sheet as Excel/CSV instead, or use the manual-entry form. This is why the
Upload page always shows you a preview/fix step before saving.

## 6. Power BI

See `powerbi/PowerBI_Setup_Guide.md`. In short: click "Refresh Power BI export
file" on the Data Table page — this writes `powerbi/cow_data_export.csv`,
which you point Power BI Desktop at as its data source. Each time you add new
days of data, refresh the export in the app, then hit "Refresh" in Power BI.

## 7. Troubleshooting

**Blank/white page after saving**: This usually means a validation error occurred.
Check the terminal where you ran `streamlit run app.py` for error messages. The
app now catches most common errors and displays them on-screen.

**NumPy version conflicts**: If you see import errors about xarray or bottleneck,
run the app in a virtual environment (see Install section above). The
requirements.txt now pins NumPy < 2.0 to prevent compatibility issues.
