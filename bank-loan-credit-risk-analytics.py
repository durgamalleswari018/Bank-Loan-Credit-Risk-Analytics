import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

application = pd.read_csv("/kaggle/input/datasets/durgamalleswaris/project/application_data.csv")
previous = pd.read_csv("/kaggle/input/datasets/durgamalleswaris/project/previous_application.csv")
description = pd.read_csv(
    "/kaggle/input/datasets/durgamalleswaris/project/columns_description.csv",
    encoding="latin1"
)

print("Application:", application.shape)
print("Previous Application:", previous.shape)
print("Description:", description.shape)

print("APPLICATION DATA")
display(application.head())

print("\nPREVIOUS APPLICATION DATA")
display(previous.head())

print("\nDESCRIPTION DATA")
display(description.head())

print("Application columns:")
print(application.columns.tolist())

print("\nPrevious Application columns:")
print(previous.columns.tolist())

print("Missing values in Application:")
print(application.isnull().sum().sort_values(ascending=False).head(20))

print("\nMissing values in Previous Application:")
print(previous.isnull().sum().sort_values(ascending=False).head(20))

print("Application duplicate rows:", application.duplicated().sum())
print("Previous Application duplicate rows:", previous.duplicated().sum())
application = application.drop_duplicates()
previous = previous.drop_duplicates()

print("Application shape:", application.shape)
print("Previous Application shape:", previous.shape)

print(application["TARGET"].value_counts())
print(application["TARGET"].value_counts(normalize=True) * 100)


missing = application.isnull().sum()
missing_percent = (missing / len(application)) * 100

missing_table = pd.DataFrame({
    "Missing Count": missing,
    "Missing Percentage": missing_percent
})

missing_table = missing_table[
    missing_table["Missing Count"] > 0
].sort_values("Missing Percentage", ascending=False)

display(missing_table.head(20))

print("Total columns:", len(application.columns))

print("\nColumns with more than 50% missing values:")
print(
    missing_table[missing_table["Missing Percentage"] > 50].index.tolist()
)


high_missing_cols = missing_table[
    missing_table["Missing Percentage"] > 50
].index.tolist()

print("Columns to remove:", high_missing_cols)
print("Number of columns:", len(high_missing_cols))
application_clean = application.drop(columns=high_missing_cols)
print("Original shape:", application.shape)
print("Cleaned shape:", application_clean.shape)


print(f"Shape: {application_clean.shape}\n")
print("Target distribution:\n", application_clean["TARGET"].value_counts())
print("\nTarget %:\n", (application_clean["TARGET"].value_counts(normalize=True)*100).round(2))
print("\nData types:\n", application_clean.dtypes.value_counts())
print(f"\nTotal missing values: {application_clean.isnull().sum().sum():,}")
print(f"Duplicate rows: {application_clean.duplicated().sum():,}")
display(application_clean.describe(include="all").T.head(15))

cols = ["AMT_INCOME_TOTAL","DAYS_BIRTH","DAYS_EMPLOYED","AMT_CREDIT","AMT_ANNUITY","CNT_CHILDREN"]
x = application_clean[cols].copy()
x["AGE"] = (-x.DAYS_BIRTH/365).round(1)
x["EMPLOYMENT_YEARS"] = (-x.DAYS_EMPLOYED/365).clip(lower=0).round(1)
display(x.groupby(application_clean["TARGET"]).mean().T.round(2))

cols = ["NAME_EDUCATION_TYPE","NAME_INCOME_TYPE","NAME_FAMILY_STATUS","NAME_HOUSING_TYPE"]
for c in cols:
    print(f"\n📊 Risk by {c}")
    display((pd.crosstab(application_clean[c], application_clean["TARGET"], normalize="index")*100).round(2))

x = application_clean[["AMT_INCOME_TOTAL","AMT_CREDIT","AMT_ANNUITY","TARGET"]].copy()
x["CREDIT_INCOME_RATIO"] = x["AMT_CREDIT"] / x["AMT_INCOME_TOTAL"]
x["ANNUITY_INCOME_RATIO"] = x["AMT_ANNUITY"] / x["AMT_INCOME_TOTAL"]
display(x.groupby("TARGET")[["AMT_INCOME_TOTAL","AMT_CREDIT","AMT_ANNUITY",
                              "CREDIT_INCOME_RATIO","ANNUITY_INCOME_RATIO"]].mean().round(3))


print("Loan Status %:\n",
      (previous["NAME_CONTRACT_STATUS"].value_counts(normalize=True)*100).round(2))

history = previous.groupby("NAME_CONTRACT_STATUS").agg(
    Applications=("SK_ID_PREV","count"),
    Avg_Credit=("AMT_CREDIT","mean"),
    Avg_Annuity=("AMT_ANNUITY","mean")
).round(2)

display(history.sort_values("Applications", ascending=False))


prev_summary = previous.groupby("SK_ID_CURR").agg(
    PREV_LOANS=("SK_ID_PREV","count"),
    APPROVED=("NAME_CONTRACT_STATUS",lambda x:(x=="Approved").sum()),
    REFUSED=("NAME_CONTRACT_STATUS",lambda x:(x=="Refused").sum()),
    AVG_PREV_CREDIT=("AMT_CREDIT","mean")
).reset_index()

risk = application_clean[["SK_ID_CURR","TARGET"]].merge(prev_summary,on="SK_ID_CURR",how="left").fillna(0)
risk["APPROVAL_RATE"] = (risk["APPROVED"]/risk["PREV_LOANS"].replace(0,1)*100).round(2)

display(risk.groupby("TARGET")[["PREV_LOANS","APPROVED","REFUSED","AVG_PREV_CREDIT","APPROVAL_RATE"]].mean().round(2))

import matplotlib.pyplot as plt

fig, ax = plt.subplots(2, 2, figsize=(12, 8))

application_clean["TARGET"].value_counts().plot(kind="bar", ax=ax[0,0])
ax[0,0].set_title("Loan Risk Distribution")

pd.crosstab(application_clean["NAME_EDUCATION_TYPE"], application_clean["TARGET"],
normalize="index")[1].mul(100).sort_values().plot(kind="barh", ax=ax[0,1])
ax[0,1].set_title("Risk Rate by Education")
ax[0,1].set_xlabel("Risk %")

pd.crosstab(application_clean["NAME_INCOME_TYPE"], application_clean["TARGET"],
normalize="index")[1].mul(100).sort_values().plot(kind="barh", ax=ax[1,0])
ax[1,0].set_title("Risk Rate by Income Type")
ax[1,0].set_xlabel("Risk %")

previous["NAME_CONTRACT_STATUS"].value_counts().plot(kind="bar", ax=ax[1,1])
ax[1,1].set_title("Previous Loan Status")

plt.tight_layout()
plt.show()

