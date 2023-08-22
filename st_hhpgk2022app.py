import pandas as pd
import streamlit as st
import re
import numpy as np

# Inject Google Analytics tracking code

# Run the Streamlit app
if __name__ == '__main__':
    st.title('PLI2022 HH')
    st.write('Use the interactive widgets to calculate PLI values.')
    
    # Inject Google Analytics code
    # st.markdown(google_analytics_code, unsafe_allow_html=True)
    
    st.sidebar.title('PLI2022 HH')
    st.sidebar.write('Kalkulator.')

    # ... Add more sidebar options if needed ...

    st.sidebar.markdown('---')
    st.sidebar.write('Created by Najmi Ariffin')

    # ... Add more attribution or information if needed ...

    st.sidebar.write('Powered by Streamlit')

# Create interactive widgets
state_dropdown = st.selectbox('State:', ['select', 'Johor', 'Kedah', 'Kelantan', 'Melaka', 'Negeri Sembilan', 'Pahang', 'Perak', 'Perlis', 'Pulau Pinang', 'Sabah', 'Sarawak', 'Selangor', 'Terengganu', 'W.P. Kuala Lumpur', 'W.P. Labuan', 'W.P. Putrajaya'])
strata_dropdown = st.selectbox('Strata:', ['select', 'Bandar', 'Luar Bandar'])

# Sample data
table_data = [
    ["KIR", "select", "select", False],  # Added the "False" flag for no income by default
    ["IR2", "select", "select", False],
    ["IR3", "select", "select", False],
    ["IR4", "select", "select", False],
    ["IR5", "select", "select", False],
    ["IR6", "select", "select", False]
]

st.title("Perincian Isi Rumah")

for i in range(len(table_data)):
    col1, col2, col3, col4, col5 = st.columns(5)
    
    with col1:
        ahli = st.write(f"**Ahli {i+1}:**", table_data[i][0])
        
    with col2:
        gender = st.selectbox(f"Gender {i+1}:", ["select", "Lelaki", "Perempuan"], index=0 if table_data[i][1] == "select" else 1)
    
    with col3:
        age_group = st.selectbox(f"Age Group {i+1}:", ['select', 
                    '6-8 bulan',
                    '9-11 bulan',
                    '1-3 tahun',
                    '4-6 tahun',                    
                    '7-9 tahun',
                    '10-12 tahun',
                    '13-15 tahun',
                    '16-<18 tahun',
                    '18-29 tahun',
                    '30-59 tahun',
                    '≥60 tahun'], index=0 if table_data[i][2] == "select" else 1)
    
    with col4:
        has_income = st.checkbox(f"D {i+1}:", value=False)
    
    if has_income:
        with col5:
            income = st.number_input(f"Income: {i+1}:", value=0)
    else:
        table_data[i][3] = False  # Reset the income flag to False if no income is selected
    
    table_data[i][3] = has_income

header_names = ["Ahli", "Gender", "Age Group", "Has Income", "Income"]  # Add header names to the data

# st.write("Updated Table:")
# st.table([header_names] + table_data)
