# model.py
import requests
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
import pathlib



class AppModel:
    def __init__(self):
        def get_ssl_cert():
            current_path = pathlib.Path(__file__).parent.parent
            return str(current_path/"DigiCertGlobalRootG2.crt.pem")
        db_secrets = st.secrets["mysql"]

        self.earthquake_data = None
        self.mydb = mysql.connector.connect(
                user=db_secrets["user"],
                password=db_secrets["password"],
                host=db_secrets["host"],
                port=3306,
                database='test',
                client_flags = [mysql.connector.ClientFlag.SSL],
                ssl_ca = get_ssl_cert(),
                ssl_disabled=False                
            )
        self.query = "SELECT * FROM earthquakedata"
        self.df_heatmap = pd.read_sql(self.query, self.mydb)

        self.query_user = "SELECT * FROM users"
        self.df_user = pd.read_sql(self.query_user, self.mydb)

        self.query_artikel = """SELECT artikel.id, artikel.link_gambar, artikel.judul, artikel.konten, artikel.link_vidio, artikel.tanggal_publikasi, users.name AS penulis
FROM artikel 
JOIN users ON artikel.penulis = users.id;"""
        self.df_artikel = pd.read_sql(self.query_artikel, self.mydb)
    
    


    def api_usgs(self):
        url = "https://earthquake.usgs.gov/fdsnws/event/1/query"
        today = date.today()
        start_of_week = today - datetime.timedelta(days=7)
        end_of_week = today + datetime.timedelta(days=7)
        # Parameter untuk permintaan API
        params = {
            "format": "geojson",
            "starttime":start_of_week.isoformat(),
            "endtime":end_of_week.isoformat(),
            "minmagnitude": 2.5
        }

        # Melakukan permintaan GET ke API
        response = requests.get(url, params=params)

        # Mengecek status permintaan
        if response.status_code == 200:
            # Mengubah data yang diterima menjadi JSON
            self.earthquake_data = response.json()
            return self.earthquake_data
        

        else:
            print(f"Request failed with status code {response.status_code}")
    
    def df_usgs(self):
        df_properties = pd.DataFrame([feature['properties'] for feature in self.earthquake_data['features']])
        df_geometry = pd.DataFrame([feature['geometry']['coordinates'] for feature in self.earthquake_data['features']], columns=['longitude', 'latitude', 'depth'])
        #country, Reference_Point, state, status, tsunami,magnitudo, significance, data_type, longitude, latitude, depth, date
        # Concatenate the DataFrames along columns
        df = pd.concat([df_properties, df_geometry], axis=1)
        df['reference_point'] = df['place'].apply(lambda a: a.split(',')[0].split(' of ')[-1] if (a and "of" in a) else (a.split(',')[0] if a else ""))
        df['state'] = df['place'].apply(lambda x: x.split(',')[1] if (x and len(x.split(',')) > 1) else x)
        df = df[['place', 'reference_point', 'state', 'status', 'tsunami', 'mag', 'sig', 'type', 'longitude', 'latitude', 'depth', 'time']]
        
        df['time'] = pd.to_datetime(df['time'], unit='ms')
        df['time_date'] = df['time'].dt.date
        df = df[df['state'].str.strip().isin(['Indonesia'])]
        return df

    def processing_df_heatmap(self,df):
        df['date'] = pd.to_datetime(df['date'])
        df['times'] = df['date'].dt.time
        bantu = pd.to_datetime(df['times'], format='%H:%M:%S')
        df['month'] = df['date'].dt.month
        df['year'] = df['date'].dt.year
        df['quarter'] = df['month'].apply(lambda x:1 if x < 4 else 2 if x < 7
                                 else 3 if x < 10 else 4)
        listBantu = []
        for i in bantu.dt.hour:
            varBantu = ''
            if (i<3):
                varBantu = 'Early Morning'
            elif(i<6):
                varBantu = 'Dawn'
            elif(i<12):
                varBantu = 'Morning'
            elif(i<18):
                varBantu = 'Afternoon'
            else:
                varBantu = 'Night'
            listBantu.append(varBantu)
        df['dayperiod'] = listBantu

        df['categorical earthquake'] = df['magnitudo'].apply(lambda x: 'micro' if x < 3 else 'minor' if x < 4 else 'light' if x < 5
                                                    else 'moderate' if x < 6 else 'strong' if x < 7 else 'major' if x < 8 
                                                     else 'very strong')
        
        df['season'] = df['month'].apply(lambda x:'dry season' if (x>3)&(x<11) else 'rainy season')
        df['depth category'] = df['depth'].apply(lambda x:'shallow' if x < 60 else 'intermediate' if x < 300 else 'deep')

        return df
    
    def show_artikel(self):
        try:
            cursor = self.mydb.cursor()
            query = """SELECT artikel.id, artikel.link_gambar, artikel.judul, artikel.konten, artikel.link_vidio, artikel.tanggal_publikasi, users.name AS penulis
FROM artikel 
JOIN users ON artikel.penulis = users.id"""
            cursor.execute(query)
            results = cursor.fetchall()

            articles = []

            for result in results:
                article = {
                    'id': result[0],
                    'element': {
                        'link_gambar': result[1],
                        'judul': result[2],
                        'konten': result[3],
                        'link_vidio': result[4],
                        'tanggal_publikasi': result[5],
                        'penulis':  result[6]
                    }
                    # Add more fields as needed
                }

                articles.append(article)

            return articles

        except Exception as e:
            st.error(f'Error: {e}')
    
    def login(self, email, password):
        try:
            cursor = self.mydb.cursor(buffered=True)
            query = "SELECT * FROM users WHERE email = %s AND password = %s"
            cursor.execute(query, (email, password))
            self.mydb.commit()
            result = cursor.fetchone()
            

            if result:
                
                # If login is successful, return the user information
                user_info = {
                    'id': result[0],
                    'name': result[1],
                    'email': result[2],
                    'password': result[3],
                    'alamat': result[4],
                    'is_admin': result[7],
                    # Add more fields as needed
                }
                return 'berhasil', user_info
            else:

                return "gagal", {}
        except Exception as e:
            st.error(f'Error: {e}')
    
    def update_myuser(self, name, email, password, alamat, updated_at, id):
        try:
            cursor = self.mydb.cursor()
            query = "UPDATE users SET name = %s, email = %s, password = %s, alamat = %s, updated_at = %s WHERE id = %s"
            cursor.execute(query, (name, email, password, alamat, updated_at, id))
            self.mydb.commit()
            self.query = "SELECT * FROM users"
            self.df_user = pd.read_sql(self.query, self.mydb)
            st.info('Data Successfully Update.') 
            
        except Exception as e:
            st.error(f'Error: {e}')
        return self.df_user

    def register_myuser(self, name, email, password, alamat, created_at, updated_at, is_admin):
        try:
            # Tambahkan data baru ke database
            cursor = self.mydb.cursor()
            query = "INSERT INTO users (name, email, password, alamat, created_at, updated_at, is_admin) VALUES (%s, %s, %s, %s, %s, %s, %s)"
            cursor.execute(query, (name, email, password,alamat, created_at, updated_at, is_admin))
            self.mydb.commit()
            self.query = "SELECT * FROM users"
            st.info('Data Successfully Added')
        except Exception as e:
            st.error(f'Error: {e}')
    
    def createdata_heatmap(self, country, Reference_Point, state, status, tsunami, magnitudo, significance, data_type, longitude, latitude, depth, date):
        try:
            # Tambahkan data baru ke database
            cursor = self.mydb.cursor()
            query = "INSERT INTO earthquakedata (country, Reference_Point, state, status, tsunami, magnitudo, significance, data_type, longitude, latitude, depth, date) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)"
            cursor.execute(query, (country, Reference_Point, state, status, tsunami, magnitudo, significance, data_type, longitude, latitude, depth, date))
            self.mydb.commit()
            self.query = "SELECT * FROM earthquakedata"
            self.df_heatmap = pd.read_sql(self.query, self.mydb)
            st.info('Data Successfully Added') 
        except Exception as e:
            st.error(f'Error: {e}')

        return self.df_heatmap
    
    def updatedata_heatmap(self, country, Reference_Point, state, status, tsunami, magnitudo, significance, data_type, longitude, latitude, depth, date, ids):
        try:
            cursor = self.mydb.cursor()
            query = "UPDATE earthquakedata SET country = %s, reference_point = %s, state = %s, status = %s, tsunami = %s, magnitudo = %s, significance = %s, data_type = %s, longitude = %s, latitude = %s, depth = %s, date = %s WHERE id = %s;"
            cursor.execute(query,(country, Reference_Point, state, status, tsunami, magnitudo, significance, data_type, longitude, latitude, depth, date, ids))
            self.mydb.commit()
            self.query = "SELECT * FROM earthquakedata"
            self.df_heatmap = pd.read_sql(self.query, self.mydb)
            st.info('Data Successfully Update') 
        except Exception as e:
            st.error(f'Error: {e}')
        return self.df_heatmap
    
    
    def deletedata_heatmap(self, ids):
        if len(ids) == 1:
            try:
                cursor = self.mydb.cursor()
                query = "DELETE FROM earthquakedata WHERE id = %s"
                cursor.execute(query, ids)
                self.mydb.commit()
                self.query = "SELECT * FROM earthquakedata"
                self.df_heatmap = pd.read_sql(self.query, self.mydb)
            except Exception as e:
                st.error(f'Error: {e}')
            return self.df_heatmap
        else:
            try:
                cursor = self.mydb.cursor()
                placeholders = ','.join(['%s'] * len(ids))
                query = f"DELETE FROM earthquakedata WHERE id IN ({placeholders})"
                cursor.execute(query, tuple(ids))
                self.mydb.commit()
                self.query = "SELECT * FROM earthquakedata"
                self.df_heatmap = pd.read_sql(self.query, self.mydb)
                st.info('Data Successfully Deleted') 
            except Exception as e:
                st.error(f'Error: {e}')
            return self.df_heatmap
    
    def createdata_article(self, link_g, judul, kontent, link_v, tanggal_p, penulis):
        try:
            # Tambahkan data baru ke database
            cursor = self.mydb.cursor()
            query = "INSERT INTO artikel (link_gambar, judul, konten, link_vidio, tanggal_publikasi, penulis) VALUES (%s, %s, %s, %s, %s, %s)"
            cursor.execute(query, (link_g, judul, kontent, link_v, tanggal_p, penulis))
            self.mydb.commit()
            st.info('Data Successfully Added') 
        except Exception as e:
            st.error(f'Error: {e}')
    
    def updatedata_article(self, link_g, judul, konten, link_v, publikasi, ids):
        try:
            cursor = self.mydb.cursor()
            query = "UPDATE artikel SET link_gambar = %s, judul = %s, konten = %s, link_vidio = %s, tanggal_publikasi = %s WHERE id = %s"
            cursor.execute(query, (link_g, judul, konten, link_v, publikasi, ids))
            self.mydb.commit()
            st.info('Data Successfully Updated.') 
        except Exception as e:
            st.error(f'Error: {e}')
    
    def deletedata_article(self, ids):
        if len(ids) == 1:
            try:
                cursor = self.mydb.cursor()
                query = "DELETE FROM artikel WHERE id = %s"
                cursor.execute(query, ids)
                self.mydb.commit()
                st.info('Data Successfully Deleted') 
            except Exception as e:
                st.error(f'Error: {e}')
        else:
            try:
                cursor = self.mydb.cursor()
                placeholders = ','.join(['%s'] * len(ids))
                query = f"DELETE FROM artikel WHERE id IN ({placeholders})"
                cursor.execute(query, tuple(ids))
                self.mydb.commit()
                st.info('Data Successfully Deleted') 
            except Exception as e:
                st.error(f'Error: {e}')
    
    def createdata_user(self, name, email, password, alamat, created_at, updated_at, is_admin):
        try:
            # Tambahkan data baru ke database
            cursor = self.mydb.cursor()
            query = "INSERT INTO users (name, email, password, alamat, created_at, updated_at, is_admin) VALUES (%s, %s, %s, %s, %s, %s, %s)"
            cursor.execute(query, (name, email, password,alamat, created_at, updated_at, is_admin))
            self.mydb.commit()
            st.info('Data Successfully Added') 
        except Exception as e:
            st.error(f'Error: {e}')
    
    def updatedata_user(self, name, email, password, alamat, updated_at, is_admin, ids):
        try:
            cursor = self.mydb.cursor()
            query = "UPDATE users SET name = %s, email = %s, password = %s, alamat = %s, updated_at = %s, is_admin = %s WHERE id = %s"
            cursor.execute(query, (name, email, password, alamat, updated_at, is_admin, ids))
            self.mydb.commit()
            st.info('Data Successfully Updated.') 
        except Exception as e:
            st.error(f'Error: {e}')
    
    def deletedata_user(self,ids):
        if len(ids) == 1:
            try:
                cursor = self.mydb.cursor()
                query = "DELETE FROM users WHERE id = %s"
                cursor.execute(query, ids)
                self.mydb.commit()
                st.info('Data Successfully Deleted') 
            except Exception as e:
                st.error(f'Error: {e}')
        else:
            try:
                cursor = self.mydb.cursor()
                placeholders = ','.join(['%s'] * len(ids))
                query = f"DELETE FROM users WHERE id IN ({placeholders})"
                cursor.execute(query, ids)
                self.mydb.commit()
                st.info('Data Successfully Deleted') 
            except Exception as e:
                st.error(f'Error: {e}')
    
    



