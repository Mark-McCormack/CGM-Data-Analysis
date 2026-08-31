# CGM Glucose Viewer 🩸

CGM Glucose Viewer is an interactive Streamlit dashboard designed for multi-patient Continuous Glucose Monitoring (CGM) analysis. It automatically extracts sensor metadata, visualizes glucose trends over customizable date ranges, and applies advanced machine learning algorithms to detect anomalies, cluster physiological states, and analyze circadian patterns.

## ✨ Key Features

* **Multi-Patient Support:** Upload multiple CGM CSV files simultaneously, with each patient displayed in a dedicated tab.
* **Automatic Metadata Extraction:** Automatically parses patient name, date of birth, device model, and sensor type from CSV header rows.
* **Smart Data Parsing:** Pre-configured to bypass 9 header metadata rows and cleanly ingest sensor readouts.
* **Interactive Main Visualizations:** Plotly line charts with range sliders, interactive date range controls, and metric summaries (Mean, Min, Max).
* **Independent ML Date Filtering:** Dedicated time-window slider specifically for ML algorithms to isolate specific days or weeks.
* **5 Machine Learning & Statistical Tools:**
  * **Isolation Forest:** Flag unusual glucose spikes, drops, or reading anomalies.
  * **K-Means Clustering:** Group physiological states using glucose levels and rate of change (ROC).
  * **Fast Fourier Transform (FFT):** Discover repeating circadian rhythms and meal cycles in the frequency domain.
  * **Rolling Trend Analysis:** Compute moving averages with $\pm 1\text{ Std}$ volatility bands.
  * **Linear Regression:** Evaluate baseline drift rate (mmol/L per hour) and regression fit ($R^2$).
* **In-App Method Guidance:** Clear methodological explanations for each ML tab detailing how the algorithm works and what it measures.

---

## 🚀 Getting Started

Follow these simple step-by-step instructions to get the app running on your computer.

### Step 1: Download the Project

1. Click the green **Code** button near the top right of this page.
2. Click **Download ZIP**.
3. Open your computer's `Downloads` folder, double-click the file, and extract/unzip the folder.

---

### Step 2: Open Your Command Terminal

* **Windows:** Press the `Windows Key`, type `cmd` or `PowerShell`, and press **Enter**.
* **Mac:** Press `Cmd + Space`, type `Terminal`, and press **Enter**.

---

### Step 3: Navigate to the Project Folder

Type `cd ` (with a space after it), then drag and drop your extracted folder directly into the terminal window, or copy and paste:

* **Windows:**
  ```cmd
  cd %USERPROFILE%\Downloads\cgm-glucose-analysis-main

```

* **Mac:**
```bash
cd ~/Downloads/cgm-glucose-analysis-main

```



---

### Step 4: Install Dependencies

Paste the appropriate command into your terminal and press **Enter**:

* **Windows:**
```cmd
pip install -r requirements.txt

```


* **Mac:**
```bash
pip3 install -r requirements.txt

```



*(If Python is missing, download it from [python.org](https://www.python.org/downloads/). Ensure you check the box that says "Add Python to PATH" during installation on Windows).*

---

### Step 5: Run the App

Launch the application by running:

* **Windows:**
```cmd
streamlit run main.py

```


* **Mac:**
```bash
python3 -m streamlit run main.py

```



Your browser will automatically pop open to **`http://localhost:8501`** with the dashboard ready to use!

---

## 🛠️ Project Setup & Dependencies

If creating `requirements.txt` manually, include the following dependencies:

```text
streamlit
pandas
numpy
plotly
scikit-learn
scipy

```

*Note: On macOS systems, the app automatically configures environment variables to prevent potential `joblib`/`scikit-learn` CPU auto-detection issues during K-Means clustering.*

---

## 📁 Supported CSV Format

The application expects CGM CSV files structured as follows:

* **Metadata Header (Rows 1–9):**
* Row 2, Column E: Patient First Name
* Row 3, Column E: Patient Last Name
* Row 4, Column E: Patient Birthday
* Row 5, Column F: Device Typename
* Row 6, Column F: Sensor Type


* **Data Rows (Row 10 onward):** Automatically skipped past row 9 with expected columns including:
* `Timestamp (YYYY-MM-DDThh:mm:ss)`
* `Glucose Value (mmol/L)`
* `Glucose Rate of Change (mmol/L/min)`



---

## 🧠 Machine Learning Overview

| Method | Focus & Measurement | Key Output |
| --- | --- | --- |
| **Isolation Forest** | Statistical outlier detection | Anomalous reading points |
| **K-Means Clustering** | Multi-variable state grouping | Cluster centroids & scatter plot |
| **FFT Periodicity** | Frequency domain cycle detection | Peak power spectral hours (e.g., 24h, 4h) |
| **Rolling Trend** | Short-term volatility and direction | Moving average band ($\pm 1\text{ Std}$) |
| **Linear Regression** | Macro baseline trajectory | Drift rate (mmol/L per hr) & $R^2$ fit |

---

## 📂 Project Structure

* `main.py` — main Streamlit application containing CSV parsing, tab layout, interactive charts, and ML algorithms
* `requirements.txt` — Python dependencies
* `README.md` — project documentation and setup instructions

Enjoy analyzing your CGM data to uncover deeper physiological insights! 🩸📈
