import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import os

st.set_page_config(
    page_title="Bank Loan Credit Risk Analytics",
    page_icon="🏦",
    layout="wide"
)

st.title("🏦 Bank Loan Credit Risk Analytics")
st.caption("Data Analytics Project | Credit Risk & Loan Application Analysis")

# ---------------------------------------------------------
# LOAD DATA
# ---------------------------------------------------------

@st.cache_data
def load_data():

    app_file = "application_data.csv"
    prev_file = "previous_application.csv"
    desc_file = "columns_description.csv"

    if not os.path.exists(app_file):
        st.error(
            "application_data.csv not found. "
            "Add the dataset files to the project or connect the Kaggle dataset."
        )
        st.stop()

    if not os.path.exists(prev_file):
        st.error("previous_application.csv not found.")
        st.stop()

    application = pd.read_csv(app_file)

    previous = pd.read_csv(
        prev_file,
        usecols=[
            "SK_ID_CURR",
            "SK_ID_PREV",
            "NAME_CONTRACT_STATUS",
            "AMT_CREDIT",
            "AMT_ANNUITY"
        ]
    )

    description = None

    if os.path.exists(desc_file):
        description = pd.read_csv(
            desc_file,
            encoding="latin1"
        )

    return application, previous, description


application, previous, description = load_data()

# ---------------------------------------------------------
# CLEAN DATA
# ---------------------------------------------------------

application = application.drop_duplicates()
previous = previous.drop_duplicates()

missing = application.isnull().sum()
missing_percent = (missing / len(application)) * 100

high_missing_cols = missing_percent[
    missing_percent > 50
].index.tolist()

application_clean = application.drop(
    columns=high_missing_cols,
    errors="ignore"
)

# ---------------------------------------------------------
# SIDEBAR
# ---------------------------------------------------------

st.sidebar.title("📊 Dashboard")

page = st.sidebar.radio(
    "Select Analysis",
    [
        "Overview",
        "Risk Analysis",
        "Customer Profile",
        "Loan History",
        "Risk Insights"
    ]
)

# ---------------------------------------------------------
# OVERVIEW
# ---------------------------------------------------------

if page == "Overview":

    st.header("📌 Project Overview")

    col1, col2, col3, col4 = st.columns(4)

    with col1:
        st.metric(
            "Applications",
            f"{len(application_clean):,}"
        )

    with col2:
        st.metric(
            "Previous Loans",
            f"{len(previous):,}"
        )

    with col3:
        st.metric(
            "Original Columns",
            f"{len(application.columns)}"
        )

    with col4:
        st.metric(
            "Cleaned Columns",
            f"{len(application_clean.columns)}"
        )

    st.divider()

    st.subheader("🎯 Loan Risk Distribution")

    target_counts = application_clean["TARGET"].value_counts()

    c1, c2 = st.columns(2)

    with c1:
        st.write("**Target Distribution**")
        st.dataframe(
            target_counts.rename(
                index={
                    0: "Low / No Default",
                    1: "Default"
                }
            )
        )

    with c2:
        fig, ax = plt.subplots(figsize=(6, 4))

        target_counts.plot(
            kind="bar",
            ax=ax
        )

        ax.set_title("Loan Risk Distribution")
        ax.set_xlabel("TARGET")
        ax.set_ylabel("Applications")

        st.pyplot(fig)

    st.subheader("📋 Dataset Preview")

    st.dataframe(
        application_clean.head(10),
        use_container_width=True
    )


# ---------------------------------------------------------
# RISK ANALYSIS
# ---------------------------------------------------------

elif page == "Risk Analysis":

    st.header("⚠️ Credit Risk Analysis")

    target_percent = (
        application_clean["TARGET"]
        .value_counts(normalize=True) * 100
    ).round(2)

    c1, c2 = st.columns(2)

    with c1:
        st.metric(
            "Non-Default %",
            f"{target_percent.get(0, 0):.2f}%"
        )

    with c2:
        st.metric(
            "Default %",
            f"{target_percent.get(1, 0):.2f}%"
        )

    st.divider()

    # Education risk
    st.subheader("🎓 Risk Rate by Education")

    education_risk = (
        pd.crosstab(
            application_clean["NAME_EDUCATION_TYPE"],
            application_clean["TARGET"],
            normalize="index"
        ) * 100
    )

    if 1 in education_risk.columns:

        education_risk = (
            education_risk[1]
            .sort_values(ascending=False)
            .round(2)
        )

        st.bar_chart(education_risk)

        st.dataframe(
            education_risk.rename("Risk Rate %"),
            use_container_width=True
        )

    st.divider()

    # Income risk
    st.subheader("💼 Risk Rate by Income Type")

    income_risk = (
        pd.crosstab(
            application_clean["NAME_INCOME_TYPE"],
            application_clean["TARGET"],
            normalize="index"
        ) * 100
    )

    if 1 in income_risk.columns:

        income_risk = (
            income_risk[1]
            .sort_values(ascending=False)
            .round(2)
        )

        st.bar_chart(income_risk)

        st.dataframe(
            income_risk.rename("Risk Rate %"),
            use_container_width=True
        )


# ---------------------------------------------------------
# CUSTOMER PROFILE
# ---------------------------------------------------------

elif page == "Customer Profile":

    st.header("👤 Customer Risk Profile")

    cols = [
        "AMT_INCOME_TOTAL",
        "DAYS_BIRTH",
        "DAYS_EMPLOYED",
        "AMT_CREDIT",
        "AMT_ANNUITY",
        "CNT_CHILDREN"
    ]

    available_cols = [
        c for c in cols
        if c in application_clean.columns
    ]

    x = application_clean[available_cols + ["TARGET"]].copy()

    if "DAYS_BIRTH" in x.columns:
        x["AGE"] = (
            -x["DAYS_BIRTH"] / 365
        ).round(1)

    if "DAYS_EMPLOYED" in x.columns:
        x["EMPLOYMENT_YEARS"] = (
            -x["DAYS_EMPLOYED"] / 365
        ).clip(lower=0).round(1)

    st.subheader("📊 Customer Metrics by Risk")

    grouped = (
        x.groupby("TARGET")
        .mean()
        .T
        .round(2)
    )

    st.dataframe(
        grouped,
        use_container_width=True
    )

    st.divider()

    # Financial ratios
    st.subheader("💰 Financial Risk Ratios")

    ratio_cols = [
        "AMT_INCOME_TOTAL",
        "AMT_CREDIT",
        "AMT_ANNUITY",
        "TARGET"
    ]

    ratio_data = application_clean[
        ratio_cols
    ].copy()

    ratio_data["CREDIT_INCOME_RATIO"] = (
        ratio_data["AMT_CREDIT"] /
        ratio_data["AMT_INCOME_TOTAL"]
    )

    ratio_data["ANNUITY_INCOME_RATIO"] = (
        ratio_data["AMT_ANNUITY"] /
        ratio_data["AMT_INCOME_TOTAL"]
    )

    ratio_summary = (
        ratio_data
        .groupby("TARGET")[
            [
                "AMT_INCOME_TOTAL",
                "AMT_CREDIT",
                "AMT_ANNUITY",
                "CREDIT_INCOME_RATIO",
                "ANNUITY_INCOME_RATIO"
            ]
        ]
        .mean()
        .round(3)
    )

    st.dataframe(
        ratio_summary,
        use_container_width=True
    )


# ---------------------------------------------------------
# LOAN HISTORY
# ---------------------------------------------------------

elif page == "Loan History":

    st.header("🏦 Previous Loan History")

    status_counts = (
        previous["NAME_CONTRACT_STATUS"]
        .value_counts()
    )

    c1, c2 = st.columns(2)

    with c1:
        st.subheader("Loan Status Distribution")

        st.bar_chart(status_counts)

    with c2:
        st.subheader("Loan Status %")

        status_percent = (
            previous["NAME_CONTRACT_STATUS"]
            .value_counts(normalize=True) * 100
        ).round(2)

        st.dataframe(
            status_percent.rename("Percentage"),
            use_container_width=True
        )

    st.divider()

    st.subheader("📋 Previous Loan Summary")

    history = (
        previous
        .groupby("NAME_CONTRACT_STATUS")
        .agg(
            Applications=("SK_ID_PREV", "count"),
            Avg_Credit=("AMT_CREDIT", "mean"),
            Avg_Annuity=("AMT_ANNUITY", "mean")
        )
        .round(2)
        .sort_values(
            "Applications",
            ascending=False
        )
    )

    st.dataframe(
        history,
        use_container_width=True
    )

    st.divider()

    # Customer previous loan summary
    prev_summary = (
        previous
        .groupby("SK_ID_CURR")
        .agg(
            PREV_LOANS=("SK_ID_PREV", "count"),
            APPROVED=(
                "NAME_CONTRACT_STATUS",
                lambda x: (x == "Approved").sum()
            ),
            REFUSED=(
                "NAME_CONTRACT_STATUS",
                lambda x: (x == "Refused").sum()
            ),
            AVG_PREV_CREDIT=("AMT_CREDIT", "mean")
        )
        .reset_index()
    )

    risk = (
        application_clean[
            ["SK_ID_CURR", "TARGET"]
        ]
        .merge(
            prev_summary,
            on="SK_ID_CURR",
            how="left"
        )
        .fillna(0)
    )

    risk["APPROVAL_RATE"] = (
        risk["APPROVED"] /
        risk["PREV_LOANS"].replace(0, 1) *
        100
    ).round(2)

    st.subheader("📈 Previous Loan Behaviour by Risk")

    risk_summary = (
        risk
        .groupby("TARGET")[
            [
                "PREV_LOANS",
                "APPROVED",
                "REFUSED",
                "AVG_PREV_CREDIT",
                "APPROVAL_RATE"
            ]
        ]
        .mean()
        .round(2)
    )

    st.dataframe(
        risk_summary,
        use_container_width=True
    )
elif page == "Risk Insights":

    st.header("💡 Risk Insights")

    st.markdown("""
    ### Key Analytical Areas

    **1. Loan Risk Distribution**
    
    TARGET = 1 represents customers with repayment difficulties,
    while TARGET = 0 represents customers without repayment difficulties.

    **2. Customer Profile**
    
    Income, age, employment duration, credit amount and annuity
    can be compared across risk groups.

    **3. Education & Income**
    
    Risk rates can be examined across education and income categories.

    **4. Financial Ratios**
    
    Credit-to-income and annuity-to-income ratios provide additional
    financial indicators.

    **5. Previous Loan Behaviour**
    
    Previous applications can be analysed through approved,
    refused and other contract statuses.

    **6. Approval Behaviour**
    
    Previous loan history can be connected with current application
    risk using SK_ID_CURR.
    """)

    st.divider()

    st.subheader("📊 Data Quality")

    c1, c2, c3 = st.columns(3)

    with c1:
        st.metric(
            "Missing Values",
            f"{application_clean.isnull().sum().sum():,}"
        )

    with c2:
        st.metric(
            "Duplicate Rows",
            f"{application_clean.duplicated().sum():,}"
        )

    with c3:
        st.metric(
            "High-Missing Columns Removed",
            f"{len(high_missing_cols):,}"
        )

    st.success(
        "Dashboard generated from the Bank Loan Credit Risk Analytics dataset."
  )
