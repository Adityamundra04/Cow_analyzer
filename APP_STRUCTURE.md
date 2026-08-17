# 🗺️ Cow Farm Analytics App - Structure Guide

## File Organization

```
cow_farm_app/
│
├── app.py                          # Main application (all pages, logic)
├── cow_farm.db                     # SQLite database (auto-created, persists data)
├── requirements.txt                # Python dependencies
│
├── README.md                       # Technical installation guide
├── QUICK_START_GUIDE.md           # User-friendly daily usage guide
├── SETUP_VENV.md                  # Virtual environment setup
├── CHANGELOG.md                   # Detailed list of all changes
├── PROJECT_COMPLETION_SUMMARY.md  # Executive summary
├── APP_STRUCTURE.md               # This file
├── test_validation.py             # Automated test suite
│
├── sample_data/
│   ├── cow_data_template.xlsx     # Blank template with headers
│   └── sample_test_data.csv       # 20 sample rows for testing
│
└── powerbi/
    ├── PowerBI_Setup_Guide.md     # Manual Power BI setup steps
    ├── DAX_measures.txt           # Copy-paste DAX formulas
    └── cow_data_export.csv        # Generated export (created at runtime)
```

---

## Application Architecture

### Technology Stack

```
Frontend: Streamlit (Python web framework)
Backend: Python 3.9+
Database: SQLite (local file)
Charts: Plotly (graph_objects only)
Data: Pandas (DataFrame manipulation)
Parsers: pdfplumber (PDF), openpyxl (Excel)
```

### Data Flow

```
[User's File]
    ↓
[File Uploader] → Parse (PDF/Excel/CSV)
    ↓
[Column Mapper] → Auto-detect or manual selection
    ↓
[Data Editor] → Review and edit values
    ↓
[Validation] → Check for errors, warnings
    ↓
[SQLite Database] ← Upsert (INSERT or UPDATE)
    ↓
[Power BI Export] → Regenerate CSV file
    ↓
[All Pages] ← Load data for display
```

---

## Database Schema

### Table: `records`

| Column  | Type    | Nullable | Description                        |
|---------|---------|----------|------------------------------------|
| date    | TEXT    | NOT NULL | Date in YYYY-MM-DD format          |
| cow_no  | INTEGER | NOT NULL | Cow identifier (1, 2, 3, ...)      |
| code1   | TEXT    | YES      | Ear tag code 1 (alphanumeric)      |
| code2   | TEXT    | YES      | Ear tag code 2 (usually numeric)   |
| morning | REAL    | YES      | Morning milk yield (litres)        |
| evening | REAL    | YES      | Evening milk yield (litres)        |
| remark  | TEXT    | YES      | Optional health note               |

**Primary Key:** `(date, cow_no)`  
**Constraint:** Prevents duplicate entries for the same cow on the same day  
**Upsert Behavior:** If (date, cow_no) exists, UPDATE; otherwise INSERT

---

## Page Breakdown

### 📤 Upload Data

**Purpose:** Ingest daily milk records

**Components:**
1. File uploader (PDF/Excel/CSV)
2. Column mapper (7 dropdown menus)
3. Data editor (spreadsheet-like table)
4. Save button
5. Manual single-row entry form (collapsed by default)

**Validation Performed:**
- Date parsing and conversion
- Cow No presence and numeric check
- Morning/Evening numeric conversion with error handling
- Negative value detection and auto-correction
- High value warning (>30L)
- Update vs insert tracking

**Output:**
- Success message: "X new rows, Y updated rows"
- Warning messages: List of validation issues
- Auto-triggers Power BI export refresh

---

### 📊 Dashboard

**Purpose:** Farm-wide performance overview

**Components:**
1. Date range filter (2-date picker)
2. KPI cards (4 metrics)
   - Total cows recorded
   - Latest day's total yield
   - Average yield per cow
   - Remarks count today
3. Farm-wide trend line chart
   - Daily total (green line)
   - 7-day rolling avg (orange dashed)
   - 15-day rolling avg (blue dotted)
4. Top 5 cows bar chart
5. Bottom 5 cows bar chart
6. Period summaries (tabs)
   - Weekly summary tables
   - Monthly summary tables

**Calculations:**
```python
# Daily totals
daily_totals = df.groupby("date")["total"].sum()

# Rolling averages (per day)
daily_totals["avg_7d"] = daily_totals.rolling(7, min_periods=1).mean()
daily_totals["avg_15d"] = daily_totals.rolling(15, min_periods=1).mean()

# Top/Bottom performers
avg_per_cow = df.groupby("cow_no")["total"].mean().sort_values()
```

---

### 🐄 Per-Cow Analysis

**Purpose:** Deep dive into individual cow performance

**Components:**
1. Cow selector (dropdown)
2. Latest metrics (3 cards)
   - Latest total
   - 7-day average
   - 15-day average
3. Multi-line time series chart
   - Morning (light green)
   - Evening (blue)
   - Total (dark green, thick line)
   - 7-day avg (orange dashed)
   - 15-day avg (red dotted)
4. Full history table (all columns, sortable)

**Calculations:**
```python
# Per cow, sorted by date
cow_data = df[df["cow_no"] == selected_cow].sort_values("date")

# Rolling averages (per cow)
cow_data["avg_7d"] = cow_data["total"].rolling(7, min_periods=1).mean()
cow_data["avg_15d"] = cow_data["total"].rolling(15, min_periods=1).mean()
```

---

### ⚠️ Health Alerts

**Purpose:** Early detection of health issues

**Alert Types:**

1. **Remark-Logged Alerts**
   - Any row with non-blank remark text
   - Examples: "mastitis", "limping", "not eating"

2. **Sudden Yield Drop Alerts**
   - Condition: `today's total < (7-day avg * 0.7)`
   - Per-cow basis (each cow compared to own history)
   - 30% drop threshold based on research

**Display:**
- Sorted newest first
- Styled as colored alert cards
- Shows: date, cow number, alert type, detail message

**Algorithm:**
```python
for each cow:
    calculate 7-day rolling average
    shift by 1 day to get "previous" average
    for each day:
        if total < (prev_avg * 0.7):
            flag as "Sudden yield drop"
    
    for each row with remark:
        flag as "Remark logged"
```

---

### 📁 Data Table & Export

**Purpose:** Raw data access and Power BI integration

**Components:**
1. Full data table (sortable, filterable by Streamlit)
2. Download CSV button (in-browser download)
3. Refresh Power BI export button (writes file to disk)

**Export Schema (cow_data_export.csv):**
```
date,cow_no,code1,code2,morning,evening,remark,total
2026-07-17,1,25C,1111857,3.3,3.2,,6.5
2026-07-17,2,25C,1111878,1.2,1.0,,2.2
...
```

**Note:** The export includes a `total` column (morning + evening) pre-calculated for Power BI convenience.

---

## Key Functions Reference

### Database Functions

```python
def get_conn()
    # Creates connection to SQLite
    # Auto-creates records table if not exists
    # Returns: sqlite3.Connection object

def upsert_records(df: pd.DataFrame)
    # Validates and inserts/updates records
    # Returns: (new_count, updated_count, errors_list)
    # Key validations:
    #   - Date parsing
    #   - Cow No presence and type
    #   - Morning/Evening numeric conversion
    #   - Negative value correction
    #   - High value warning

def load_all() -> pd.DataFrame
    # Loads all records from database
    # Calculates total = morning + evening
    # Returns: DataFrame with all historical data

def export_for_powerbi(df: pd.DataFrame)
    # Writes cow_data_export.csv for Power BI
    # Formats dates as YYYY-MM-DD
    # Includes total column
```

### Parser Functions

```python
def parse_pdf(file) -> pd.DataFrame
    # Uses pdfplumber to extract tables
    # Only works on text-based PDFs (not scanned images)
    # Returns: DataFrame or empty if no tables found

def parse_excel(file) -> pd.DataFrame
    # Uses pandas.read_excel() with openpyxl
    # Supports .xlsx and .xls
    # Returns: DataFrame

def parse_csv(file) -> pd.DataFrame
    # Uses pandas.read_csv()
    # Auto-detects encoding and separators
    # Returns: DataFrame

def guess_column_map(raw_cols)
    # Fuzzy matches source columns to standard columns
    # Uses keyword matching (case-insensitive, space-flexible)
    # Returns: dict mapping standard → source column names
```

### Analytics Functions

```python
def add_rolling(df_cow: pd.DataFrame) -> pd.DataFrame
    # Adds 7-day and 15-day rolling averages
    # Input: Single cow's data, sorted by date
    # Returns: Same DataFrame with avg_7d and avg_15d columns

def build_alerts(df: pd.DataFrame) -> pd.DataFrame
    # Detects remark-logged and yield-drop alerts
    # Per-cow analysis with 70% threshold
    # Returns: DataFrame of alerts, sorted by date DESC
```

---

## Error Handling Strategy

### Layer 1: File Parsing
```python
try:
    raw = parse_pdf(file)
except Exception as e:
    st.error(f"Could not parse file: {e}")
    # User sees error, can try different file
```

### Layer 2: Data Validation
```python
# In upsert_records():
errors = []
for each row:
    try:
        validate_cow_no()
        validate_morning()
        validate_evening()
    except Exception as e:
        errors.append(f"Row {i}: {e}")

# Show all errors to user at once
if errors:
    st.warning(f"{len(errors)} validation issues found:")
    for err in errors:
        st.warning(f"• {err}")
```

### Layer 3: Page Display
```python
# Before calculations:
if df.empty:
    st.info("No data yet — go to Upload Data first.")
else:
    # Safe to proceed with calculations
```

### Layer 4: Index Access
```python
# Instead of: value = df.iloc[-1]
# Use:
if len(df) > 0:
    value = df.iloc[-1]
else:
    value = 0.0  # Safe default
```

---

## Rolling Average Implementation

### Why Rolling Averages?

- **Smooths daily fluctuations:** A cow might produce less one day due to stress, weather, feed changes
- **Reveals true trends:** 7-day shows short-term, 15-day shows medium-term
- **Enables anomaly detection:** Compare today to 7-day average → catches sudden drops

### Calculation Method

```python
# Pandas built-in rolling window
df["avg_7d"] = df["total"].rolling(7, min_periods=1).mean()

# What this does:
# Day 1: avg_7d = mean of [day1]           (only 1 value)
# Day 2: avg_7d = mean of [day1, day2]     (only 2 values)
# ...
# Day 7: avg_7d = mean of [day1...day7]    (full window)
# Day 8: avg_7d = mean of [day2...day8]    (slides forward)
```

### Per-Cow vs Farm-Wide

- **Per-Cow:** Each cow's rolling avg calculated separately (different baselines)
- **Farm-Wide:** Sum all cows per day, then rolling avg on farm totals
- **Why separate?** A naturally high-yielding cow's "normal" is different from a low-yielding cow's "normal"

---

## Health Alert Logic

### Remark-Logged Alerts

Simple: Any row where `remark` column is not NULL and not empty string.

```python
remarked = df[df["remark"].notna() & (df["remark"].str.strip() != "")]
```

### Yield Drop Alerts

**Threshold:** Today's total < 70% of previous 7-day average

**Why 70%?**
- Research shows mastitis/illness often causes 30-50% production drop
- 30% threshold catches real problems while avoiding false alarms from normal variation
- "Previous" 7-day average excludes today (looks at prior week)

**Implementation:**
```python
# Per cow:
cow_data = cow_data.sort_values("date")
cow_data["avg_7d"] = cow_data["total"].rolling(7, min_periods=1).mean()
cow_data["prev_avg_7d"] = cow_data["avg_7d"].shift(1)  # Yesterday's 7-day avg

# Flag drops:
drops = cow_data[
    (cow_data["prev_avg_7d"] > 0) &  # Avoid division by zero
    (cow_data["total"] < cow_data["prev_avg_7d"] * 0.7)
]
```

**Edge Cases Handled:**
- First 7 days: Uses whatever data exists (no false positives)
- Zero-yield days: Only alerts if previous average was > 0
- Dry cows: If consistently 0, no alerts (since prev_avg = 0)

---

## Power BI Integration

### Export File Format

**Location:** `powerbi/cow_data_export.csv`

**Schema:**
```csv
date,cow_no,code1,code2,morning,evening,remark,total
2026-07-17,1,25C,1111857,3.3,3.2,,6.5
```

**Key Points:**
- Date format: YYYY-MM-DD (Power BI's preferred date format)
- Total column: Pre-calculated (morning + evening)
- Null remarks: Empty string (not "None" or "nan")

### Usage in Power BI

1. **Get Data** → **Text/CSV** → Select `cow_data_export.csv`
2. **Transform Data** → Set date column type to Date
3. **Create measures** using DAX formulas from `DAX_measures.txt`
4. **Build visuals** as described in `PowerBI_Setup_Guide.md`
5. **Refresh:** Click "Refresh" in Power BI after updating export in web app

---

## Configuration

### No Config Files

This app is designed to be zero-config:
- Database path: Hardcoded relative to app.py
- No API keys needed
- No environment variables
- No external services

### Customization Points (if needed)

In `app.py`, lines 14-17:
```python
APP_DIR = os.path.dirname(os.path.abspath(__file__))
DB_PATH = os.path.join(APP_DIR, "cow_farm.db")
POWERBI_CSV_PATH = os.path.join(APP_DIR, "powerbi", "cow_data_export.csv")
STANDARD_COLS = ["Date", "Cow No", "Code 1", "Code 2", "Morning", "Evening", "Remark"]
```

Change these if you want different paths or column names (though changing column names would break existing functionality).

---

## Performance Considerations

### Database Size

SQLite handles millions of rows easily. With typical farm data:
- 50 cows × 2 records/day × 365 days = ~36,500 rows/year
- SQLite can handle this with no performance issues

### Chart Rendering

Plotly handles up to ~10,000 points smoothly. If you have:
- 5 years of data
- Daily records
- Single cow chart: ~1,800 points ✓ Fast
- Farm-wide chart: ~1,800 points ✓ Fast

### Query Optimization

All queries are simple:
- `SELECT * FROM records ORDER BY date, cow_no` — fast with proper index
- Primary key (date, cow_no) is automatically indexed
- No complex joins or subqueries

---

## Security Considerations

### Local-Only Design

- **No network calls:** All processing happens locally
- **No authentication:** Not needed (single-user, local app)
- **No cloud storage:** Data stays on your computer

### SQL Injection Protection

Uses parameterized queries:
```python
cur.execute("INSERT INTO records ... VALUES (?, ?, ?)", (val1, val2, val3))
# NOT: cur.execute(f"INSERT ... VALUES ({val1}, {val2}, {val3})")
```

### File Upload Safety

- Only accepts known types: PDF, XLSX, XLS, CSV
- Parsers handle corrupt files gracefully (no code execution risk)
- User reviews data before committing to database

---

## Troubleshooting Guide

### Common Issues

| Symptom | Cause | Solution |
|---------|-------|----------|
| Blank page | Old bug (now fixed) | Use updated app.py |
| NumPy warnings | Anaconda base env conflict | See SETUP_VENV.md |
| "No table detected" | Scanned PDF | Export as Excel/CSV instead |
| Missing data | Didn't click Save | Click "💾 Save to database" |
| Charts empty | No data uploaded yet | Upload data first |
| Power BI not refreshing | Forgot to click Refresh | Click refresh in app, then in Power BI |

### Debugging Steps

1. **Check terminal output** where you ran `streamlit run app.py`
2. **Look for red error messages** (stack traces)
3. **Run test suite:** `python test_validation.py`
4. **Try sample data:** Upload `sample_test_data.csv` to isolate issue
5. **Check file permissions:** Ensure app can write to folder

---

## Extending the App

### Adding a New Page

1. Add a new option in sidebar radio:
```python
page = st.sidebar.radio("Navigate", [
    "📤 Upload Data",
    "📊 Dashboard",
    "🐄 Per-Cow Analysis",
    "⚠️ Health Alerts",
    "📁 Data Table & Export",
    "🆕 Your New Page"  # Add here
])
```

2. Add the page logic at the end of app.py:
```python
elif page == "🆕 Your New Page":
    st.title("Your New Page")
    # Your code here
```

### Adding a New Validation

In `upsert_records()`, add to the validation loop:
```python
# Check your new condition
if some_condition:
    errors.append(f"Row {idx+1}: Your error message here")
```

### Adding a New Chart

```python
import plotly.graph_objects as go

fig = go.Figure()
fig.add_trace(go.Scatter(x=data["x"], y=data["y"], name="Label"))
fig.update_layout(height=400, plot_bgcolor="white")
st.plotly_chart(fig, use_container_width=True)
```

---

## Maintenance

### Regular Tasks

- **Backup database:** Copy `cow_farm.db` to safe location weekly
- **Check disk space:** Database grows over time (very slowly)
- **Update dependencies:** Run `pip install --upgrade -r requirements.txt` periodically

### If Something Breaks

1. Check if `cow_farm.db` is corrupted:
   - Rename it to `cow_farm.db.backup`
   - Restart app (creates new empty database)
   - If that works, restore from backup CSV

2. Check if dependencies broke:
   - Run `pip install --force-reinstall -r requirements.txt`

3. Check if code was modified:
   - Restore from backup or re-download original

---

## License & Attribution

This app was built using:
- **Streamlit:** Open-source Python web framework (Apache 2.0)
- **Pandas:** Data manipulation library (BSD 3-Clause)
- **Plotly:** Charting library (MIT)
- **SQLite:** Public domain database
- **pdfplumber:** PDF parsing (MIT)
- **openpyxl:** Excel reading (MIT)

No proprietary or paid services used. Entire stack is open-source.

---

## Credits

**Built by:** Kiro AI Agent  
**For:** Dairy farm milk production tracking and analysis  
**Date:** August 2026  
**Version:** 2.0 (Master Prompt Compliant)  

---

**End of App Structure Guide**
