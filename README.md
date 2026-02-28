# 💉 ADC Manufacturing Intelligence Dashboard

An interactive manufacturing intelligence dashboard for Antibody-Drug Conjugate (ADC) production, built with Python, Streamlit and PostgreSQL. Designed to reflect the real operational data needs of CDMO and biotech manufacturing teams.

🔗 **[Live Dashboard](https://adc-manufacturing-dashboard.streamlit.app/)**

---

<img width="1552" height="901" alt="Screenshot 2026-02-28 at 07 08 37" src="https://github.com/user-attachments/assets/adff587b-b546-4c9c-ab73-d20017b5fa54" />


---

## 📋 Project Overview

ADC manufacturing generates complex, multi-dimensional process data across bioconjugation, purification, and analytical testing. This dashboard centralises that data into an accessible intelligence tool — surfacing batch trends, out-of-spec results, yield patterns, and raw material traceability in a single interface.

Built as a portfolio project by a pharmaceutical manufacturing professional transitioning into data engineering. The dataset is synthetic but modelled on real ADC manufacturing parameters including realistic DAR distributions, SEC purity thresholds, endotoxin limits, and conjugation yield ranges.

---

## 🖥️ Dashboard Pages

| Page | Description |
|---|---|
| **Batch Overview** | KPI summary, filterable batch records table with pass/fail status |
| **Process Analytics** | Conjugation yield and purification recovery trends across batches |
| **DAR & Quality Metrics** | Drug-to-antibody ratio distribution, SEC purity, endotoxin and bioburden |
| **Raw Materials** | Lot number traceability linking materials to batch records |
| **Deviations** | QA deviation log with severity classification and status tracking |

---

## 🛠️ Tech Stack

| Tool | Purpose |
|---|---|
| Python 3.14 | Core language |
| Streamlit | Dashboard framework |
| PostgreSQL | Database backend |
| psycopg2 | PostgreSQL connector |
| pandas | Data manipulation |
| Plotly | Interactive visualisations |

---

## 🗄️ Database Schema

Database: `adc_manufacturing`

Three schemas reflecting real CDMO data warehouse domain separation:

```
adc_manufacturing
├── manufacturing
│   ├── batches            # Master batch records
│   ├── bioconjugation     # Conjugation process parameters
│   ├── purification       # TFF/UF purification data
│   └── raw_materials      # Material lot traceability
├── analytical
│   └── analytical_results # DAR, SEC, endotoxin, bioburden
└── quality
    └── deviations         # QA deviation log
```

**Key specifications modelled:**
- DAR specification window: 3.0 – 4.5
- SEC purity minimum: 95.0%
- Endotoxin limit: 1.0 EU/mL
- ~10% of batches seeded as outliers to simulate real process variability

---

## 📸 Screenshots

### Batch Overview
<img width="1552" height="901" alt="Screenshot 2026-02-28 at 07 11 21" src="https://github.com/user-attachments/assets/de58fdfb-4e44-452d-83f6-0914175ae6cd" />


### Process Analytics
<img width="1552" height="901" alt="Screenshot 2026-02-28 at 07 12 51" src="https://github.com/user-attachments/assets/8315ad26-ec65-4c8e-9910-aefb8dcbb8eb" />
<img width="1552" height="901" alt="Screenshot 2026-02-28 at 07 13 01" src="https://github.com/user-attachments/assets/fbc13359-d5aa-4e14-b84c-2f7835f18350" />
<img width="1552" height="901" alt="Screenshot 2026-02-28 at 07 13 10" src="https://github.com/user-attachments/assets/922ca746-7557-4bc4-a6d6-fb2c107ba590" />


### DAR & Quality Metrics
<img width="1552" height="901" alt="Screenshot 2026-02-28 at 07 14 30" src="https://github.com/user-attachments/assets/3e41ec5f-df25-4a4c-bbfc-0bc6b45bf9e4" />
<img width="1552" height="901" alt="Screenshot 2026-02-28 at 07 14 37" src="https://github.com/user-attachments/assets/b017442c-8222-4871-b43a-0d67729beb2f" />
<img width="1552" height="901" alt="Screenshot 2026-02-28 at 07 14 49" src="https://github.com/user-attachments/assets/4a81a27f-0136-498b-92eb-f90cdb992950" />
<img width="1552" height="901" alt="Screenshot 2026-02-28 at 07 14 59" src="https://github.com/user-attachments/assets/3510af5e-96b1-42e3-aaa0-a39d285c4803" />


### Deviations Log
<img width="1552" height="901" alt="Screenshot 2026-02-28 at 07 15 08" src="https://github.com/user-attachments/assets/5762c174-6e87-473f-b2b8-73fbbd6cf0ef" />


---

## 🚀 Run Locally

### Prerequisites
- Python 3.9+
- PostgreSQL
- Git

### Setup

```bash
# Clone the repository
git clone https://github.com/rorymoir/adc-manufacturing-dashboard.git
cd adc-manufacturing-dashboard

# Create and activate virtual environment
python3 -m venv venv
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Generate synthetic dataset
python generate_data.py

# Set up database
psql -d adc_manufacturing -f create_tables.sql
python load_data.py

# Launch dashboard
streamlit run app.py
```

### Database Configuration

Update the connection details in `app.py` to match your PostgreSQL setup:

```python
conn = psycopg2.connect(
    dbname="adc_manufacturing",
    user="your_username",
    password="your_password",
    host="localhost",
    port="5432"
)
```

---

## 📁 Project Structure

```
adc-manufacturing-dashboard/
├── app.py                  # Main Streamlit application
├── generate_data.py        # Synthetic dataset generator
├── load_data.py            # ETL pipeline (CSV → PostgreSQL)
├── create_tables.sql       # Database schema
├── requirements.txt        # Python dependencies
├── screenshots/            # Dashboard screenshots
└── README.md
```

---

## 📊 Dataset

All data is synthetic and generated programmatically. No real patient, batch, or proprietary manufacturing data is used. The dataset is designed to be statistically realistic based on published ADC manufacturing parameters.

**Dataset summary:**
- 60 batches across 3 ADC products (HER2-MMAE, TROP2-DXd, CD30-MMAE)
- 550 total database records across 6 tables
- Date range: January – December 2023

---

## 👤 About

Built by **Rory Moir** — pharmaceutical manufacturing professional with experience in ADC manufacturing, transitioning into data engineering.

This is Project 3 of my data engineering portfolio, combining domain expertise in pharmaceutical manufacturing with Python, SQL, and data visualisation skills.


---

## 📄 Licence

MIT Licence — free to use, adapt, and build upon with attribution.
