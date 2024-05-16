import os
import pandas as pd
import numpy as np
from datetime import datetime
import streamlit as st
import base64
import joblib
import pickle

pd.set_option('display.float_format', '{:.2f}'.format)

# Read the data into DataFrame 'dfn'
dfn = pd.read_csv('https://github.com/booluckgmie/sharecode/raw/master/data/indv_stats.csv')

# Select the first 26 columns of the DataFrame
df2 = dfn.iloc[:, :26]

# Define the mapping dictionary for states
state_mapping = {
    1.0: 'JOHOR',
    2.0: 'KEDAH',
    3.0: 'KELANTAN',
    4.0: 'MELAKA',
    5.0: 'NEGERI SEMBILAN',
    6.0: 'PAHANG',
    7.0: 'PULAU PINANG',
    8.0: 'PERAK',
    9.0: 'PERLIS',
    10.0: 'SELANGOR',
    11.0: 'TERENGGANU',
    12.0: 'SABAH',
    13.0: 'SARAWAK',
    14.0: 'W.P. KUALA LUMPUR',
    15.0: 'W.P. LABUAN',
    16.0: 'W.P. PUTRAJAYA'
}

# Map the values in the 'NEGERI_SEMASA' column to their corresponding state names
df2['NEGERI_SEMASA'] = dfn['NEGERI_SEMASA'].map(state_mapping)

## mapping district
# Read the 'code_district.csv' file to get the mapping between district codes and district names
district_code = pd.read_csv('https://github.com/booluckgmie/sharecode/raw/master/data/code_district.csv')

# Create a dictionary from the DataFrame 'district_code' where district codes are keys and district names are values
district_mapping = dict(zip(district_code['code_district'], district_code['district']))

# Map the district codes to district names and populate the 'DAERAH_SEMASA' column in DataFrame 'df2'
df2['DAERAH_SEMASA'] = dfn['DAERAH_SEMASA'].map(district_mapping)

## mapping strata
# Define the mapping dictionary for states
strata_mapping = {
    1.0: 'BANDAR',
    2.0: 'LUAR BANDAR'
}

df2['STRATA_SEMASA'] = dfn['STRATA_SEMASA'].map(strata_mapping)

## mapping jantina
# Define the mapping dictionary for jantina
gender_mapping = {
    1.0: 'LELAKI',
    2.0: 'PEREMPUAN'
}

df2['JANTINA'] = dfn['JANTINA'].map(gender_mapping)

# Display the first few rows of DataFrame 'df2'
# st.write(df2.head())

# Assuming df2 is your DataFrame
contains_slash_or_bracket = df2['DAERAH_SEMASA'].str.contains(r'[/()]', na=False)

# Filter the DataFrame based on the condition
df_filtered = df2[contains_slash_or_bracket]

# Display the filtered DataFrame
# st.write(df_filtered)

# Assuming df2 is your DataFrame
replace_dict = {
    'W.P. KUALA LUMPUR': 'W.P. Kuala Lumpur',
    'W.P. PUTRAJAYA': 'W.P. Putrajaya',
    'W.P. LABUAN': 'W.P. Labuan'
}

df2['DAERAH_SEMASA'] = df2['DAERAH_SEMASA'].replace(replace_dict)

# Display unique values of 'DAERAH_SEMASA'
# st.write(df2['DAERAH_SEMASA'].unique())

# Assuming df2 is your DataFrame
df2['DAERAH_SEMASA'] = df2['DAERAH_SEMASA'].str.split(r'[/()]').str.get(0)

# Display the updated DataFrame
# st.write(df2[df2['DAERAH_SEMASA']=='Jasin'])

df2['UMUR_KSH']= df2['UMUR_KSH'].str.replace('?', '>')

# Select columns of interest into df3
df3 = df2[['UMUR_KSH', 'NEGERI_SEMASA', 'DAERAH_SEMASA', 'STRATA_SEMASA',
           'JANTINA', 'KSH_PAKAIAN', 'KSH_PERUMAHAN', 'KSH_BRG_THN_LAMA',
           'KSH_PENGANGKUTAN', 'KSH_LAIN_LAIN', 'KSH_MAKANAN_TOTAL']].copy()

# Calculate the sum value across multiple columns
df3['KSH_BMAKANAN_TOTAL'] = df3[['KSH_PAKAIAN', 'KSH_PERUMAHAN', 'KSH_BRG_THN_LAMA',
                           'KSH_PENGANGKUTAN', 'KSH_LAIN_LAIN']].sum(axis=1)

df3['KSH_INDIVIDU_TOTAL'] = df3[['KSH_BMAKANAN_TOTAL', 'KSH_MAKANAN_TOTAL']].sum(axis=1)

# Drop rows with more than 3 NaN values
df3 = df3.dropna(thresh=df3.shape[1] - 3)

# Display the resulting DataFrame
# st.write(df3.tail())

#========================================================================
# Read the tuned model
from pycaret.regression import load_model, predict_model

# Load the tuned model
tuned_gbm = pickle.load(open('pakw_v1/tune_PAKW.pkl', 'rb'))

#========================================================================

# Define dropdown widgets for fixed columns
negeri_dropdown = st.selectbox('Select NEGERI_SEMASA:', df3['NEGERI_SEMASA'].unique())
daerah_dropdown = st.selectbox('Select DAERAH_SEMASA:', df3['DAERAH_SEMASA'].unique())
strata_dropdown = st.selectbox('Select STRATA_SEMASA:', df3['STRATA_SEMASA'].unique())

# Define input for number of rows to generate
num_rows = st.number_input('Number of rows:', value=1, min_value=1)

# Generate input widgets for UMUR_KSH and JANTINA
umur_widgets = [st.selectbox(f'UMUR_KSH {i+1}:', df3['UMUR_KSH'].unique()) for i in range(num_rows)]
jantina_widgets = [st.selectbox(f'JANTINA {i+1}:', df3['JANTINA'].unique()) for i in range(num_rows)]

# Button to trigger data generation
generate_data_button = st.button("Generate Data")

# Function to generate data rows based on selected values
def generate_data_rows():
    data = [
        [umur_widgets[i], negeri_dropdown, daerah_dropdown, strata_dropdown, jantina_widgets[i]]
        for i in range(num_rows)
    ]
    return pd.DataFrame(data, columns=['UMUR_KSH', 'NEGERI_SEMASA', 'DAERAH_SEMASA', 'STRATA_SEMASA', 'JANTINA'])

# Function to display and save generated data rows
def on_generate_data_button_clicked():
    new_rows = generate_data_rows()
    st.write(new_rows)

# Display initial widgets
st.write(negeri_dropdown, daerah_dropdown, strata_dropdown, num_rows, generate_data_button)

# Check if the button is clicked
if generate_data_button:
    on_generate_data_button_clicked()

# Predict model on new_data
predictions = tuned_gbm.predict(df3)  # Use the model directly to make predictions
st.write(predictions)

# Calculate the sum of prediction labels
totalpakw = predictions.sum()
st.write("\nPAKW HH :", totalpakw)
