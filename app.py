import streamlit as st
from os import error
import pandas as pd
import base64
import matplotlib.pyplot as plt
import seaborn as sns
import numpy as np
import os
import glob
from shutil import copy2, rmtree
import time
import altair as alt

st.set_option('deprecation.showPyplotGlobalUse', False) # remove warning of pyplot

def _configure_layout():
    html = '''
    <style>
        body { 
            margin: 0;
            font-family: Arial, Helvetica, sans-serif;
            color: #111; 
            # background-color: #F79C60; 
            }
        .header {
            padding: 10px 16px;
            background: #FF7100;
            color: #f1f1f1;
            position: fixed;
            top: 0;
            }
        .sticky .sidebar { 
            position: fixed;
            top: 0;
            width: 100%;
            }
        .reportview-container .main .block-container{
            max-width: 1150px;
            }
        # .st-by {
            # color: #111; 
            # background-color: #F79C60; 
            # background: linear-gradient(to right, rgb(246, 51, 102) 0%, rgb(246, 51, 102) 75%, rgb(213, 218, 229) 75%, rgb(213, 218, 229) 100%);
            }
    </style>
    '''
    st.markdown(html, unsafe_allow_html=True)
_configure_layout()

abas = ['Energia Armazenada Inicial', 'Previsão de Vazões', 'Previsão Pluviométricas', 'Atualização PMO/PMR']
run_app = st.sidebar.selectbox('Run app', abas)
# run_app = st.sidebar.radio('Run app', abas)

if run_app == 'Energia Armazenada Inicial':
    st.title('Energia Armazenada Inicial')

    input_path = st.sidebar.text_input("input path", 'input', key='1')
    output_path = st.sidebar.text_input("output path", 'output', key='2')
    case_name = st.sidebar.text_input("case name", 'example', key='3')

    seek_goal_sudeste = st.sidebar.slider('Sudeste', 0.0,100.0,50.0)
    seek_goal_sul = st.sidebar.slider('Sul', 0.0,100.0,50.0)
    seek_goal_nordeste = st.sidebar.slider('Nordeste', 0.0,100.0,50.0)
    seek_goal_norte = st.sidebar.slider('Norte', 0.0,100.0,50.0)

    if input_path is not None:
        filepath = './'+input_path

        st.write('\n')

        space1, left_column, space2, right_column, space3 = st.beta_columns([0.1,1,0.1,1,0.1])

        hidr_csv_filepath = filepath+'/hidr.csv'
        try:
            hidr = pd.read_csv(hidr_csv_filepath)
            if left_column.checkbox("Show hidr"):
                st.dataframe(hidr)

        except:
            st.warning('hidr.csv not found!!! Check input path!!!')
        
        # dadger_filepath = ''.join(glob.glob(filepath+'DADGER.RV*'))
        dadger_filepath = filepath+'/DADGER.RV0'
        try:
            with open(dadger_filepath, 'r', encoding="latin1") as dadger:
                dadger_content = dadger.read()
                dadger_content_split = dadger_content.split('\n')
                if right_column.checkbox("Show DADGER"):
                    st.write(dadger_content_split)
        except:
            st.warning('DADGER not found!!! Check input path!!!')

    st.subheader('Before seek goal')
    st.write('\n')

    space1, left_column, space2, right_column, space3 = st.beta_columns([0.5,4,0.5,4,0.5])
    hidr_subsistema = pd.merge(hidr.groupby('subsistema')['earmmax'].sum().reset_index(), hidr.groupby('subsistema')['earmmax'].mean().reset_index(name='%'), on='subsistema', how='left')
    hidr_reeid = pd.merge(hidr.groupby('REE_id')['earmmax'].sum().reset_index(), hidr.groupby('REE_id')['earmmax'].mean().reset_index(name='%'), on='REE_id', how='left')
    left_column.dataframe(hidr_subsistema)
    right_column.dataframe(hidr_reeid)

    if st.button('Seek goal', key='button_seek_goal'):
        st.button("Re-run")
    
    st.subheader("Powerplant")
    powerplant = st.multiselect(
        'Choose:', list(hidr.set_index('UH_nome').index),
    )

    data = hidr.set_index('UH_nome').loc[powerplant]

    left_column, right_column = st.beta_columns([1,3])

    table_vis = data.filter(like='vol/volutilmax_itr', axis=1).T.reset_index(drop=True).reset_index().set_index('index')

    left_column.write(table_vis)

    data = data.filter(like='vol/volutilmax_itr', axis=1).T.reset_index(drop=True).reset_index()
    data = pd.melt(data, id_vars=["index"])
    data.columns = ['iteration', 'UH_nome', 'vol/volutilmax']
    st.write('')

    chart = (
        alt.Chart(data)
        .mark_area(opacity=0.2)
        # .mark_line()
        .encode(
            x="iteration:N",
            y=alt.Y("vol/volutilmax:Q", stack=None),
            color="UH_nome:N",
        )
    )
    right_column.altair_chart(chart, use_container_width=True)

    st.subheader('After seek goal')
    st.write('\n')
    
    space1, left_column, space2, right_column, space3 = st.beta_columns([0.5,4,0.5,4,0.5])
    hidr_subsistema = pd.merge(hidr.groupby('subsistema')['earmmax'].sum().reset_index(), hidr.groupby('subsistema')['earmmax'].mean().reset_index(name='%'), on='subsistema', how='left')
    hidr_reeid = pd.merge(hidr.groupby('REE_id')['earmmax'].sum().reset_index(), hidr.groupby('REE_id')['earmmax'].mean().reset_index(name='%'), on='REE_id', how='left')
    left_column.dataframe(hidr_subsistema)
    right_column.dataframe(hidr_reeid)

    # def filedownload():
    #     csv = hidr.to_csv(index=False)
    #     b64 = base64.b64encode(csv.encode()).decode()  # strings <-> bytes conversions
    #     href = f'<a href="data:file/csv;base64,{b64}" download="playerstats.csv">Download CSV File</a>'
    #     return href
    # st.markdown(filedownload(), unsafe_allow_html=True)

    if st.button('Save study', key='button_save_study'):
        st.balloons()
        if os.path.exists(output_path):
            pass
        else:
            os.makedirs(output_path)

        test_path = output_path + '/' + case_name + '_SE_' + str(int(seek_goal_sudeste)) + \
                                                    '_S_' + str(int(seek_goal_sul)) + \
                                                    '_NE_' + str(int(seek_goal_nordeste)) + \
                                                    '_N_' + str(int(seek_goal_norte))
        if os.path.exists(test_path):
            rmtree(test_path)
        os.makedirs(test_path)

        with open(test_path + '/' + dadger_filepath.split('/')[-1], 'w', encoding="latin1") as new_dadger:
            new_dadger.write('\n'.join(dadger_content_split))

        st.write('Created case study in \"{}\"'.format(test_path))

if run_app == 'Previsão de Vazões':
    st.title('Previsão de Vazões')

if run_app == 'Previsão Pluviométricas':
    st.title('Previsão Pluviométricas')

if run_app == 'Atualização PMO/PMR':
    st.title('Atualização PMO/PMR')

    st.write('\n')

    atualiza_pmo = st.file_uploader("Upload your input file", type=['csv','txt'])
    if atualiza_pmo is not None:
        pmo = pd.read_csv(atualiza_pmo)