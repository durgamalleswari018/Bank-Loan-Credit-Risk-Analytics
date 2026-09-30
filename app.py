from flask import Flask

app = Flask(__name__)

@app.route("/")
def home():
    return """
    <!DOCTYPE html>
    <html>
    <head>
        <title>Bank Loan & Credit Risk Analytics</title>
        <meta name="viewport" content="width=device-width, initial-scale=1">
        <style>
            body {
                font-family: Arial, sans-serif;
                background: #0B1220;
                color: #F8FAFC;
                margin: 0;
                padding: 40px 20px;
            }

            .container {
                max-width: 900px;
                margin: auto;
            }

            h1 {
                color: #3B82F6;
            }

            .card {
                background: #111C2E;
                padding: 25px;
                margin-top: 20px;
                border-radius: 12px;
                border: 1px solid #1E293B;
            }

            a {
                display: inline-block;
                margin-top: 10px;
                padding: 12px 18px;
                background: #3B82F6;
                color: white;
                text-decoration: none;
                border-radius: 8px;
            }

            a:hover {
                background: #06B6D4;
            }
        </style>
    </head>

    <body>
        <div class="container">

            <h1>Bank Loan & Credit Risk Analytics</h1>

            <div class="card">
                <h2>Project Overview</h2>
                <p>
                    A data analysis project focused on exploring bank loan
                    information and understanding credit risk patterns.
                </p>
            </div>

            <div class="card">
                <h2>Analysis Workflow</h2>
                <p>
                    Data loading → Data cleaning → Exploratory Data Analysis
                    → Risk analysis → Visualization → Insights
                </p>
            </div>

            <div class="card">
                <h2>Python Analysis</h2>
                <p>
                    The complete analysis is available in the original
                    Jupyter Notebook.
                </p>

                <a href="https://github.com/durgamalleswari018/Bank-Loan-Credit-Risk-Analytics/blob/7222047685c844d79bd5b19ee09c9d10fb2e6b45/bank-loan-credit-risk-analytics.ipynb"
                   target="_blank">
                    View Analysis Notebook
                </a>
            </div>

        </div>
    </body>
    </html>
    """

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
