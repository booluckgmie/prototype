import os
import pandas as pd
import numpy as np
from datetime import datetime
import streamlit as st
import base64

pd.set_option('display.float_format', '{:.2f}'.format)

# Sample data
table_data = [
    ["KIR", "###", "###", 1200],  
    ["IR2", "select", "select", False],
    ["IR3", "select", "select", False],
    ["IR4", "select", "select", False],
    ["IR5", "select", "select", False],
    ["IR6", "select", "select", False],
    ["IR7", "select", "select", False]
]

def reset_data():
    for i in range(len(table_data)):
        table_data[i][1] = "select"
        table_data[i][2] = "select"
        table_data[i][3] = False

def main():

    st.title('PLI2022 HH')
    st.write('Use the interactive widgets to calculate PLI values.')

    # Create interactive widgets
    default_state = 'Johor'
    default_strata = 'Luar Bandar'  

    # State dropdown with default value
    state_dropdown = st.selectbox('**State:**', ['select', 'Johor', 'Kedah', 'Kelantan', 'Melaka', 'Negeri Sembilan', 'Pahang', 'Perak', 'Perlis', 'Pulau Pinang', 
                                             'Sabah', 'Sarawak', 'Selangor', 'Terengganu', 'W.P. Kuala Lumpur', 'W.P. Labuan', 'W.P. Putrajaya'], index=1)  

    # Strata dropdown with default value
    strata_dropdown = st.selectbox('**Strata:**', ['select', 'Bandar', 'Luar Bandar'], index=2) 

    # Set default values based on selection
    state_dropdown = default_state if state_dropdown == 'select' else state_dropdown
    strata_dropdown = default_strata if strata_dropdown == 'select' else strata_dropdown

    
    # Add sidebar options
    st.sidebar.title('PLI2022 HH Kalkulator.')
    st.sidebar.write('v11.2023')
    st.sidebar.markdown('---')
    st.sidebar.write('Created by Najmi Ariffin')
    st.sidebar.write('Powered by Streamlit')
    
    # Reset button
    if st.button("Reset"):
        reset_data()
        
    # Display the table data input
    st.title("Perincian Isi Rumah")

    for i in range(len(table_data)):
        col1, col2, col3, col4, col5 = st.columns(5)

        with col1:
            st.write(f"**Ahli {i+1}:**", table_data[i][0])

        with col2:
            gender_index = 0 if table_data[i][1] == "select" else 1
            table_data[i][1] = st.selectbox(f"Gender {i+1}:", ["select", "Lelaki", "Perempuan"], index=gender_index)

        with col3:
            age_group_index = 0 if table_data[i][2] == "select" else 1
            table_data[i][2] = st.selectbox(f"Age Group {i+1}:", ['select',
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
                                                           '≥60 tahun'], index=age_group_index)

        with col4:
            table_data[i][3] = st.number_input(f"Income: {i+1}:", value=0)


    # Data processing and DataFrame creation
    filtered_data = [row for row in table_data if row[2] is not None and row[2] != 'select']
    header_names = ["Ahli", "JANTINA", "Umur", "INC_HH"]
    padu = pd.DataFrame(filtered_data, columns=header_names)

    # state
    padu["NEGERI_SEMASA"] = state_dropdown
    padu["STRATA_SEMASA"] = strata_dropdown

    # Create a dictionary to map state or region names to their identifiers
    state_mapping = {
        'Johor': 1,
        'Kedah': 2,
        'Kelantan': 3,
        'Melaka': 4,
        'Negeri Sembilan': 5,
        'Pahang': 6,
        'Pulau Pinang': 7,
        'Perak': 8,
        'Perlis': 9,
        'Selangor': 10,
        'Terengganu': 11,
        'Sabah': 12,
        'Sarawak': 13,
        'W.P. Kuala Lumpur': 14,
        'W.P. Labuan': 15,
        'W.P. Putrajaya': 16
    }

    # Create a new column 'NEGERI_CODE' by mapping 'NEGERI_SEMASA' to its corresponding identifier
    padu['NEGERI_CODE'] = padu['NEGERI_SEMASA'].map(state_mapping)

    # Sum the "Income" column
    total_income = padu["INC_HH"].sum()

    # Count hhsize
    hhsize = padu['Ahli'].shape[0]

    # Recode data for calculation
    padu['JANTINA_CODE'] = padu['JANTINA'].apply(lambda x: 1 if x == 'Lelaki' else 2)
    padu['STRATA_CODE'] = padu['STRATA_SEMASA'].apply(lambda x: 1 if x == 'Bandar' else 2)

    padu[['JANTINA_CODE', 'NEGERI_CODE', 'STRATA_CODE']] = padu[['JANTINA_CODE', 'NEGERI_CODE', 'STRATA_CODE']].apply(lambda x: x.astype(str))
    
    # padu['TARIKH_LAHIR'] = pd.to_datetime(padu['TARIKH_LAHIR']).dt.strftime('%d/%m/%Y')
    # padu[['NEGERI_SEMASA', 'STRATA_SEMASA']] = padu[['NEGERI_SEMASA', 'STRATA_SEMASA']].apply(lambda x: x.astype(str).str.zfill(2))

    # # Filtering
    # mask = (
    #     padu['JANTINA'].notna() &
    #     padu['UMUR'].notna() &
    #     padu['STRATA_SEMASA'].notna() &
    #     padu['JUMLAH_PENDAPATAN_BULANAN'].notna() &
    #     padu['NEGERI_SEMASA'].notna()
    # )

    # Derive Variables
    # def calculate_umurSEMASA(df):
    #     df['TARIKH_LAHIR'] = pd.to_datetime(df['TARIKH_LAHIR'], format='%d/%m/%Y')
    #     df['UMUR_SEMASA'] = (datetime.now() - df['TARIKH_LAHIR']).astype('<m8[Y]').astype(int)
    #     return df

    # padu = calculate_umurSEMASA(padu)

    # Special Need
    # hhsize = padu.groupby('NO_IR')['NO_IR'].transform('count')
    # padu['INC_HH'] = padu.groupby('NO_IR')['JUMLAH_PENDAPATAN_BULANAN'].transform('sum').apply(pd.to_numeric, errors='coerce').fillna(0)
    # padu['BABY'] = (padu['UMUR_SEMASA'] <= 2).astype(int)
    # padu['OLD_CIT'] = (padu['UMUR_SEMASA'] >= 60).astype(int)

    # Grouping Umur
    # age_bins = [-1, 3, 6, 9, 12, 15, 18, 29, 59, float('inf')]
    # age_labels = ['1-3 tahun', '4-6 tahun', '7-9 tahun', '10-12 tahun', '13-15 tahun', '16-18 tahun', '18-29 tahun', '30-59 tahun', '≥60 tahun']
    # padu['UMUR_PGK'] = pd.cut(padu['UMUR_SEMASA'], bins=age_bins, labels=age_labels, right=False)

    # Calculate Food PLI
    def get_totalFood_PLI(row):
        key = (row['JANTINA_CODE'], row['Umur'], row['NEGERI_CODE'], row['STRATA_CODE'])
        value = mapping_dict.get(key)
        return value

    # Calculate Food PLI
    food_PLI = pd.read_csv('./foodpli_cal_v2.csv', usecols=['JANTINA_CODE', 'Umur', 'NEGERI_CODE', 'STRATA_CODE', 'totalFood_PLI'],
                           dtype={"NEGERI_CODE": str, "STRATA_CODE": str, "JANTINA_CODE": str})
    mapping_dict = food_PLI.set_index(['JANTINA_CODE', 'Umur', 'NEGERI_CODE', 'STRATA_CODE']).to_dict()['totalFood_PLI']

    # Apply the function to calculate 'totalFood_PLI' for the single row
    padu['totalFood_PLI'] = padu.apply(get_totalFood_PLI, axis=1)

    # Sum the 'totalFood_PLI' column
    sum_fpli = padu['totalFood_PLI'].sum()
    padu['SUM_FPLI'] = sum_fpli

    # Calculate NFPLI
    nonfood_PLI = pd.read_excel("nfoodpli_cal_v2.xlsx", sheet_name='Data PGK B.Makanan (p)',
                                dtype={"NEGERI_CODE": str, "STRATA_CODE": str})  


    condition = (nonfood_PLI['NEGERI_CODE'].isin(padu['NEGERI_CODE'])) & (
            nonfood_PLI['STRATA_CODE'].isin(padu['STRATA_CODE']))

    # Extract 'Pakaian' value
    p_cloth = nonfood_PLI.loc[condition, 'Pakaian'].values[0] if not condition.empty and condition.any() else 0
    p_cloth = p_cloth * 27.737395 * hhsize
    p_rent = nonfood_PLI.loc[condition, 'Perumahan'].values[0] if not condition.empty and condition.any() else 0
    p_rent = p_rent * 458.49397 * (hhsize ** 0.474518)
    p_durable = nonfood_PLI.loc[condition, 'Barang Tahan Lama'].values[0] if not condition.empty and condition.any() else 0
    p_durable = p_durable * 7.5236389 * hhsize
    p_transport = nonfood_PLI.loc[condition, 'Pengangkutan'].values[0] if not condition.empty and condition.any() else 0
    p_transport = p_transport * 73.48135 * hhsize
    p_other = nonfood_PLI.loc[condition, 'Barang Bukan Makanan Lain'].values[0] if not condition.empty and condition.any() else 0
    p_other = p_other * 175.84981 * hhsize

    sum_nfpli = p_cloth + p_rent + p_durable + p_transport + p_other
        
    padu['SUM_NFPLI'] = sum_nfpli

    # try:
    #     # Check if the DataFrame is not empty
    #     if not padu.empty:
    #         # Access the first element of the 'PGK' column
    #         pgk = padu['PGK'][0]

    #         # Your Streamlit code here, using the 'pgk' variable
    #         # ...
    #     else:
    #         st.warning("The DataFrame is empty. Please provide valid data.")

    # except IndexError:
    #     # Suppress the IndexError warning
    #     pass
    # except Exception as e:
    #     st.error(f"An error occurred: {e}. Kindly check your data.")

    # Total PLI @ PGK
    padu['PGK'] = padu['SUM_FPLI'] + sum_nfpli
    pgk = padu['PGK'][0]


    # Classification
    def calculate_status(row):
        conditions = [
            total_income < row['totalFood_PLI'],
            total_income < row['PGK']
        ]
        choices = ['Miskin Tegar', 'Miskin']
        return np.select(conditions, choices, default='Tidak Miskin')

    # padu['STATUS'] = padu.apply(calculate_status, axis=1)
    # statusk = padu['STATUS'][0]

    statusk = padu.apply(calculate_status, axis=1)[0]

    # kumpulan pendapatan 2022
    kump_pdptn = pd.read_csv("./kump_pdptn2022_v2.csv",
                            usecols=['decile_min', 'decile_max', 'income_min', 'income_max', 'State', 'NEGERI_CODE', 'kump_main', 'kump_decile', 'KUMP_B60'],
                            dtype={"NEGERI_CODE": str})

    kump_decile = None
    kump_main = None
    KUMP_B60 = None

    for index, row in kump_pdptn.iterrows():
        min_val = row['income_min']
        max_val = row['income_max']

        if min_val <= total_income <= max_val and row['NEGERI_CODE'] == padu['NEGERI_CODE'][0]:
            kump_decile = row['kump_decile']
            kump_main = row['kump_main']

            if kump_pdptn.loc[index, 'kump_decile'] == kump_decile:
                KUMP_B60 = row['KUMP_B60']
                break

            
    padu = padu[['Ahli','JANTINA','Umur','INC_HH','NEGERI_SEMASA','STRATA_SEMASA']]
    # Display the DataFrame and total income
    
    st.title('#########')
    st.write("### INPUT")
    st.write(padu)
    
    st.write("### OUTPUT")
    # Display in two columns
    col1, col2 = st.columns(2)

    with col1:
        st.write(f"**Total HH Income:** {total_income}")
        st.write(f"**HH Size:** {hhsize}")
        st.write(f"**SUM_FPLI:** {sum_fpli:.2f}")
        st.write(f"**SUM_NFPLI:** {sum_nfpli:.2f}")   
        st.write(f"**PGK:** {pgk:.2f}")


    with col2:
        st.write(f"**STATUS:** {statusk}")
        st.write(f"**KUMP. PENDAPATAN:** {kump_main}")
        st.write(f"**KUMP. DECILE:** {kump_decile}")
        st.write(f"**KUMP. B60:** {KUMP_B60}")      
        
if __name__ == "__main__":
    main()
