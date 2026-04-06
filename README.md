# Real Estate Analytics Project
(Work in Progress)

## Overview
This project analyzes real estate property data to identify trends in
pricing, location demand and investment opportunities.

The project demonstrates skills in:
- Python
- Pandas
- SQL
- VBA
- Data Visualization
- ETL pipelines

## Current automation status:
- Pricing_Comparison: automated
- Revenue_Summary: planned
- Occupancy_Trends: planned
- Expense_Analysis: planned

## Project Structure

real-estate-analytics/
│
├── data/
│   ├── raw
│   └── processed
│
|__ database/
|     schema.sql
|
|__ etl/
│     extract.py
│     transform.py
│     load.py
|
|__ notebooks/
│     occupancy_analysis.ipynb: planned
|     revenue_analysis.ipynb: planned
│
|__ Real Estate Analytics
|     Real_Estate_Dashboard.xslx
|     Real_Estate_Dashboard_Template.xslx
|     Real_Estate_Dashboard_Template.xslm
|     Rent_Pricing_Analysis_Report.docx
|
|── scripts/
|     clear_output_files.py
|     generate_synthetic_data.py
│
|__ setup_env.bat
|__ run_portfolio.py
|__ requirements.txt
|__ README.md
└── run_jupyter.bat

## Installation

Clone the repository

```bash
git clone https://github.com/yourusername/real-estate-analytics.git
cd real-estate-analytics
```

# Setup

### 1. Create virtual environment

```bash
python -m venv venv
```

### 1a. Check libraries

Run:
   setup_env.bat


### 2. Activate the Windows environment

```bash
venv\Scripts\activate
```

###  2a. Activate the Mac/Linux environment

```bash
source venv\Scripts\activate
``` 


### 3. Install dependencies

#### Base environment
```bash
pip install -r requirements.txt
```

#### For exact environment:
```bash
pip install -r requirements-lock.txt
```

#### For dev environment:
```bash
pip install -r requirements-dev.txt
```

## Install SQLite ODBC Driver 
This driver is required to connect to Python SQLite database
from Excel to load the processed data

Go to https://www.ch-werner.de/sqliteodbc/ 
Download the appropriate SQLite ODBC driver for your environment


## Create C:\Temp dir 
Create a directory on the C:\ called \Temp.
It is necessary to run this project from the C:\Temp directory 
to avoid auto-saving that occurs with OneDrive.  
This will prevent the Template file from being overwritten and
remaining in it's original state.


## How to Run the Project

### 1. Install dependencies
pip install -r requirements.txt

### 2. Run the full pipeline 
python run_portfolio.py

### 3.  Excel prompts

1st prompt:  After a few minutes Go to Excel icon on the status bar that will be blinking.  
Click  “No” to not save  C:\Temp\Real_Estate_Dashboard_Template.xlsm.  

2nd prompt:  Click  “Yes” to save or replace existing  C:\Temp\Real_Estate_Dashboard.xlsx.  

Then open C:\Temp\Real_Estate_Dashboard.xlsx and review the Dashboard sheet.


This will:
- generate synthetic real estate data
- process and transform datasets
- save outputs to Real Estate Analysis
- load data into SQLite database
- format Excel dashboard


## Data Disclaimer

All datasets used in this project are synthetic and generated for educational and portfolio purposes.  
No real tenant, financial, or property data is used.

## Work Flow Diagram 
Raw Data (CSV)
   ↓
Extract (Python)
   ↓
Transform (Pandas)
   ↓
Load (SQLite / CSV)
   ↓
Analysis (Jupyter)
   ↓
Dashboard (Excel)


## Analysis Deliverables

This project includes business-focused outputs:

- **Rent Pricing Analysis Report (Word)**  
  Located in: `Real Estate Analysis/Rent_Pricing_Analysis_Report.docx`  
  Contains pricing evaluation, insights, and recommendations.

- **Excel Dashboard Template**  
  Located in: `Real Estate Analysis/Real_Estate_Dashboard_Template.xlsx`  
  Includes rent comparison analysis, charts, and structured reporting outputs.



## Rent Pricing Analysis

### Key Questions & Insights

**1. Are our rental units priced competitively?**  
Most units are priced below market, indicating an opportunity to increase rental income.

**2. Which units are underpriced?**  
2–3 bedroom units show the largest rent gaps and highest revenue potential.

**3. Are any units overpriced?**  
Studio units appear above market, which may impact demand.

### Recommendations

- Adjust pricing for larger units  
- Monitor studio competitiveness  
- Implement data-driven pricing strategy  

