"""
Author: Ryan Kroker (ryan.kroker@gmail.com)
Version: 1.0
Created: 3-23-2026
Last Updated: 4-2-2026
Purpose: Parses uploaded CSV files and normalizes their columns for downstream processing.
"""

import pandas as pd


def load_csv_file(file_path):
    return pd.read_csv(file_path)


def normalize_columns(df):
    df.columns = [col.strip().lower() for col in df.columns]
    df = df.fillna("")
    return df