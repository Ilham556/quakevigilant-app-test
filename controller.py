import streamlit as st
import hydralit_components as hc
from st_aggrid import AgGrid, GridOptionsBuilder, DataReturnMode, AgGridTheme
import pandas as pd
from pandas.api.types import is_bool_dtype, is_numeric_dtype
import mysql.connector
import datetime
from datetime import date, timedelta
import numpy as np
from streamlit_option_menu import option_menu
import altair as alt
import requests
import geopandas
from folium.plugins import MarkerCluster
from folium.plugins import HeatMap
from folium import plugins
import folium
from streamlit_folium import st_folium
from streamlit_folium import folium_static
from datetime import datetime as dt



# controller.py
from model import AppModel
from view import AppView


class AppController:
    def __init__(self, model, view):
        self.model = model
        self.view = view
        self.model.api_usgs()
        self.df = self.model.df_usgs()
        self.df_heatmap = self.model.processing_df_heatmap(self.model.df_heatmap)
        self.df_artikel = self.model.df_artikel
        self.df_user = self.model.df_user

    def filtered_map_usgs(self):
        self.df = self.view.homeviewfilter(self.df)
        return self.df

    def filtered_map_heatmap(self):
        self.df_heatmap = self.view.heatmapviewfilter(self.df_heatmap)
        return self.df_heatmap

    def filtered_graph(self):
        self.df_heatmap = self.view.graphviewfilter(self.df_heatmap)
        return self.df_heatmap
    
    def header_heatmap(self):
        max_year = self.df_heatmap['date'].dt.year.max()
        min_year = self.df_heatmap['date'].dt.year.min()
        return self.view.header(f'Summarize QuakeVigilant, {min_year}-{max_year}')
    
    def title_heatmap(self):
        max_year = self.df_heatmap['date'].dt.year.max()
        min_year = self.df_heatmap['date'].dt.year.min()
        return self.view.title(f'QuakeVigilant Heat Map, {min_year}-{max_year}')
    
    def title_graph(self):
        max_year = self.df_heatmap['date'].dt.year.max()
        min_year = self.df_heatmap['date'].dt.year.min()
        return self.view.title(f'QuakeVigilant Graph, {min_year}-{max_year}')
    
    def title_data(self):
        max_year = self.df_heatmap['date'].dt.year.max()
        min_year = self.df_heatmap['date'].dt.year.min()
        return self.view.title(f'Data QuakeVigilant, {min_year}-{max_year}')

    def table_usgs(self):
        col1,col2 = st.columns(2)
        with col2:
            grid = self.view.table(self.df)
        selected_rows = grid['selected_rows']
        if selected_rows:
            selected_indices = [i['_selectedRowNodeInfo']['nodeRowIndex'] for i in selected_rows]
            valid_indices = [idx for idx in selected_indices if idx < len(self.df)]
            self.df = self.df.iloc[valid_indices]
        with col1:
            self.map_usgs()
    
        
    def map_usgs(self):
        self.view.show_map(self.df)
    
    def table_heatmap(self):
        self.view.table(self.df_heatmap)
    
    def map_heatmap(self):
        self.view.show_heatmap(self.df_heatmap)
    
    def list_article(self):
        return self.model.show_artikel()
    
    def login_validation(self,login_email, login_password):
        return self.model.login(login_email, login_password)

    def update_myuser(self, name, email, password, alamat, updated_at, ids):
        if any(value == "" for value in (name, email, password, alamat, updated_at, ids)):
            st.warning('All fields must be filled')
        else:
            self.model.update_myuser(name, email, password, alamat, updated_at, ids)
            st.experimental_rerun()
    def register_myuser(self, name, email, password, alamat, created_at, updated_at, is_admin):
        if any(value == "" for value in (name, email, password, alamat, created_at, updated_at)):
            st.warning('All fields must be filled')
        else:
            return self.model.register_myuser(name, email, password, alamat, created_at, updated_at, is_admin)
    
    def Summarizeview_user(self):
        self.view.Summarizeview_user(self.df_user)
    
    def graphview_user(self):
        self.view.graphview_user(self.df_user)
    
    def createdata_heatmap(self, country, Reference_Point, state, status, tsunami, magnitudo, significance, data_type, longitude, latitude, depth, date):
        if any(value == "" for value in (country, Reference_Point, state, status, tsunami, magnitudo, significance, data_type, longitude, latitude, depth, date)):
            st.warning('All fields must be filled')
        else:
            self.model.createdata_heatmap(country, Reference_Point, state, status, tsunami, magnitudo, significance, data_type, longitude, latitude, depth, date)
            st.experimental_rerun()
    
    def deletedata_heatmap(self,ids):
        self.model.deletedata_heatmap(ids)
        st.experimental_rerun()
    
    def updatedata_heatmap(self, country, Reference_Point, state, status, tsunami, magnitudo, significance, data_type, longitude, latitude, depth, date, ids):
        if any(value == "" for value in (country, Reference_Point, state, status, tsunami, magnitudo, significance, data_type, longitude, latitude, depth, date, ids)):
            st.warning('All fields must be filled')
        else:
            self.model.updatedata_heatmap(country, Reference_Point, state, status, tsunami, magnitudo, significance, data_type, longitude, latitude, depth, date, ids)
            st.experimental_rerun()
    
    def createdata_article(self, link_g, judul, kontent, link_v, tanggal_p, penulis):
        if any(value == "" for value in (link_g, judul, kontent, link_v, tanggal_p, penulis)):
            st.warning('All fields must be filled')
        else:
            self.model.createdata_article(link_g, judul, kontent, link_v, tanggal_p, penulis)
            st.experimental_rerun()
    
    def updatedata_article(self, link_g, judul, konten, link_v, publikasi, ids):
        if any(value == "" for value in (link_g, judul, konten, link_v, publikasi, ids)):
            st.warning('All fields must be filled')
        else:
            self.model.updatedata_article(link_g, judul, konten, link_v, publikasi, ids)
            st.experimental_rerun()
    def deletedata_article(self,ids):
        self.model.deletedata_article(ids)
        st.experimental_rerun()
    
    def createdata_user(self, name, email, password, alamat, created_at, updated_at, is_admin):
        if any(value == "" for value in (name, email, password, alamat, created_at, updated_at, is_admin)):
            st.warning('All fields must be filled')
        else:
            self.model.createdata_user(name, email, password, alamat, created_at, updated_at, is_admin)
            st.experimental_rerun()
    
    def updatedata_user(self, name, email, password, alamat, updated_at, is_admin, ids):
        if any(value == "" for value in (name, email, password, alamat, updated_at, is_admin, ids)):
            st.warning('All fields must be filled')
        else:
            self.model.updatedata_user(name, email, password, alamat, updated_at, is_admin, ids)
            st.experimental_rerun()
    
    def deletedata_user(self,ids):
        self.model.deletedata_user(ids)
        st.experimental_rerun()
    
    def get_city(self):
        return self.model.get_city()
    
