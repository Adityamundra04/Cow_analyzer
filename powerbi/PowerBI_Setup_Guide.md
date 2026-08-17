# Power BI Desktop Setup — Cow Farm Milk Analytics

A quick note first: Power BI's `.pbix` is a proprietary binary file that only
Power BI Desktop itself can save, so I can't generate that file directly here.
What I've set up instead gets you to the same dashboard in about 10 minutes —
you build it once in Power BI Desktop using the steps below, and after that
it's just "Refresh" every time you add new days of data.

## 1. Your data source

Two options — use whichever is easier for you:

- **From the web app (recommended):** open the app → go to
  **📁 Data Table & Export** → click **"Refresh Power BI export file"**.
  This writes `powerbi/cow_data_export.csv` with all your accumulated,
  cleaned data (already includes a `total` column).
- **Directly from your files:** use `sample_data/cow_data_template.xlsx` as
  the format, and keep appending your daily sheets into one Excel file.

## 2. Load it into Power BI Desktop

1. Open **Power BI Desktop** → **Get Data** → **Text/CSV** (or **Excel**).
2. Select `cow_data_export.csv`.
3. Click **Transform Data** (opens Power Query) and check:
   - `date` → Data Type: **Date**
   - `cow_no` → **Whole Number**
   - `morning`, `evening`, `total` → **Decimal Number**
   - `remark` → **Text**
4. Click **Close & Apply**.

## 3. Add a Date table (needed for time-intelligence)

**Modeling** tab → **New Table**, paste:

```
DateTable = CALENDAR(MIN(cow_data_export[date]), MAX(cow_data_export[date]))
```

Then **Model view** → drag a relationship from `cow_data_export[date]` to
`DateTable[Date]`.

## 4. DAX measures (paste each as New Measure)

See `DAX_measures.txt` in this folder for the full list, ready to copy-paste.
Highlights:

- `Total Milk` — sum of morning + evening for the selected filter
- `7-Day Avg Milk` / `15-Day Avg Milk` — rolling averages per cow, using
  `AVERAGEX` over a windowed date range
- `Remark Count` — count of non-blank remarks (mastitis, etc.)
- `Yield Drop Flag` — flags a day where a cow's total fell below 70% of its
  own 7-day average (mirrors the alert logic in the web app)

## 5. Build the visuals

| Visual | Fields |
|---|---|
| Card | `Total Milk`, `Remark Count` |
| Line chart | Axis: `date`, Values: `Total Milk`, `7-Day Avg Milk`, `15-Day Avg Milk` |
| Table/Matrix | Rows: `cow_no`, Values: `Total Milk`, `7-Day Avg Milk`, `15-Day Avg Milk`, `Remark Count` |
| Bar chart | Axis: `cow_no`, Values: `Total Milk` (sort descending → top/bottom performers) |
| Slicer | `date` (range slider), `cow_no` |
| Table (alerts) | Filter: `Yield Drop Flag = 1` OR `remark` is not blank |

## 6. Keeping it updated

Each time you add new days of data in the web app:
1. Go to **📁 Data Table & Export** → **Refresh Power BI export file**.
2. In Power BI Desktop, click **Refresh** on the Home ribbon.

If you want this fully automatic on a schedule, that requires publishing to
the Power BI Service (cloud) with a paid workspace — outside the "local only"
scope you asked for, so it's not covered here, but it's a small step up if
you ever want it.
