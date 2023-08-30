import os
import argparse

import boto3
import kaggle
import pandas as pd

DATA_PATH = os.environ.get("DATA_PATH", "../../data")
ARTIFACT_BUCKET_NAME = os.environ.get("ARTIFACT_BUCKET_NAME", "artifacts-and-data-bp")
REFERENCE_DATA_KEY_PATH = os.environ.get(
    "REFERENCE_DATA_KEY_PATH", "default_reference_data_key_path"
)


def download_kaggle_dataset(username, key, data_path=DATA_PATH):
    os.environ['KAGGLE_USERNAME'] = username
    os.environ['KAGGLE_KEY'] = key
    kaggle.api.dataset_download_files(
        'utkarshx27/lending-club-loan-dataset', path=data_path, unzip=True
    )


def upload_to_s3(filename, destination_path, bucket_name=ARTIFACT_BUCKET_NAME):
    s3 = boto3.client('s3')
    s3.upload_file(
        filename,
        bucket_name,
        os.path.join(destination_path, os.path.basename(filename)),
    )


def clean_and_process_data(df):
    df2 = df.drop(
        columns=[
            'annual_income_joint',
            'verification_income_joint',
            'debt_to_income_joint',
        ]
    )
    columns_to_impute = [
        'emp_length',
        'debt_to_income',
        'months_since_last_delinq',
        'months_since_90d_late',
        'months_since_last_credit_inquiry',
    ]

    for column in columns_to_impute:
        median_value = df2[column].median()
        df2[column].fillna(median_value, inplace=True)

    df2['emp_title'] = df2['emp_title'].fillna('unemployed')
    df2['num_accounts_120d_past_due'] = df2['num_accounts_120d_past_due'].fillna(0)
    df2['loan_status'].replace(
        {
            'In Grace Period': 'Late',
            'Late (31-120 days)': 'Late',
            'Late (16-30 days)': 'Late',
        },
        inplace=True,
    )
    df2['loan_status'] = (df2['loan_status'] == 'Charged Off').astype(int)

    return df2


def main(args):
    download_kaggle_dataset(args.username, args.key)

    # Load data
    df = pd.read_csv(os.path.join(DATA_PATH, 'loans_full_schema.csv'), index_col=0)

    # Clean and process data
    df_cleaned = clean_and_process_data(df)

    # Save cleaned data locally first
    local_filename = os.path.join(DATA_PATH, 'loans_full_schema_clean.parquet')
    df_cleaned.to_parquet(local_filename, index=None)

    # Then upload cleaned data to S3
    upload_to_s3(local_filename, REFERENCE_DATA_KEY_PATH)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Download and process Lending Club Loan dataset from Kaggle"
    )
    parser.add_argument("--username", required=True, help="Your Kaggle username")
    parser.add_argument("--key", required=True, help="Your Kaggle API key")

    args = parser.parse_args()
    main(args)
