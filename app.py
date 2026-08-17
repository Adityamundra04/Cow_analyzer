"""
Cow Farm Milk Analytics — local web app
Run with:  streamlit run app.py
Opens at:  http://localhost:8501
"""

import io
import os
import sqlite3
from datetime import datetime, timedelta

import pandas as pd
import plotly.graph_objects as go
import streamlit as st

# --------------------------------------------------------------------------
# CONFIG
# --------------------------------------------------------------------------
APP_DIR = os.path.dirname(os.path.abspath(__file__))
DB_PATH = os.path.join(APP_DIR, "cow_farm.db")
POWERBI_CSV_PATH = os.path.join(APP_DIR, "powerbi", "cow_data_export.csv")

STANDARD_COLS = ["Date", "Cow No", "Code 1", "Code 2", "Morning", "Evening", "Remark"]

st.set_page_config(
    page_title="Cow Farm Milk Analytics",
    page_icon="🐄",
    layout="wide",
    initial_sidebar_state="expanded",
)

# --------------------------------------------------------------------------
# STYLE
# --------------------------------------------------------------------------
st.markdown(
    """
    <style>
    .stApp { background-color: #f5f7f2; }
    div[data-testid="stMetric"] {
        background: #ffffff;
        border: 1px solid #e0e5da;
        border-radius: 10px;
        padding: 14px 16px;
        box-shadow: 0 1px 3px rgba(0,0,0,0.04);
    }
    h1, h2, h3 { color: #2f4b26; }
    .stTabs [data-baseweb="tab"] { font-weight: 600; }
    .alert-box {
        background: #fff3f0; border-left: 5px solid #d9534f;
        padding: 10px 14px; border-radius: 6px; margin-bottom: 8px;
    }
    </style>
    """,
    unsafe_allow_html=True,
)

# --------------------------------------------------------------------------
# DATABASE
# --------------------------------------------------------------------------
def get_conn():
    conn = sqlite3.connect(DB_PATH)
    conn.execute(
        """
        CREATE TABLE IF NOT EXISTS records (
            date TEXT NOT NULL,
            cow_no INTEGER NOT NULL,
            code1 TEXT,
            code2 TEXT,
            morning REAL,
            evening REAL,
            remark TEXT,
            PRIMARY KEY (date, cow_no)
        )
        """
    )
    return conn


def upsert_records(df: pd.DataFrame):
    """
    Upsert records into the database. Returns (new_count, updated_count, errors_list).
    """
    conn = get_conn()
    cur = conn.cursor()
    rows = df[["Date", "Cow No", "Code 1", "Code 2", "Morning", "Evening", "Remark"]].copy()
    
    # Parse dates
    rows["Date"] = pd.to_datetime(rows["Date"], errors="coerce", dayfirst=True).dt.strftime("%Y-%m-%d")
    rows = rows.dropna(subset=["Date", "Cow No"])
    
    new_count = 0
    updated_count = 0
    errors = []
    
    for idx, r in rows.iterrows():
        try:
            # Validate Cow No
            cow_no = int(r["Cow No"])
            if cow_no <= 0:
                errors.append(f"Row {idx+1}: Cow No must be positive (got {cow_no})")
                continue
            
            # Validate and parse Morning/Evening
            try:
                morning_val = float(r["Morning"]) if pd.notna(r["Morning"]) and str(r["Morning"]).strip() else 0.0
                if morning_val < 0:
                    errors.append(f"Row {idx+1} Cow {cow_no}: Morning value cannot be negative ({morning_val})")
                    morning_val = 0.0
                if morning_val > 30:
                    errors.append(f"Row {idx+1} Cow {cow_no}: Morning value suspiciously high ({morning_val} L) — verify this")
            except (ValueError, TypeError):
                errors.append(f"Row {idx+1} Cow {cow_no}: Morning value '{r['Morning']}' is not a number — using 0.0")
                morning_val = 0.0
            
            try:
                evening_val = float(r["Evening"]) if pd.notna(r["Evening"]) and str(r["Evening"]).strip() else 0.0
                if evening_val < 0:
                    errors.append(f"Row {idx+1} Cow {cow_no}: Evening value cannot be negative ({evening_val})")
                    evening_val = 0.0
                if evening_val > 30:
                    errors.append(f"Row {idx+1} Cow {cow_no}: Evening value suspiciously high ({evening_val} L) — verify this")
            except (ValueError, TypeError):
                errors.append(f"Row {idx+1} Cow {cow_no}: Evening value '{r['Evening']}' is not a number — using 0.0")
                evening_val = 0.0
            
            # Check if this is an update or insert
            cur.execute("SELECT 1 FROM records WHERE date=? AND cow_no=?", (r["Date"], cow_no))
            is_update = cur.fetchone() is not None
            
            cur.execute(
                """
                INSERT INTO records (date, cow_no, code1, code2, morning, evening, remark)
                VALUES (?, ?, ?, ?, ?, ?, ?)
                ON CONFLICT(date, cow_no) DO UPDATE SET
                    code1=excluded.code1, code2=excluded.code2,
                    morning=excluded.morning, evening=excluded.evening,
                    remark=excluded.remark
                """,
                (
                    r["Date"], cow_no,
                    str(r["Code 1"]) if pd.notna(r["Code 1"]) else None,
                    str(r["Code 2"]) if pd.notna(r["Code 2"]) else None,
                    morning_val, evening_val,
                    str(r["Remark"]) if pd.notna(r["Remark"]) and str(r["Remark"]).strip() else None,
                ),
            )
            
            if is_update:
                updated_count += 1
            else:
                new_count += 1
                
        except Exception as e:
            errors.append(f"Row {idx+1}: {str(e)}")
    
    conn.commit()
    conn.close()
    return new_count, updated_count, errors


def load_all() -> pd.DataFrame:
    conn = get_conn()
    df = pd.read_sql_query("SELECT * FROM records ORDER BY date, cow_no", conn)
    conn.close()
    if df.empty:
        return df
    df["date"] = pd.to_datetime(df["date"])
    df["total"] = df["morning"].fillna(0) + df["evening"].fillna(0)
    return df


def export_for_powerbi(df: pd.DataFrame):
    os.makedirs(os.path.dirname(POWERBI_CSV_PATH), exist_ok=True)
    out = df.copy()
    out["date"] = out["date"].dt.strftime("%Y-%m-%d")
    out.to_csv(POWERBI_CSV_PATH, index=False)


# --------------------------------------------------------------------------
# PARSERS
# --------------------------------------------------------------------------
def guess_column_map(raw_cols):
    """Map messy source headers to STANDARD_COLS using keyword matching."""
    mapping = {}
    low = {c: str(c).strip().lower() for c in raw_cols}
    for target in STANDARD_COLS:
        tgt_l = target.lower()
        best = None
        for orig, l in low.items():
            if tgt_l == l:
                best = orig
                break
        if best is None:
            for orig, l in low.items():
                key = tgt_l.replace(" ", "")
                if key in l.replace(" ", ""):
                    best = orig
                    break
        mapping[target] = best
    return mapping


def parse_excel(file) -> pd.DataFrame:
    try:
        df = pd.read_excel(file)
        return df
    except Exception as e:
        raise ValueError(f"Failed to parse Excel file: {str(e)}")


def parse_csv(file) -> pd.DataFrame:
    try:
        return pd.read_csv(file)
    except Exception as e:
        raise ValueError(f"Failed to parse CSV file: {str(e)}")


def parse_pdf(file) -> pd.DataFrame:
    try:
        import pdfplumber

        tables = []
        with pdfplumber.open(file) as pdf:
            for page in pdf.pages:
                for tbl in page.extract_tables():
                    if not tbl or len(tbl) < 2:
                        continue
                    header, *body = tbl
                    tables.append(pd.DataFrame(body, columns=header))
        if not tables:
            return pd.DataFrame()
        return pd.concat(tables, ignore_index=True)
    except Exception as e:
        raise ValueError(f"Failed to parse PDF file: {str(e)}")


# --------------------------------------------------------------------------
# ANALYTICS HELPERS
# --------------------------------------------------------------------------
def add_rolling(df_cow: pd.DataFrame) -> pd.DataFrame:
    df_cow = df_cow.sort_values("date").copy()
    df_cow["avg_7d"] = df_cow["total"].rolling(7, min_periods=1).mean()
    df_cow["avg_15d"] = df_cow["total"].rolling(15, min_periods=1).mean()
    return df_cow


def build_alerts(df: pd.DataFrame) -> pd.DataFrame:
    """Flag remarks + sudden drops vs each cow's 7-day rolling average."""
    alerts = []
    for cow, g in df.groupby("cow_no"):
        g = add_rolling(g)
        g["prev_avg_7d"] = g["avg_7d"].shift(1)
        drop = g[(g["prev_avg_7d"] > 0) & (g["total"] < g["prev_avg_7d"] * 0.7)]
        for _, r in drop.iterrows():
            alerts.append(
                {
                    "date": r["date"].strftime("%Y-%m-%d"),
                    "cow_no": cow,
                    "type": "Sudden yield drop",
                    "detail": f"{r['total']:.1f} L vs 7-day avg {r['prev_avg_7d']:.1f} L",
                }
            )
        remarked = g[g["remark"].notna() & (g["remark"].str.strip() != "")]
        for _, r in remarked.iterrows():
            alerts.append(
                {
                    "date": r["date"].strftime("%Y-%m-%d"),
                    "cow_no": cow,
                    "type": "Remark logged",
                    "detail": r["remark"],
                }
            )
    if not alerts:
        return pd.DataFrame(columns=["date", "cow_no", "type", "detail"])
    out = pd.DataFrame(alerts).sort_values("date", ascending=False)
    return out


# --------------------------------------------------------------------------
# SIDEBAR NAV
# --------------------------------------------------------------------------
st.sidebar.title("🐄 Farm Analytics")
page = st.sidebar.radio(
    "Navigate",
    ["📤 Upload Data", "📊 Dashboard", "🐄 Per-Cow Analysis", "⚠️ Health Alerts", "📁 Data Table & Export"],
)

df_all = load_all()

# --------------------------------------------------------------------------
# PAGE: UPLOAD
# --------------------------------------------------------------------------
if page == "📤 Upload Data":
    st.title("Upload Daily Records")
    st.caption("Accepts PDF, Excel (.xlsx/.xls) or CSV in the Date / Cow No / Code 1 / Code 2 / Morning / Evening / Remark format.")

    up = st.file_uploader("Choose a file", type=["pdf", "xlsx", "xls", "csv"])

    if up is not None:
        ext = up.name.split(".")[-1].lower()
        raw = pd.DataFrame()
        parse_error = None
        
        try:
            if ext == "pdf":
                raw = parse_pdf(up)
            elif ext == "csv":
                raw = parse_csv(up)
            else:
                raw = parse_excel(up)
        except Exception as e:
            parse_error = str(e)

        if parse_error:
            st.error(f"Could not parse file: {parse_error}")
        elif raw.empty:
            st.warning("No table detected. If this is a scanned/image PDF, try exporting to Excel/CSV instead, or enter data manually below.")
        else:
            st.subheader("1. Check column mapping")
            mapping = guess_column_map(raw.columns)
            cols = st.columns(len(STANDARD_COLS))
            final_map = {}
            for i, target in enumerate(STANDARD_COLS):
                with cols[i]:
                    options = ["(none)"] + list(raw.columns)
                    default = mapping[target] if mapping[target] in raw.columns else "(none)"
                    choice = st.selectbox(target, options, index=options.index(default) if default in options else 0, key=f"map_{target}")
                    final_map[target] = None if choice == "(none)" else choice

            preview = pd.DataFrame()
            for target, src in final_map.items():
                preview[target] = raw[src] if src else None

            # default date if column missing: let user pick one date for the whole batch
            if final_map["Date"] is None:
                batch_date = st.date_input("This file has no Date column — apply one date to all rows", datetime.today())
                preview["Date"] = batch_date.strftime("%Y-%m-%d")

            st.subheader("2. Review & fix before saving")
            st.caption("Check for missing Cow No, negative values, or typos. You can edit cells directly below.")
            edited = st.data_editor(preview, num_rows="dynamic", use_container_width=True)

            if st.button("💾 Save to database", type="primary"):
                with st.spinner("Saving..."):
                    new_count, updated_count, errors = upsert_records(edited)
                    
                    if errors:
                        st.warning(f"⚠️ {len(errors)} validation issues found:")
                        for err in errors[:10]:  # Show first 10 errors
                            st.warning(f"• {err}")
                        if len(errors) > 10:
                            st.warning(f"... and {len(errors) - 10} more issues")
                    
                    if new_count > 0 or updated_count > 0:
                        export_for_powerbi(load_all())
                        msg = []
                        if new_count > 0:
                            msg.append(f"{new_count} new row{'s' if new_count != 1 else ''}")
                        if updated_count > 0:
                            msg.append(f"{updated_count} updated row{'s' if updated_count != 1 else ''}")
                        st.success(f"✅ Saved: {', '.join(msg)}. Power BI export refreshed.")
                        st.rerun()
                    else:
                        st.error("No valid rows to save. Please fix the errors above.")

    st.divider()
    with st.expander("Or enter a single row manually"):
        with st.form("manual_entry"):
            c1, c2, c3 = st.columns(3)
            d = c1.date_input("Date", datetime.today())
            cow = c2.number_input("Cow No", min_value=1, step=1)
            code1 = c3.text_input("Code 1")
            c4, c5, c6 = st.columns(3)
            code2 = c4.text_input("Code 2")
            morning = c5.number_input("Morning (L)", min_value=0.0, step=0.1)
            evening = c6.number_input("Evening (L)", min_value=0.0, step=0.1)
            remark = st.text_input("Remark")
            if st.form_submit_button("Add row"):
                one = pd.DataFrame([{
                    "Date": d.strftime("%Y-%m-%d"), "Cow No": cow, "Code 1": code1,
                    "Code 2": code2, "Morning": morning, "Evening": evening, "Remark": remark,
                }])
                new_count, updated_count, errors = upsert_records(one)
                if errors:
                    for err in errors:
                        st.error(err)
                if new_count > 0 or updated_count > 0:
                    export_for_powerbi(load_all())
                    st.success(f"Row {'updated' if updated_count > 0 else 'added'}.")
                    st.rerun()

# --------------------------------------------------------------------------
# PAGE: DASHBOARD
# --------------------------------------------------------------------------
elif page == "📊 Dashboard":
    st.title("Farm Dashboard")

    if df_all.empty:
        st.info("No data yet — go to 'Upload Data' first.")
    else:
        min_d, max_d = df_all["date"].min(), df_all["date"].max()
        dr = st.date_input("Date range", (min_d, max_d), min_value=min_d, max_value=max_d)
        if isinstance(dr, tuple) and len(dr) == 2:
            mask = (df_all["date"] >= pd.Timestamp(dr[0])) & (df_all["date"] <= pd.Timestamp(dr[1]))
            df = df_all[mask]
        else:
            df = df_all

        if df.empty:
            st.warning("No data in the selected date range.")
        else:
            latest_date = df["date"].max()
            today_df = df[df["date"] == latest_date]

            c1, c2, c3, c4 = st.columns(4)
            c1.metric("Cows recorded", df["cow_no"].nunique())
            c2.metric(f"Total yield on {latest_date.strftime('%d-%b')}", f"{today_df['total'].sum():.1f} L")
            avg_yield = today_df['total'].mean() if len(today_df) > 0 else 0.0
            c3.metric("Avg yield / cow (latest day)", f"{avg_yield:.1f} L")
            alerts_today = today_df["remark"].notna().sum()
            c4.metric("Remarks today", int(alerts_today))

            st.subheader("Farm-wide milk trend")
            daily = df.groupby("date", as_index=False)["total"].sum().sort_values("date")
            daily["avg_7d"] = daily["total"].rolling(7, min_periods=1).mean()
            daily["avg_15d"] = daily["total"].rolling(15, min_periods=1).mean()

            fig = go.Figure()
            fig.add_trace(go.Scatter(x=daily["date"], y=daily["total"], name="Daily total", mode="lines+markers", line=dict(color="#6aa84f")))
            fig.add_trace(go.Scatter(x=daily["date"], y=daily["avg_7d"], name="7-day avg", line=dict(color="#e69138", dash="dash")))
            fig.add_trace(go.Scatter(x=daily["date"], y=daily["avg_15d"], name="15-day avg", line=dict(color="#3d85c6", dash="dot")))
            fig.update_layout(height=420, plot_bgcolor="white", legend=dict(orientation="h", y=1.1))
            st.plotly_chart(fig, use_container_width=True)

            colA, colB = st.columns(2)
            with colA:
                st.subheader("Top 5 cows (avg yield)")
                top = df.groupby("cow_no")["total"].mean().sort_values(ascending=False).head(5).reset_index()
                if not top.empty:
                    fig2 = go.Figure(go.Bar(x=top["cow_no"].astype(str), y=top["total"], marker_color="#6aa84f"))
                    fig2.update_layout(height=320, plot_bgcolor="white", xaxis_title="Cow No", yaxis_title="Avg L/day")
                    st.plotly_chart(fig2, use_container_width=True)
                else:
                    st.info("Not enough data for rankings.")
            with colB:
                st.subheader("Bottom 5 cows (avg yield)")
                bot = df.groupby("cow_no")["total"].mean().sort_values(ascending=True).head(5).reset_index()
                if not bot.empty:
                    fig3 = go.Figure(go.Bar(x=bot["cow_no"].astype(str), y=bot["total"], marker_color="#cc4125"))
                    fig3.update_layout(height=320, plot_bgcolor="white", xaxis_title="Cow No", yaxis_title="Avg L/day")
                    st.plotly_chart(fig3, use_container_width=True)
                else:
                    st.info("Not enough data for rankings.")
            
            # Monthly/Weekly Summary
            st.divider()
            st.subheader("📅 Period Summaries")
            
            tab1, tab2 = st.tabs(["Weekly Summary", "Monthly Summary"])
            
            with tab1:
                df_weekly = df.copy()
                df_weekly["week"] = df_weekly["date"].dt.to_period("W").astype(str)
                weekly_summary = df_weekly.groupby(["week", "cow_no"])["total"].sum().reset_index()
                weekly_pivot = weekly_summary.pivot_table(index="cow_no", columns="week", values="total", fill_value=0, aggfunc="sum")
                
                # Add farm-wide totals
                farm_weekly = df_weekly.groupby("week", as_index=False)["total"].sum()
                farm_weekly.columns = ["Week", "Farm Total (L)"]
                
                st.caption("Farm-wide weekly totals")
                st.dataframe(farm_weekly, use_container_width=True, hide_index=True)
                
                st.caption("Per-cow weekly totals (litres)")
                st.dataframe(weekly_pivot, use_container_width=True)
            
            with tab2:
                df_monthly = df.copy()
                df_monthly["month"] = df_monthly["date"].dt.to_period("M").astype(str)
                monthly_summary = df_monthly.groupby(["month", "cow_no"])["total"].sum().reset_index()
                monthly_pivot = monthly_summary.pivot_table(index="cow_no", columns="month", values="total", fill_value=0, aggfunc="sum")
                
                # Add farm-wide totals
                farm_monthly = df_monthly.groupby("month", as_index=False)["total"].sum()
                farm_monthly.columns = ["Month", "Farm Total (L)"]
                
                st.caption("Farm-wide monthly totals")
                st.dataframe(farm_monthly, use_container_width=True, hide_index=True)
                
                st.caption("Per-cow monthly totals (litres)")
                st.dataframe(monthly_pivot, use_container_width=True)

# --------------------------------------------------------------------------
# PAGE: PER-COW
# --------------------------------------------------------------------------
elif page == "🐄 Per-Cow Analysis":
    st.title("Per-Cow Analysis")
    if df_all.empty:
        st.info("No data yet — go to 'Upload Data' first.")
    else:
        cow_list = sorted(df_all["cow_no"].unique())
        cow = st.selectbox("Select Cow No", cow_list)
        g = add_rolling(df_all[df_all["cow_no"] == cow])

        if len(g) == 0:
            st.warning(f"No data found for Cow {cow}.")
        else:
            c1, c2, c3 = st.columns(3)
            latest_total = g['total'].iloc[-1] if len(g) > 0 else 0.0
            latest_7d = g['avg_7d'].iloc[-1] if len(g) > 0 else 0.0
            latest_15d = g['avg_15d'].iloc[-1] if len(g) > 0 else 0.0
            
            c1.metric("Latest total (L)", f"{latest_total:.1f}")
            c2.metric("7-day avg (L)", f"{latest_7d:.1f}")
            c3.metric("15-day avg (L)", f"{latest_15d:.1f}")

            fig = go.Figure()
            fig.add_trace(go.Scatter(x=g["date"], y=g["morning"], name="Morning", line=dict(color="#93c47d")))
            fig.add_trace(go.Scatter(x=g["date"], y=g["evening"], name="Evening", line=dict(color="#6d9eeb")))
            fig.add_trace(go.Scatter(x=g["date"], y=g["total"], name="Total", line=dict(color="#38761d", width=3)))
            fig.add_trace(go.Scatter(x=g["date"], y=g["avg_7d"], name="7-day avg", line=dict(color="#e69138", dash="dash")))
            fig.add_trace(go.Scatter(x=g["date"], y=g["avg_15d"], name="15-day avg", line=dict(color="#cc0000", dash="dot")))
            fig.update_layout(height=430, plot_bgcolor="white", legend=dict(orientation="h", y=1.1), title=f"Cow {cow} — milk yield history")
            st.plotly_chart(fig, use_container_width=True)

            st.subheader("History")
            show = g[["date", "code1", "code2", "morning", "evening", "total", "avg_7d", "avg_15d", "remark"]].sort_values("date", ascending=False)
            show.columns = ["Date", "Code 1", "Code 2", "Morning", "Evening", "Total", "7-day Avg", "15-day Avg", "Remark"]
            st.dataframe(show, use_container_width=True, hide_index=True)

# --------------------------------------------------------------------------
# PAGE: ALERTS
# --------------------------------------------------------------------------
elif page == "⚠️ Health Alerts":
    st.title("Health & Yield Alerts")
    if df_all.empty:
        st.info("No data yet — go to 'Upload Data' first.")
    else:
        alerts = build_alerts(df_all)
        if alerts.empty:
            st.success("No alerts. Everything looks steady. 🎉")
        else:
            st.caption("Sudden yield drop = a day's total fell below 70% of that cow's prior 7-day average.")
            for _, r in alerts.iterrows():
                icon = "🩺" if r["type"] == "Remark logged" else "📉"
                st.markdown(
                    f"<div class='alert-box'>{icon} <b>Cow {r['cow_no']}</b> — {r['date']} — "
                    f"<b>{r['type']}</b>: {r['detail']}</div>",
                    unsafe_allow_html=True,
                )

# --------------------------------------------------------------------------
# PAGE: DATA TABLE / EXPORT
# --------------------------------------------------------------------------
elif page == "📁 Data Table & Export":
    st.title("Full Data & Export")
    if df_all.empty:
        st.info("No data yet — go to 'Upload Data' first.")
    else:
        show = df_all[["date", "cow_no", "code1", "code2", "morning", "evening", "total", "remark"]].sort_values(["date", "cow_no"], ascending=[False, True])
        show.columns = ["Date", "Cow No", "Code 1", "Code 2", "Morning", "Evening", "Total", "Remark"]
        st.dataframe(show, use_container_width=True, hide_index=True)

        c1, c2 = st.columns(2)
        csv = show.to_csv(index=False).encode("utf-8")
        c1.download_button("⬇️ Download CSV", csv, "cow_farm_data.csv", "text/csv")

        if c2.button("🔄 Refresh Power BI export file"):
            export_for_powerbi(df_all)
            st.success(f"Refreshed: {POWERBI_CSV_PATH}\nPoint Power BI's data source at this file and click Refresh there.")
