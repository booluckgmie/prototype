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

# Read the 'code_district.csv' file to get the mapping between district codes and district names
district_code = pd.read_csv('https://github.com/booluckgmie/sharecode/raw/master/data/code_district.csv')

# Create a dictionary from the DataFrame 'district_code' where district codes are keys and district names are values
district_mapping = dict(zip(district_code['code_district'], district_code['district']))

# Map the district codes to district names and populate the 'DAERAH_SEMASA' column in DataFrame 'df2'
df2['DAERAH_SEMASA'] = dfn['DAERAH_SEMASA'].map(district_mapping)

# Define the mapping dictionary for strata
strata_mapping = {
    1.0: 'BANDAR',
    2.0: 'LUAR BANDAR'
}

df2['STRATA_SEMASA'] = dfn['STRATA_SEMASA'].map(strata_mapping)

# Define the mapping dictionary for gender
gender_mapping = {
    1.0: 'LELAKI',
    2.0: 'PEREMPUAN'
}

df2['JANTINA'] = dfn['JANTINA'].map(gender_mapping)

# Filter the DataFrame for rows where 'DAERAH_SEMASA' contains slash or bracket
contains_slash_or_bracket = df2['DAERAH_SEMASA'].str.contains(r'[/()]', na=False)
df_filtered = df2[contains_slash_or_bracket]

# Replace specific district names
replace_dict = {
    'W.P. KUALA LUMPUR': 'W.P. Kuala Lumpur',
    'W.P. PUTRAJAYA': 'W.P. Putrajaya',
    'W.P. LABUAN': 'W.P. Labuan'
}

df2['DAERAH_SEMASA'] = df2['DAERAH_SEMASA'].replace(replace_dict)

# Split district names and retain the first part
df2['DAERAH_SEMASA'] = df2['DAERAH_SEMASA'].str.split(r'[/()]').str.get(0)

# Replace '?' with '>' in 'UMUR_KSH'
df2['UMUR_KSH'] = df2['UMUR_KSH'].str.replace('?', '>')

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

# Read the tuned model
from pycaret.regression import load_model, predict_model

# Load the tuned model
# tuned_gbm = pickle.load(open('pakw_v1/tune_PAKW.pkl', 'rb'))
from pycaret.regression import load_model, predict_model

tuned_gbm = load_model('pakw_v1/tune_PAKW')
print(tuned_gbm)

st.title('Pengiraan PAKW by HH : Beta 1.0')

# Define dropdown widgets for fixed columns
negeri_dropdown = st.selectbox('Pilih NEGERI:', df3['NEGERI_SEMASA'].unique())
daerah_placeholder = st.empty()

# Define function to update DAERAH_SEMASA dropdown options based on selected NEGERI_SEMASA
def update_daerah_options():
    selected_negeri = negeri_dropdown
    daerah_options = df3[df3['NEGERI_SEMASA'] == selected_negeri]['DAERAH_SEMASA'].unique()
    return daerah_options

# Initial update of DAERAH_SEMASA dropdown
daerah_dropdown_options = update_daerah_options()
daerah_dropdown = st.selectbox('Pilih DAERAH:', daerah_dropdown_options)
strata_dropdown = st.selectbox('Pilih STRATA:', df3['STRATA_SEMASA'].unique())

# Define input for number of rows to generate
num_rows = st.number_input('Bilangan Isi Rumah:', value=1, min_value=1)

# Generate input widgets for UMUR_KSH and JANTINA
col1, col2 = st.columns(2)  # Divide the layout into two columns

with col1:
    umur_widgets = [st.selectbox(f'UMUR_IR {i+1}:', df3['UMUR_KSH'].unique()) for i in range(num_rows)]

with col2:
    jantina_widgets = [st.selectbox(f'JANTINA_IR {i+1}:', df3['JANTINA'].unique()) for i in range(num_rows)]


# Button to trigger data generation
generate_data_button = st.button("Jana Data")

# Function to generate data rows based on selected values
def generate_data_rows():
    negeri_value = negeri_dropdown
    daerah_value = daerah_dropdown
    strata_value = strata_dropdown
    
    data = [
        [umur_widgets[i], negeri_value, daerah_value, strata_value, jantina_widgets[i]]
        for i in range(num_rows)
    ]
    return pd.DataFrame(data, columns=['UMUR_KSH', 'NEGERI_SEMASA', 'DAERAH_SEMASA', 'STRATA_SEMASA', 'JANTINA'])

# Display generated data if button is clicked
if generate_data_button:
    new_data = generate_data_rows()
    st.write("Generated Data:", new_data)


# Button to trigger prediction
predict_button = st.button("Predict Data")

# Function to predict generated data
def predict_generated_data():
    new_data = generate_data_rows()
    predictions = tuned_gbm.predict(new_data)
    total_pakw = predictions.sum()
    st.write("Predicted PAKW mengikut Individual:", predictions)
    st.write("Total PAKW:", total_pakw)


# Check if the predict button is clicked
if predict_button:
    predict_generated_data()

# Button to trigger reset
reset_button = st.button("Reset")

# Function to reset generated data and prediction results
def reset_data():
    st.write("Reset the INPUT")
    st.empty()  # Clear the output

# Check if the reset button is clicked
if reset_button:
    reset_data()




