# Employee Performance and Salary Analytics System

A full-stack starter project based on the supplied project outline. It uses **Python, Flask, SQLite, HTML, CSS, and Chart.js**.

## Features
- Dashboard cards for employee count, average performance, average annual salary, and high performers.
- Employee records with add, edit, and delete operations.
- Search by employee name, employee code, or role.
- Filter records by department.
- Performance score chart and average salary by department chart.
- Department summaries and productivity metrics.
- Export all employee records to CSV.
- SQLite database created automatically with sample data on first run.
- Input validation and duplicate employee-code handling.

## Requirements
- Python 3.10 or later
- Internet access for the Chart.js and Google Fonts CDN assets (the application itself runs locally).

## Run on Windows
1. Extract the ZIP file.
2. Open the extracted project folder in VS Code.
3. Open Terminal in that folder.
4. Create a virtual environment (optional but recommended):

   ```bash
   python -m venv .venv
   .venv\\Scripts\\activate
   ```

5. Install dependencies:

   ```bash
   pip install -r requirements.txt
   ```

6. Start the app:

   ```bash
   python app.py
   ```

7. Open http://127.0.0.1:5000 in your browser.

## Run on macOS/Linux
```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
python app.py
```

## Project structure
```text
Employee_Performance_and_Salary_Analytics_System/
├── app.py
├── requirements.txt
├── README.md
├── templates/
│   ├── base.html
│   ├── dashboard.html
│   └── employee_form.html
├── static/
│   └── style.css
└── data/
    └── employees.db   # created automatically on first launch
```

## Data fields
- Employee code
- Name
- Department
- Role / job title
- Annual salary in INR
- Performance score (0–100)
- Productivity score (0–100)
- Review date

The included names and figures are fictional sample data. Replace them with authorized data before using this for a real organization.

## Notes
- This is a learning/demo project, not a production HR system.
- Before deploying publicly, replace the Flask secret key, disable debug mode, add authentication and authorization, configure backups, and review privacy/security requirements.
- Performance and salary summaries are descriptive analytics; they should not be used as the sole basis for employment or compensation decisions.
