import pandas as pd
from flask import Response, Flask

app = Flask(__name__)

df = pd.DataFrame({
    'Month': [],  # Add month data
    'Expense': [],  # Add expense categories
    'Amount(R)': []  # Add amount values
})

# First check if the column exists, and if not, use the Rands version
amount_column = 'Amount(R)' if 'Amount(R)' in df.columns else 'Amount(R)'

def prepare_analysis_data(df):
    try:
        # Check required columns
        required_cols = {'Month', 'Expense', 'Amount(R)'}
        if not required_cols.issubset(df.columns):
            missing = required_cols - set(df.columns)
            raise ValueError(f"Missing required columns: {missing}")
        
        # Clean data
        df = df.dropna(subset=['Month', 'Expense', 'Amount(R)'])
        df['Amount(R)'] = pd.to_numeric(df['Amount(R)'], errors='coerce')
        
        # Group and analyze
        analysis_data = df.groupby(['Month', 'Expense'], as_index=False)['Amount(R)'].sum()
        
        return analysis_data
    except Exception as e:
        print(f"Error in analysis preparation: {str(e)}")
        return pd.DataFrame(columns=['Month', 'Expense', 'Amount(R)'])

t = prepare_analysis_data(df)

print(t)

@app.route('/download-analysis')
def download_analysis():
    try:
        analysis_data = prepare_analysis_data(df)
        csv = analysis_data.to_csv(index=False)
        return Response(
            csv,
            mimetype="text/csv",
            headers={"Content-disposition": "attachment; filename=analysis.csv"}
        )
    except Exception as e:
        return str(e), 500

        return str(e), 500
