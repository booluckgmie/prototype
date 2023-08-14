import pandas as pd
import streamlit as st
import re
import numpy as np

# df = pd.read_excel("PADU_PGK Makanan, Beta & Bukan Makanan 2022.xlsx", sheet_name='Data2019')
food_PLI = pd.read_excel("PADU_PGK Makanan, Beta & Bukan Makanan 2022.xlsx", sheet_name='Data PGK Makanan')
food_PLI.columns = ['Kumpulan Umur', 'Umur', 'Kalori', 'Negeri', 'Strata', 'totalFood_PLI']
# Assuming food_PLI is your DataFrame
def map_gender(row):
    if 'Lelaki' in row['Kumpulan Umur']:
        return 'Lelaki'
    elif 'Perempuan' in row['Kumpulan Umur']:
        return 'Perempuan'
    else:
        return None  # or any default value you prefer

food_PLI['Jantina'] = food_PLI.apply(map_gender, axis=1)
food_PLI['Kumpulan Umur'] = food_PLI['Kumpulan Umur'].apply(lambda x: re.sub(r'(Lelaki|Perempuan)', '', x, flags=re.IGNORECASE))
food_PLI['totalFood_PLI'] = pd.to_numeric(food_PLI['totalFood_PLI'], errors='coerce')
food_PLI['totalFood_PLI'] = food_PLI['totalFood_PLI'].replace([np.nan, np.inf, -np.inf], 0).astype(int)


# df = pd.read_excel("PADU_PGK Makanan, Beta & Bukan Makanan 2022.xlsx", sheet_name='Data2019')
nonfood_PLI = pd.read_excel("PADU_PGK Makanan, Beta & Bukan Makanan 2022.xlsx", sheet_name='Data PGK B.Makanan (p)')
nonfood_PLI = nonfood_PLI[['Negeri', 'Strata', 'p_cloth', 'p_rent', 'p_durable', 'p_transport', 'p_other', 'totalNP_PLI']]
nonfood_PLI['totalNP_PLI'] = nonfood_PLI['totalNP_PLI'].astype(int)
nonfood_PLI.columns = ['Negeri', 'Strata', 'p_cloth', 'p_rent', 'p_durable', 'p_transport', 'p_other', 'totalNFood_PLI']

# Run the Streamlit app
if __name__ == '__main__':
    st.title('PLI2022 Individual')
    st.write('Use the interactive widgets to calculate PLI values.')
    st.sidebar.title('PLI2022 Individual')
    st.sidebar.write('Kalkulator.')

    # ... Add more sidebar options if needed ...

    st.sidebar.markdown('---')
    st.sidebar.write('Created by Najmi Ariffin')

    # ... Add more attribution or information if needed ...

    st.sidebar.write('Powered by Streamlit')

# Create interactive widgets
state_dropdown = st.selectbox('State:', ['select', 'Johor', 'Kedah', 'Kelantan', 'Malaysia', 'Melaka', 'Negeri Sembilan', 'Pahang', 'Perak', 'Perlis', 'Pulau Pinang', 'Sabah', 'Sarawak', 'Selangor', 'Terengganu', 'W.P. Kuala Lumpur', 'W.P. Labuan', 'W.P. Putrajaya'])
strata_dropdown = st.selectbox('Strata:', ['select', 'Bandar', 'Luar Bandar'])
age_dropdown = st.selectbox('Age:', ['select', '1-3 tahun', '4-6 tahun', '6-8 bulan', '7-9 tahun', '9-11 bulan', '10-12 tahun', '13-15 tahun', '16-<18 tahun', '18-29 tahun', '30-59 tahun', '≥60 tahun'])
gender_dropdown = st.selectbox('Gender:', ['select', 'Lelaki', 'Perempuan'])
pendapatan_input = st.number_input('Pendapatan:')

# Calculate and display results
if st.button('Calculate'):
    if age_dropdown == 'select' or gender_dropdown == 'select' or strata_dropdown == 'select':
        st.warning("Please select Age, Gender, and Strata.")
    else:
        selected_age = age_dropdown
        selected_gender = gender_dropdown
        selected_state = state_dropdown
        selected_strata = strata_dropdown
        pendapatan = pendapatan_input

        # Given dataset kumpulan pendapatan
        kump_pdptn = [
                        (0, 2499, 'B1', 'B40'),
                        (2500, 3170, 'B2', 'B40'),
                        (3171, 3970, 'B3', 'B40'),
                        (3971, 4849, 'B4', 'B40'),
                        (4850, 5880, 'M1', 'M40'),
                        (5881, 7100, 'M2', 'M40'),
                        (7111, 8700, 'M3', 'M40'),
                        (8701, 10959, 'M4', 'M40'),
                        (10960, 15040, 'T1', 'T20'),
                        (15040, 1000000, 'T2', 'T20')
                    ]

        # Finding the corresponding values for kump_decile and kump_main
        kump_decile = None
        kump_main = None
        for row in kump_pdptn:
            min_val, max_val, kump_decile_val, kump_main_val = row
            if min_val <= pendapatan <= max_val:
                kump_decile = kump_decile_val
                kump_main = kump_main_val
                break

        if selected_age == 'select' or selected_gender == 'select' or selected_strata == 'select':
            st.error("Please select Age, Gender, and Strata.")
        else:
            calories = food_PLI[(food_PLI['Umur'] == selected_age) & (food_PLI['Jantina'] == selected_gender)]['Kalori'].values[0]
            totalFood_PLI = food_PLI[(food_PLI['Umur'] == selected_age) & (food_PLI['Jantina'] == selected_gender) & (food_PLI['Negeri'] == selected_state) & (food_PLI['Strata'] == selected_strata)]['totalFood_PLI'].values[0]
            totalNFood_PLI = nonfood_PLI[(nonfood_PLI['Negeri'] == selected_state) & (nonfood_PLI['Strata'] == selected_strata)]['totalNFood_PLI'].values[0]
            plivalue = totalFood_PLI + totalNFood_PLI

            st.markdown("### Results")
            st.write("Calories:", calories)
            st.write("Food PLI:", totalFood_PLI)
            st.write("Non-Food PLI:", totalNFood_PLI)
            st.write("PLI:", plivalue)
            st.write("Kumpulan Pendapatan:", kump_main)
            st.write("Decile:", kump_decile)

            if pendapatan <= totalFood_PLI:
                st.write("Status: Miskin Tegar")
            elif pendapatan < plivalue:
                st.write("Status: Miskin")
            else:
                st.write("Status: Tidak Miskin")
