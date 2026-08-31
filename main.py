import os

# Works around a known macOS joblib/scikit-learn bug where CPU-core
# auto-detection can return None and crash inside KMeans.
os.environ.setdefault("LOKY_MAX_CPU_COUNT", "4")

import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px

# Professional Page Configuration
st.set_page_config(
    page_title="CGM Glucose Viewer", 
    page_icon="🩸",
    layout="wide",
    initial_sidebar_state="expanded"
)

st.title("🩸 CGM Glucose Value Over Time — Multi-Patient")

st.markdown(
    """
    <style>
    .big-font { font-size:18px !important; color: #2C3E50; }
    .patient-card {
        background-color: #F8F9F9;
        padding: 15px;
        border-radius: 8px;
        border-left: 5px solid #2980B9;
        margin-bottom: 20px;
    }
    .ml-desc {
        background-color: #EBF5FB;
        padding: 12px 16px;
        border-radius: 6px;
        border-left: 4px solid #3498DB;
        margin-bottom: 15px;
        font-size: 14px;
        color: #2C3E50;
    }
    </style>
    <div class="big-font">
    Upload one or more CGM CSV exports. Each file gets its own dedicated tab below with independent patient details, crop ranges, and ML results.
    </div>
    <br>
    """, unsafe_allow_html=True
)

uploaded_files = st.file_uploader(
    "📂 Upload CGM CSV file(s)", type=["csv"], accept_multiple_files=True
)

EXPECTED_COLUMNS = [
    "Index",
    "Timestamp (YYYY-MM-DDThh:mm:ss)",
    "Event Type",
    "Event Subtype",
    "Patient Info",
    "Device Info",
    "Source Device ID",
    "Glucose Value (mmol/L)",
    "Insulin Value (u)",
    "Carb Value (grams)",
    "Duration (hh:mm:ss)",
    "Glucose Rate of Change (mmol/L/min)",
    "Transmitter Time (Long Integer)",
    "Transmitter ID",
]

TS_COL = "Timestamp (YYYY-MM-DDThh:mm:ss)"
GLUCOSE_COL = "Glucose Value (mmol/L)"
ROC_COL = "Glucose Rate of Change (mmol/L/min)"


def extract_patient_metadata(uploaded_file):
    """Extract patient and device metadata from header cells."""
    uploaded_file.seek(0)
    meta_df = pd.read_csv(uploaded_file, nrows=7, header=None)
    uploaded_file.seek(0)

    def safe_get(row, col):
        try:
            val = meta_df.iloc[row, col]
            return str(val).strip() if pd.notna(val) else "N/A"
        except Exception:
            return "N/A"

    return {
        "first_name": safe_get(1, 4),  # 2E
        "last_name": safe_get(2, 4),   # 3E
        "birthday": safe_get(3, 4),    # 4E
        "device_type": safe_get(4, 5), # 5F
        "sensor_type": safe_get(5, 5), # 6F
    }


def apply_professional_layout(fig):
    """Applies a consistent, colorful, and professional theme to Plotly figures."""
    fig.update_layout(
        template="plotly_white",
        font=dict(family="Arial, sans-serif", size=12, color="#2C3E50"),
        title_font=dict(size=20, color="#1F618D", family="Arial, sans-serif"),
        hovermode="x unified",
        plot_bgcolor="rgba(0,0,0,0)",
        paper_bgcolor="rgba(0,0,0,0)",
        margin=dict(l=40, r=40, t=60, b=40)
    )
    return fig


def load_dataframe(uploaded_file, skip_rows=9):
    """Parse one uploaded CGM CSV into a cleaned DataFrame (skipping 9 header rows by default)."""
    uploaded_file.seek(0)
    df = pd.read_csv(
        uploaded_file,
        skiprows=skip_rows,
        names=EXPECTED_COLUMNS,
        header=None,
    )
    df[TS_COL] = pd.to_datetime(df[TS_COL], errors="coerce")
    df[GLUCOSE_COL] = pd.to_numeric(df[GLUCOSE_COL], errors="coerce")
    return df.dropna(subset=[TS_COL, GLUCOSE_COL])


def render_patient_view(uploaded_file, key_prefix):
    """Render metadata summary + full single-patient view (chart + ML)."""
    
    meta = extract_patient_metadata(uploaded_file)
    
    st.markdown(
        f"""
        <div class="patient-card">
            <h3 style="margin-top:0; color:#1F618D;">👤 {meta['first_name']} {meta['last_name']}</h3>
            <b>Date of Birth:</b> {meta['birthday']} &nbsp;|&nbsp; 
            <b>Device Model:</b> {meta['device_type']} &nbsp;|&nbsp; 
            <b>Sensor Type:</b> {meta['sensor_type']}
        </div>
        """,
        unsafe_allow_html=True
    )

    try:
        plot_df = load_dataframe(uploaded_file, skip_rows=9)
    except Exception as e:
        st.error(f"Could not read this file with the expected column layout: {e}")
        return

    if plot_df.empty:
        st.warning("⚠️ No valid Timestamp / Glucose Value rows found in this file.")
        return

    st.markdown("### 📈 Main Glucose Trend Over Time")

    min_date = plot_df[TS_COL].min()
    max_date = plot_df[TS_COL].max()
    
    col_d1, col_d2 = st.columns(2)
    start_date = col_d1.date_input(
        "📅 Start Date (Main Graph)",
        value=min_date.date(),
        min_value=min_date.date(),
        max_value=max_date.date(),
        key=f"{key_prefix}_main_start_date"
    )
    end_date = col_d2.date_input(
        "📅 End Date (Main Graph)",
        value=max_date.date(),
        min_value=min_date.date(),
        max_value=max_date.date(),
        key=f"{key_prefix}_main_end_date"
    )

    filtered = plot_df[
        (plot_df[TS_COL].dt.date >= start_date) & 
        (plot_df[TS_COL].dt.date <= end_date)
    ]

    if filtered.empty:
        st.warning("⚠️ No data available within the selected date range.")
        return

    fig = px.line(
        filtered,
        x=TS_COL,
        y=GLUCOSE_COL,
        title="<b>Primary Glucose Trend (mmol/L)</b>",
        markers=True,
    )
    fig.update_traces(
        line=dict(color="royalblue", width=2), 
        marker=dict(color="coral", size=5, line=dict(width=1, color="DarkSlateGrey"))
    )
    fig.update_layout(
        xaxis_title="Timestamp",
        yaxis_title="Glucose Value (mmol/L)",
        xaxis=dict(rangeslider=dict(visible=True), type="date"),
        dragmode="zoom",
    )
    fig = apply_professional_layout(fig)
    
    st.plotly_chart(fig, use_container_width=True, key=f"{key_prefix}_main_chart")

    # Metrics
    col1, col2, col3 = st.columns(3)
    col1.metric("📊 Mean Glucose", f"{filtered[GLUCOSE_COL].mean():.2f} mmol/L")
    col2.metric("📉 Min Glucose", f"{filtered[GLUCOSE_COL].min():.2f} mmol/L")
    col3.metric("📈 Max Glucose", f"{filtered[GLUCOSE_COL].max():.2f} mmol/L")

    with st.expander("🔍 View raw data table"):
        st.dataframe(filtered)

    st.markdown("---")
    st.markdown("### 🧠 ML Pattern Analysis")
    st.caption("Analyze specific subsets of time using the custom ML date filter below.")

    ml_min_date = filtered[TS_COL].min()
    ml_max_date = filtered[TS_COL].max()

    ml_date_range = st.slider(
        "⏳ Select Specific Time Window for ML Methods",
        min_value=ml_min_date.to_pydatetime(),
        max_value=ml_max_date.to_pydatetime(),
        value=(ml_min_date.to_pydatetime(), ml_max_date.to_pydatetime()),
        key=f"{key_prefix}_ml_date_range",
    )

    ml_filtered = filtered[
        (filtered[TS_COL] >= ml_date_range[0]) & 
        (filtered[TS_COL] <= ml_date_range[1])
    ]

    analysis_df = ml_filtered.copy().sort_values(TS_COL).set_index(TS_COL)

    if len(analysis_df) < 10:
        st.warning("⚠️ Selected ML range is too short (< 10 readings) — widen the ML time window slider above.")
        return

    ml_tabs = st.tabs([
        "🔴 Anomaly Detection",
        "🟢 Clustering",
        "🔵 Periodicity (FFT)",
        "🟠 Trend Analysis",
        "📈 Linear Regression"
    ])

    # Tab 1: Anomaly Detection
    with ml_tabs[0]:
        st.markdown("#### Isolation Forest Anomaly Detection")
        st.markdown(
            """
            <div class="ml-desc">
                <b>Method & Purpose:</b> Uses tree partitioning to isolate rare data points. Anomalies require fewer decision-tree splits to isolate than typical readings.<br>
                <b>What it measures:</b> Statistical outliers and unexpected glucose spikes or drops that deviate significantly from standard glycemic behavior.<br>
                <b>How to read:</b> Highlighted red markers flag unexpected readings based on your chosen contamination threshold.
            </div>
            """,
            unsafe_allow_html=True
        )

        from sklearn.ensemble import IsolationForest

        contamination = st.slider(
            "Expected anomaly fraction", 0.01, 0.25, 0.05, 0.01, key=f"{key_prefix}_contam"
        )
        features = analysis_df[[GLUCOSE_COL]].dropna()
        model = IsolationForest(contamination=contamination, random_state=42)
        labels = model.fit_predict(features)
        features = features.copy()
        features["anomaly"] = labels == -1

        fig2 = px.scatter(
            features.reset_index(),
            x=TS_COL,
            y=GLUCOSE_COL,
            color="anomaly",
            color_discrete_map={True: "crimson", False: "lightseagreen"},
            title="<b>Detected Anomalies</b>",
        )
        fig2.update_traces(marker=dict(size=7, opacity=0.8, line=dict(width=1, color="White")))
        fig2.update_layout(xaxis=dict(rangeslider=dict(visible=True)))
        fig2 = apply_professional_layout(fig2)
        
        st.plotly_chart(fig2, use_container_width=True, key=f"{key_prefix}_anomaly_chart")
        st.success(f"Flagged **{int(features['anomaly'].sum())}** anomalous readings out of {len(features)}.")

    # Tab 2: Clustering
    with ml_tabs[1]:
        st.markdown("#### K-Means Clustering (Value + Rate of Change)")
        st.markdown(
            """
            <div class="ml-desc">
                <b>Method & Purpose:</b> Groups time-series readings into <i>K</i> distinct clusters by standardizing glucose level and rate of change (velocity).<br>
                <b>What it measures:</b> Physiological states based on both magnitude and direction (e.g., rapid rise, post-prandial drop, nocturnal stability).<br>
                <b>How to read:</b> Colors correspond to distinct clusters. The table below summarizes the centroid (mean metrics) for each behavioral cluster.
            </div>
            """,
            unsafe_allow_html=True
        )

        from sklearn.cluster import KMeans
        from sklearn.preprocessing import StandardScaler

        n_clusters = st.slider("Number of clusters", 2, 6, 3, key=f"{key_prefix}_nclusters")
        feat_cols = [GLUCOSE_COL]
        if ROC_COL in analysis_df.columns:
            analysis_df[ROC_COL] = pd.to_numeric(analysis_df[ROC_COL], errors="coerce")
            if analysis_df[ROC_COL].notna().sum() > 0:
                feat_cols.append(ROC_COL)

        cluster_df = analysis_df[feat_cols].dropna()
        scaled = StandardScaler().fit_transform(cluster_df)
        km = KMeans(n_clusters=n_clusters, random_state=42, n_init=10)
        cluster_df = cluster_df.copy()
        cluster_df["cluster"] = km.fit_predict(scaled).astype(str)

        fig3 = px.scatter(
            cluster_df.reset_index(),
            x=TS_COL,
            y=GLUCOSE_COL,
            color="cluster",
            color_discrete_sequence=px.colors.qualitative.Vivid,
            title=f"<b>K-Means Clusters (k={n_clusters})</b>",
        )
        fig3.update_traces(marker=dict(size=7, opacity=0.8, line=dict(width=1, color="White")))
        fig3.update_layout(xaxis=dict(rangeslider=dict(visible=True)))
        fig3 = apply_professional_layout(fig3)
        
        st.plotly_chart(fig3, use_container_width=True, key=f"{key_prefix}_cluster_chart")
        st.dataframe(cluster_df.groupby("cluster").mean())

    # Tab 3: Periodicity
    with ml_tabs[2]:
        st.markdown("#### Fast Fourier Transform (FFT) Periodicity")
        st.markdown(
            """
            <div class="ml-desc">
                <b>Method & Purpose:</b> Converts time-domain glucose values into the frequency domain using discrete Fourier transforms.<br>
                <b>What it measures:</b> Recurrent cyclical patterns (circadian rhythms, regular meal intervals, scheduled insulin actions).<br>
                <b>How to read:</b> Higher spectral power peaks indicate dominant repeating cycles measured in hours (e.g., ~24-hour daily cycle or ~4-hour meal cycle).
            </div>
            """,
            unsafe_allow_html=True
        )

        from scipy.fft import rfft, rfftfreq

        resample_min = st.slider("Resample interval (minutes)", 1, 30, 5, key=f"{key_prefix}_resample")
        series = analysis_df[GLUCOSE_COL].resample(f"{resample_min}min").mean().interpolate()

        if len(series) < 10:
            st.warning("Not enough points after resampling — lower the resample interval or widen the time range.")
        else:
            values = series.values - series.values.mean()
            n = len(values)
            yf = rfft(values)
            xf = rfftfreq(n, d=resample_min * 60)
            power = np.abs(yf)
            with np.errstate(divide="ignore"):
                period_hours = 1 / (xf[1:] * 3600)
                
            fig4 = px.line(
                x=period_hours,
                y=power[1:],
                labels={"x": "Period (hours)", "y": "Power"},
                title="<b>FFT Power Spectrum</b>",
            )
            fig4.update_traces(line=dict(color="darkorchid", width=2.5))
            fig4.update_layout(xaxis_range=[0, min(48, period_hours.max())])
            fig4 = apply_professional_layout(fig4)
            
            st.plotly_chart(fig4, use_container_width=True, key=f"{key_prefix}_fft_chart")

            top_idx = np.argsort(power[1:])[::-1][:5]
            top_periods = period_hours[top_idx]
            st.info(f"💡 **Top candidate periods (hours):** {[round(p, 2) for p in top_periods if 0 < p < 72]}")

    # Tab 4: Trend Analysis
    with ml_tabs[3]:
        st.markdown("#### Rolling Mean / Standard Deviation")
        st.markdown(
            """
            <div class="ml-desc">
                <b>Method & Purpose:</b> Computes a moving average and moving standard deviation over a sliding window of sequential readings.<br>
                <b>What it measures:</b> Underlying direction (mean) while isolating short-term volatility and variance (standard deviation).<br>
                <b>How to read:</b> The solid line shows central trend direction; the shaded band represents ±1 standard deviation of glucose instability.
            </div>
            """,
            unsafe_allow_html=True
        )

        window = st.slider("Rolling window (number of readings)", 3, 50, 12, key=f"{key_prefix}_window")
        roll = analysis_df[GLUCOSE_COL].rolling(window).agg(["mean", "std"]).reset_index()

        fig5 = px.line(roll, x=TS_COL, y="mean", title=f"<b>Rolling Mean (window={window}) with ±1 Std Band</b>")
        fig5.add_scatter(
            x=roll[TS_COL], y=roll["mean"] + roll["std"], mode="lines", 
            line=dict(width=0), showlegend=False
        )
        fig5.add_scatter(
            x=roll[TS_COL], y=roll["mean"] - roll["std"], mode="lines", line=dict(width=0),
            fill="tonexty", fillcolor="rgba(255, 140, 0, 0.2)", showlegend=False,
        )
        fig5.update_traces(selector=dict(mode="lines", line_width=2), line_color="darkorange")
        fig5.update_layout(xaxis=dict(rangeslider=dict(visible=True)))
        fig5 = apply_professional_layout(fig5)
        
        st.plotly_chart(fig5, use_container_width=True, key=f"{key_prefix}_trend_chart")

    # Tab 5: Linear Regression
    with ml_tabs[4]:
        st.markdown("#### Linear Regression (Overall Drift)")
        st.markdown(
            """
            <div class="ml-desc">
                <b>Method & Purpose:</b> Fits an ordinary least-squares trend line ($y = mx + b$) to evaluate macro baseline trajectory over time.<br>
                <b>What it measures:</b> Macro-level directional drift rate (mmol/L per hour) and overall fit strength ($R^2$).<br>
                <b>How to read:</b> Slope indicates hourly upward/downward baseline trajectory. Lower $R^2$ values are normal due to short-term meal/insulin oscillations.
            </div>
            """,
            unsafe_allow_html=True
        )

        from sklearn.linear_model import LinearRegression
        from sklearn.metrics import r2_score

        reg_df = analysis_df[[GLUCOSE_COL]].dropna().reset_index()
        t0 = reg_df[TS_COL].min()
        reg_df["minutes_elapsed"] = (reg_df[TS_COL] - t0).dt.total_seconds() / 60.0

        X = reg_df[["minutes_elapsed"]].values
        y = reg_df[GLUCOSE_COL].values

        model = LinearRegression()
        model.fit(X, y)
        reg_df["predicted"] = model.predict(X)

        slope_per_min = model.coef_[0]
        slope_per_hour = slope_per_min * 60
        r2 = r2_score(y, reg_df["predicted"])

        fig6 = px.scatter(
            reg_df,
            x=TS_COL,
            y=GLUCOSE_COL,
            title="<b>Linear Regression Trend Line</b>",
        )
        fig6.update_traces(marker=dict(color="mediumpurple", size=5, opacity=0.6))
        fig6.add_scatter(
            x=reg_df[TS_COL],
            y=reg_df["predicted"],
            mode="lines",
            line=dict(color="indigo", width=4, dash="dash"),
            name="Regression fit",
        )
        fig6.update_layout(
            xaxis_title="Timestamp",
            yaxis_title="Glucose Value (mmol/L)",
            xaxis=dict(rangeslider=dict(visible=True)),
        )
        fig6 = apply_professional_layout(fig6)
        
        st.plotly_chart(fig6, use_container_width=True, key=f"{key_prefix}_regression_chart")

        col_a, col_b = st.columns(2)
        col_a.metric("📐 Slope", f"{slope_per_hour:+.3f} mmol/L per hour")
        col_b.metric("🎯 R² (fit quality)", f"{r2:.3f}")

        if r2 < 0.1:
            st.caption(
                "⚠️ *Low R² — glucose in this range doesn't follow a simple linear "
                "trend (expected for CGM data with meal/insulin cycles). The "
                "slope above still indicates overall drift direction.*"
            )


if uploaded_files:
    tab_labels = []
    for f in uploaded_files:
        meta = extract_patient_metadata(f)
        if meta["first_name"] != "N/A":
            tab_labels.append(f"🧑‍⚕️ {meta['first_name']} {meta['last_name']}")
        else:
            tab_labels.append(f"🧑‍⚕️ {f.name}")

    tabs = st.tabs(tab_labels)
    for idx, (tab, uploaded_file) in enumerate(zip(tabs, uploaded_files)):
        with tab:
            key_prefix = f"p{idx}_{uploaded_file.name}"
            render_patient_view(uploaded_file, key_prefix)
else:
    st.info("👋 Upload one or more CSVs to get started. The data will automatically render here.")