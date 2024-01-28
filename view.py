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






class AppView:
    def __init__(self):

        self.menu_id=""
        st.set_page_config(page_title="QuakeVigilant",layout='wide', initial_sidebar_state='collapsed',)
        #auth
        self.controller = None
        self.login_email = None
        self.login_password= None
        self.user_info = None
        
        #userdata
        self.name_user= None
        self.email_user = None
        self.password_user = None
        self.address_user = None
        self.update_at_input_user = None

        self.name_user_register = None
        self.email_user_register = None
        self.password_user_register = None
        self.address_user_register = None
        self.is_admin_user_register= None
        self.created_at_user_register = None
        self.update_at_user_register = None

        #heatmapdata
        self.country_heatmap_create = None
        self.Reference_Point_heatmap_create = None
        self.state_heatmap_create = None
        self.status_heatmap_create = None
        self.tsunami_heatmap_create = None
        self.magnitudo_heatmap_create = None
        self.significance_heatmap_create = None
        self.data_type_heatmap_create = None
        self.longitude_heatmap_create = None
        self.latitude_heatmap_create = None
        self.depth_heatmap_create = None
        self.combine_formatted_heatmap_create = None

        self.country_heatmap_update = None
        self.reference_point_heatmap_update = None
        self.state_heatmap_update = None
        self.status_heatmap_update = None
        self.tsunami_heatmap_update = None
        self.magnitudo_heatmap_update = None
        self.significance_heatmap_update = None
        self.data_type_heatmap_update = None
        self.longitude_heatmap_update = None
        self.latitude_heatmap_update = None
        self.depth_heatmap_update = None
        self.datetime_heatmap_update = None

        #article data
        self.link_g_article_create = None
        self.judul_article_create  = None
        self.konten_article_create  = None
        self.link_v_article_create  = None

        self.link_g_article_update = None
        self.judul_article_update = None
        self.kontent_article_update = None
        self.link_v_article_update = None
        
        #user data 
        self.name_user_create = None
        self.email_user_create = None
        self.password_user_create = None
        self.address_user_create = None
        self.is_admin_user_create = None

        self.name_user_update = None
        self.email_user_update = None
        self.password_user_update= None
        self.address_user_update= None
        self.is_admin_user_update = None

    
    def set_controller(self,controller):
        self.controller = controller

    @staticmethod
    def render(earthquake_data):
        st.title("MVC with Streamlit, Folium, and USGS Earthquake Data")
        
        # Display a Streamlit element
        st.write("Earthquake Data:", earthquake_data)

        # Create a Folium map
        my_map = folium.Map(location=[37.7749, -122.4194], zoom_start=3)

        # Add earthquake markers to the map
        for earthquake in earthquake_data:
            coordinates = earthquake['geometry']['coordinates']
            magnitude = earthquake['properties']['mag']
            location = [coordinates[1], coordinates[0]]
            popup_text = f"Magnitude: {magnitude}"
            folium.Marker(location, popup=popup_text).add_to(my_map)

        # Display the map using Streamlit's folium_chart
        folium_static(my_map)
    
    def show_map(self,df):
        m = folium.Map(location=[-0.789275 , 113.921327], zoom_start=3, zoom_control=False)
        for index, row in df.iterrows():
            if row['place'] is not None:
                place_parts = row['place'].split(",")
                kota = place_parts[0]
                if len(place_parts) > 1:
                    negara = place_parts[1].strip()
                else:
                    negara = "No country information available"
            else:
                kota = 'No place information available'
            magnitude = row['mag']
            kedalaman = row['depth']
            waktu = row['time']
            lat = row['latitude']
            lon = row['longitude']

            # Membuat teks popup yang lebih informatif
            popup_text = f"""
            <strong>Earthquake Information:</strong><br>
            Magnitude: {magnitude}<br>
            Region: {kota}<br>
            Country: {negara}<br>
            Depth: {kedalaman} km<br>
            Time of Occurrence: {waktu}
            """

            folium.CircleMarker(
                location=[lat, lon],
                popup=folium.Popup(popup_text, max_width=250),
                radius=float(magnitude)*2,
                icon=folium.Icon(icon="cloud"),
            ).add_to(m)

        st.markdown("""
            <style>
            iframe {
                width: 100%;
                height: 100%:
            }
            </style>
            """, unsafe_allow_html=True)
        return folium_static(m,  height=600)
    
    def show_heatmap(self,df):
        geometry = geopandas.points_from_xy(df.longitude, df.latitude)
        geo_df = geopandas.GeoDataFrame(df[df.columns],
                            geometry=geometry)
        m = folium.Map(location=[-0.789275 , 113.921327], tiles="Cartodb dark_matter", zoom_start=3)
        heat_data = [[point.xy[1][0], point.xy[0][0]] for point in geo_df.geometry]

        plugins.HeatMap(heat_data).add_to(m)

        pivot_df = geo_df.pivot_table(index = ['state','reference_point'], values = ['latitude','longitude'])
        pivot_df.reset_index()

        geometry_pivot = geopandas.points_from_xy(pivot_df.longitude, pivot_df.latitude)
        geo_pivot = geopandas.GeoDataFrame(pivot_df.reset_index(),geometry = geometry_pivot)
        #marker_data = [[point.xy[1][0], point.xy[0][0]] for point in geo_pivot.loc[geo_dfs['state']=='Indonesia'].geometry]
        counts_event = geo_df['reference_point'].value_counts()
        geo_pivot['counts'] = geo_pivot['reference_point'].map(counts_event)
        
        for i, row in geo_pivot.iterrows():
            popup_text = f"""
            <strong>Earthquake Information:</strong><br>
            Region: {row['reference_point']}<br>
            Country: {row['state']}<br>
            Number of Occurrences: {str(row['counts'])}
            """

            folium.Marker(location=[row.geometry.y, row.geometry.x],popup = popup_text).add_to(m)
        
        st.markdown("""
            <style>
            iframe {
                width: 100%;
                height: 100%:
            }
            </style>
            """, unsafe_allow_html=True)
        return folium_static(m,  height=600)

    def table(self,df):
        # Konfigurasi GridOptionsBuilder
        gb = GridOptionsBuilder.from_dataframe(df)
        gb.configure_default_column(
            editable=False, filter=False, resizable=True, sortable=True, value=True, 
            enablePivot=True, enableValue=True, floatingFilter=True, aggFunc='sum', 
            flex=1, minWidth=150, width=150, maxWidth=200
        )
        gb.configure_selection(selection_mode='multiple', use_checkbox=True)
        gb.configure_pagination(enabled=True, paginationAutoPageSize=True)
        gridOptions = gb.build()

        # Konfigurasi Grid
        grid = AgGrid(
            df,
            gridOptions=gridOptions,
            data_return_mode=DataReturnMode.AS_INPUT,
            update_on='MANUAL',
            enable_quicksearch=True,
            fit_columns_on_grid_load=True,
            theme=AgGridTheme.STREAMLIT,
            enable_enterprise_modules=True,
            height=600,
            width='100%',
            custom_css={
                "#gridToolBar": {
                    "padding-bottom": "0px !important",
                }
            }
        )

        return grid
    
    def table_admin(self,df,status):
        # Konfigurasi GridOptionsBuilder
        if status == 'aktif':
            status = True
        elif status == 'tidak':
            status = False
        else:
            status = False
        gb = GridOptionsBuilder.from_dataframe(df)
        gb.configure_default_column(
            editable=False, filter=False, resizable=True, sortable=True, value=True, 
            enablePivot=True, enableValue=True, floatingFilter=True, aggFunc='sum', 
            flex=1, minWidth=150, width=150, maxWidth=200
        )
        gb.configure_selection(selection_mode='multiple', use_checkbox=status)
        gb.configure_pagination(enabled=True, paginationAutoPageSize=True)
        gridOptions = gb.build()

        # Konfigurasi Grid
        grid = AgGrid(
            df,
            gridOptions=gridOptions,
            data_return_mode=DataReturnMode.AS_INPUT,
            update_on='MANUAL',
            enable_quicksearch=True,
            fit_columns_on_grid_load=True,
            theme=AgGridTheme.STREAMLIT,
            enable_enterprise_modules=True,
            height=600,
            width='100%',
            custom_css={
                "#gridToolBar": {
                    "padding-bottom": "0px !important",
                }
            }
        )

        return grid
    
    def css(self):
        css = """
        <style>
            .stButton>button {
                width: 100%;
                height: 50px;
                font-size: 20px;
            }
            div[data-testid="stToolbar"] {
            visibility: hidden;
            height: 0%;
            position: fixed;
            }
            div[data-testid="stDecoration"] {
            visibility: hidden;
            height: 0%;
            position: fixed;
            }
            div[data-testid="stStatusWidget"] {
            visibility: hidden;
            height: 0%;
            position: fixed;
            }
            #MainMenu {
            visibility: hidden;
            height: 0%;
            }
            header {
            visibility: hidden;
            height: 0%;
            }
            footer {
            visibility: hidden;
            height: 0%;
            }

        </style>
        """
        st.markdown(css, unsafe_allow_html=True)
    
    def hidetopbar(self):
        hide_streamlit_style ="""
        <style>
        #MainMenu {visibility: hidden;}
        footer {visibility: hidden;}
        header {visibility: hidden;}
        div.embeddedAppMetaInfoBar_container__DxxL1 {visibility: hidden;}
        </style>

        """
        st.markdown(hide_streamlit_style, unsafe_allow_html=True)
    
    def menubar(self,status):
        if status == 'user':
            menu_data = [
                {
                    'icon': "fa-solid fa-radar",
                    'label': "Earthquake Prone Points",
                    'submenu': [
                        {'id': 'heatmap', 'icon': "fa fa-thermometer-full", 'label': "Heatmap"},
                        {'id': 'graph', 'icon': "fa fa-chart-bar", 'label': "Graph"},
                        {'id': 'data', 'icon': "fa fa-database", 'label': "Data"}
                    ]
                },
                {
                    'id': 'article',
                    'icon': "fa fa-newspaper",
                    'label': "Article"
                }
            ]
            over_theme = {'txc_inactive': '#FFFFFF','menu_background':'#262730'}
            self.menu_id = hc.nav_bar(
                menu_definition=menu_data,
                override_theme=over_theme,
                home_name='Home',
                login_name='Logout',
                hide_streamlit_markers=True,
                sticky_nav=True,
                sticky_mode='fixed',  # Change 'pinned' to 'fixed'
            )
        if status == 'guest':
            menu_data = [
                {
                    'icon': "fa-solid fa-radar",
                    'label': "Earthquake Prone Points",
                    'submenu': [
                        {'id': 'heatmap', 'icon': "fa fa-thermometer-full", 'label': "Heatmap"},
                        {'id': 'graph', 'icon': "fa fa-chart-bar", 'label': "Graph"}
                    ]
                },
                {
                    'id': 'article',
                    'icon': "fa fa-newspaper",
                    'label': "Article"
                },
                {'id': 'register', 'icon': "fa fa-user-plus", 'label': "Register"}
            ]
            over_theme = {'txc_inactive': '#FFFFFF','menu_background':'#262730'}
            self.menu_id = hc.nav_bar(
                menu_definition=menu_data,
                override_theme=over_theme,
                home_name='Home',
                login_name='Login',
                hide_streamlit_markers=True,
                sticky_nav=True,
                sticky_mode='fixed',  # Change 'pinned' to 'fixed'
            )
    
    def title(self,title):
        st.title(title)
        
    def header(self,header):
        st.header(header)
    
    def homeviewfilter(self,df):
        with st.sidebar:     
            st.subheader('Filter Data')
            col1,col2 = st.columns(2)
            try:
                with col1:
                    start_date = st.date_input('Start Date', value=pd.to_datetime(df['time_date'].min()), help="Mulai Hari", min_value=pd.to_datetime(df['time_date'].min()), max_value=pd.to_datetime(df['time_date'].max()), key='start_date')
                with col2:
                    end_date = st.date_input('End Date', value=pd.to_datetime(df['time_date'].max()), help="Akhir Hari", min_value=pd.to_datetime(df['time_date'].min()), max_value=pd.to_datetime(df['time_date'].max()))

                df = df[(df['time_date'] >= start_date) & (df['time_date'] <= end_date)]
            except Exception as e:
                st.sidebar.warning(f'error: {e}')
            try:
                if len(df['status'].unique()) <= 1:
                    with col1:
                        selected_status = st.selectbox('Select Status', df['status'].unique(), disabled=True)
                else:
                    with col1:
                        selected_status = st.selectbox('Select Status', df['status'].unique())

                if not selected_status:
                    selected_status=""
                    df = df
                else:
                        df = df[df['status'].isin([selected_status])]
            except Exception as e:
                st.sidebar.warning(f'error: {e}')
            
            try:
                if len(df['tsunami'].unique()) <= 1:
                    with col2:
                        selected_tsunami = st.selectbox('Select Tsunami', df['tsunami'].unique(), disabled=True, help="Terjadi Tsunami = 1\nTidak Tsunami = 0")
                else:
                    with col2:
                        selected_tsunami = st.selectbox('Select Tsunami', df['tsunami'].unique())
                if not selected_tsunami:
                    selected_tsunami=""
                    df = df
                else:
                        df = df[df['status'].isin(selected_tsunami)]
            except Exception as e:
                st.sidebar.warning(f'error: {e}')
                
            
            try:
                selected_reference_point = st.multiselect('Select Reference Point', df['reference_point'].unique())
                if not selected_reference_point:
                    selected_reference_point=""
                    df = df
                else:
                    df = df[df['reference_point'].isin(selected_reference_point)]
            except Exception as e:
                st.sidebar.warning(f'error: {e}')
            try:
                if len(df) <= 1:
                    selected_mag = st.slider('Select Magnitude',disabled=True)
                else:
                    selected_mag = st.slider('Select Magnitude', min_value=df['mag'].min(), max_value=df['mag'].max(), value=(df['mag'].min(), df['mag'].max()))
                if not selected_mag:
                    selected_mag=""
                    df = df
                else:
                    df = df[df['mag'].between(selected_mag[0], selected_mag[1])]
            except Exception as e:
                st.sidebar.warning(f'error: {e}')
            try:
                if len(df) <= 1:
                    selected_depth = st.slider('Select Depth',disabled=True)
                else:
                    selected_depth = st.slider('Select Depth', min_value=df['depth'].min(), max_value=df['depth'].max(), value=(df['depth'].min(), df['depth'].max()))
                if not selected_depth:
                    selected_depth=""
                    df = df
                else:
                    df = df[df['depth'].between(selected_depth[0], selected_depth[1])]
            except Exception as e:
                st.sidebar.warning(f'error: {e}')
            
            return df
        
    def graphviewfilter(self,df):
        with st.sidebar:     
            st.subheader('Filter Data')
            col1,col2 = st.columns(2)
            try:
                df['time_date'] = df['date'].dt.date
                with col1:
                    start_date = st.date_input('Start Date', value=pd.to_datetime(df['time_date'].min()), help="Mulai Hari", min_value=pd.to_datetime(df['time_date'].min()), max_value=pd.to_datetime(df['time_date'].max()), key='start_date')
                with col2:
                    end_date = st.date_input('End Date', value=pd.to_datetime(df['time_date'].max()), help="Akhir Hari", min_value=pd.to_datetime(df['time_date'].min()), max_value=pd.to_datetime(df['time_date'].max()))

                df = df[(df['time_date'] >= start_date) & (df['time_date'] <= end_date)]
            except Exception as e:
                st.sidebar.warning(f'error: {e}')
            
            try:
                selected_reference_point = st.multiselect('Select Reference Point', df['reference_point'].unique())
                if not selected_reference_point:
                    selected_reference_point=""
                    df = df
                else:
                    df = df[df['reference_point'].isin(selected_reference_point)]
            except Exception as e:
                st.sidebar.warning(f'error: {e}')
            
            return df

    def heatmapviewfilter(self,df):
        with st.sidebar:     
            st.subheader('Filter Data')
            col1,col2 = st.columns(2)
            try:
                df['time_date'] = df['date'].dt.date
                with col1:
                    start_date = st.date_input('Start Date', value=pd.to_datetime(df['time_date'].min()), help="Mulai Hari", min_value=pd.to_datetime(df['time_date'].min()), max_value=pd.to_datetime(df['time_date'].max()), key='start_date')
                with col2:
                    end_date = st.date_input('End Date', value=pd.to_datetime(df['time_date'].max()), help="Akhir Hari", min_value=pd.to_datetime(df['time_date'].min()), max_value=pd.to_datetime(df['time_date'].max()))

                df = df[(df['time_date'] >= start_date) & (df['time_date'] <= end_date)]
            except Exception as e:
                st.sidebar.warning(f'error: {e}')
            
            try:
                if len(df['dayperiod']) <= 1:
                    with col1:
                        selected_dayperiod = st.multiselect('Select Categorical Day Periode', df['dayperiod'].unique(),disabled=True)
                else:
                    with col1:
                        selected_dayperiod = st.multiselect('Select Categorical Day Periode', df['dayperiod'].unique())
                if not selected_dayperiod:
                    selected_dayperiod=""
                    df = df
                else:
                    df = df[df['dayperiod'].isin(selected_dayperiod)]
            except Exception as e:
                st.sidebar.warning(f'error: {e}')
            
            try:
                if len(df['season']) <= 1:
                    with col2:
                        selected_season = st.multiselect('Select Categorical Season', df['season'].unique(),disabled=True)
                else:
                    with col2:
                        selected_season = st.multiselect('Select Categorical Season', df['season'].unique())
                if not selected_season:
                    selected_season=""
                    df = df
                else:
                    df = df[df['season'].isin(selected_season)]
            except Exception as e:
                st.sidebar.warning(f'error: {e}')

            try:
                if len(df['status'].unique()) <= 1:
                    with col1:
                        selected_status = st.selectbox('Select Status', df['status'].unique(), disabled=True)
                else:
                    with col1:
                        selected_status = st.selectbox('Select Status', df['status'].unique())

                if not selected_status:
                    selected_status=""
                    df = df
                else:
                        df = df[df['status'].isin([selected_status])]
            except Exception as e:
                st.sidebar.warning(f'error: {e}')
            
            try:
                if len(df['tsunami'].unique()) <= 1:
                    with col2:
                        selected_tsunami = st.selectbox('Select Tsunami', df['tsunami'].unique(), disabled=True, help="Terjadi Tsunami = 1, Tidak Tsunami = 0")
                else:
                    with col2:
                        selected_tsunami = st.selectbox('Select Tsunami', df['tsunami'].unique(), help="Terjadi Tsunami = 1, Tidak Tsunami = 0")
                if not selected_tsunami:
                    selected_tsunami=""
                    df = df
                else:
                    df = df[df['tsunami'] == int(selected_tsunami)]
            except Exception as e:
                st.sidebar.warning(f'error: {e}')

            try:
                selected_reference_point = st.multiselect('Select Reference Point', df['reference_point'].unique())
                if not selected_reference_point:
                    selected_reference_point=""
                    df = df
                else:
                    df = df[df['reference_point'].isin(selected_reference_point)]
            except Exception as e:
                st.sidebar.warning(f'error: {e}')
            
            try:
                if len(df['categorical earthquake']) <= 1:
                    selected_categorical_earthquake = st.multiselect('Select Categorical Earthquake', df['categorical earthquake'].unique(),disabled=True)
                else:
                    selected_categorical_earthquake = st.multiselect('Select Categorical Earthquake', df['categorical earthquake'].unique())
                if not selected_categorical_earthquake:
                    selected_categorical_earthquake=""
                    df = df
                else:
                    df = df[df['categorical earthquake'].isin(selected_categorical_earthquake)]
            except Exception as e:
                st.sidebar.warning(f'error: {e}')
            
            try:
                if len(df['depth category']) <= 1:
                    selected_categorical_depth = st.multiselect('Select Categorical Depth', df['depth category'].unique(),disabled=True)
                else:
                    selected_categorical_depth = st.multiselect('Select Categorical Depth', df['depth category'].unique())
                if not selected_categorical_depth:
                    selected_categorical_depth=""
                    df = df
                else:
                    df = df[df['depth category'].isin(selected_categorical_depth)]
            except Exception as e:
                st.sidebar.warning(f'error: {e}')
            
            
            try:
                if len(df) <= 1:
                    selected_mag = st.slider('Select Magnitude',disabled=True)
                elif df['magnitudo'].min() == df['magnitudo'].max():
                    selected_mag = st.slider('Select Magnitude',disabled=True)
                else:
                    selected_mag = st.slider('Select Magnitude', min_value=df['magnitudo'].min(), max_value=df['magnitudo'].max(), value=(df['magnitudo'].min(), df['magnitudo'].max()))
                if not selected_mag:
                    selected_mag=""
                    df = df
                else:
                    df = df[df['magnitudo'].between(selected_mag[0], selected_mag[1])]
            except Exception as e:
                st.sidebar.warning(f'error: {e}')
            try:
                if len(df) <= 1:
                    selected_depth = st.slider('Select Depth',disabled=True)
                elif df['depth'].min() == df['depth'].max():
                    selected_depth = st.slider('Select Depth',disabled=True)

                else:
                    selected_depth = st.slider('Select Depth', min_value=df['depth'].min(), max_value=df['depth'].max(), value=(df['depth'].min(), df['depth'].max()))
                if not selected_depth:
                    selected_depth=""
                    df = df
                else:
                    df = df[df['depth'].between(selected_depth[0], selected_depth[1])]
            except Exception as e:
                st.sidebar.warning(f'error: {e}')
            
            return df
        
    def graphview_barchart(self,data):
        try:
            columns = st.selectbox('Select Categorical Features: ',['dayperiod','categorical earthquake','season','depth category'],index=0)
            if not columns:
                data = data
                columns = ''
            else:
                if columns == 'dayperiod':
                    st.bar_chart(data = data[columns].value_counts().rename_axis('time session').reset_index(name='amount'),x = 'time session',y = 'amount')
                elif columns == 'categorical earthquake':
                    st.bar_chart(data=data[columns].value_counts().rename_axis('strength level').reset_index(name='amount'),
                                x='strength level', y='amount')
                elif columns == 'season':
                    st.bar_chart(data=data[columns].value_counts().rename_axis('season').reset_index(name='amount'),
                                x='season', y='amount')
                elif columns == 'depth category':
                    st.bar_chart(data=data[columns].value_counts().rename_axis('depth level').reset_index(name='amount'),
                                x='depth level', y='amount')
        except:
            pass
    
    def graphview_barchart2(self,data):
        df = data
        try:
            columns = st.selectbox('Select Category Numerical', ['year', 'quarter', 'month', 'latitude', 'longitude', 'depth', 'magnitudo'], index=0)
            if columns:
                if columns in ['year', 'quarter', 'month']:
                    st.bar_chart(data=df[columns].value_counts().rename_axis(columns).reset_index(name='count'), x=columns, y='count')
                elif columns in ['latitude', 'longitude', 'depth', 'magnitudo']:
                    st.bar_chart(data=df[[columns]].value_counts().rename_axis(columns).reset_index(name='count'), x=columns, y='count')
        except Exception as e:
            st.write(f"Error: {e}")
        
        columns = st.selectbox('Select Category   ', ['based on feature categories','based on magnitude distribution'], index=0)
        if columns == 'based on feature categories':
            try:
                # Select specific category
                category = st.selectbox('Select Category', ['dayperiod', 'categorical earthquake', 'season', 'depth category'], index=0)

                # Select year
                year = st.selectbox('Year', list(df['year'].unique()), index=0)

                if not category:
                    df_filtered = df
                    category = ''
                else:
                    altair_data = df.sort_values(by='year')
                    altair_data = altair_data[['year', category]].value_counts().reset_index(name='amount')
                    altair_data = altair_data.sort_values(by='year')

                    # Create Altair chart
                    c = alt.Chart(altair_data[altair_data['year'].isin([year])]).mark_bar().encode(
                        alt.Column('year'),
                        alt.X(category),
                        alt.Y('amount'),
                        alt.Color(category, legend=alt.Legend(orient='bottom')),
                        tooltip=[category, 'amount']
                    ).properties(
                        height=437,
                        width=952
                    ).configure_axis(
                        labelColor='white',
                        titleColor='white'
                    )

                    # Show Altair chart
                    st.altair_chart(c,theme="streamlit", use_container_width=True)
            except Exception as e:
                st.error(f"An error occurred: {e}")
        
        elif columns == 'based on magnitude distribution':
            try:
                columns = st.selectbox('Select Category ', ['dayperiod', 'season', 'depth category'], index=0)
                if not columns:
                    data = data
                    columns = ''
                else:
                    c = alt.Chart(data).mark_boxplot().encode(
                        y='magnitudo', x=columns
                    )
                    st.altair_chart(c, theme="streamlit", use_container_width=True)
            except:
                pass
    
    def Summarizeview_user(self,df):
        user_df = df
        # Menghitung Total Users dan New Users
        total_users = user_df.shape[0]
        new_users = user_df[user_df['created_at'] == user_df['updated_at']].shape[0]  # Anggaplah yang 'created_at' dan 'updated_at' sama sebagai New Users

        # Menghitung Persentase New Users
        
        percentage_new_users = (new_users / total_users) * 100 if total_users > 0 else 0
        nested_col1,nested_col2,nested_col3 = st.columns(3)
        with nested_col1:
            st.metric("Total Users", total_users)
        with nested_col2:
            st.metric("New Users", new_users)
        with nested_col3:
            st.metric("Persentase New Users", f"{percentage_new_users:.2f}%")
    
    def graphview_user(self,df):
        user_df = df
        columns = st.selectbox('Analytics', ['New Users','User Address','Last Update Time', 'User Creation Time', 'Admin and Non-Admin Distribution'], index=0)
        if columns == 'Admin and Non-Admin Distribution':
            # Visualization of Admin and Non-Admin Distribution
            st.subheader("Admin and Non-Admin Distribution")
            admin_distribution = user_df['is_admin'].value_counts()
            st.bar_chart(admin_distribution)


        elif columns == 'User Creation Time':
            # Visualization of User Creation Time
            st.subheader("User Creation Time")
            user_df['created_at'] = pd.to_datetime(user_df['created_at'])
            created_at_chart = alt.Chart(user_df).mark_bar().encode(
                x='created_at:T',
                y='count()',
                tooltip=['count()']
            ).properties(width=600, height=400)
            st.altair_chart(created_at_chart,use_container_width=True)


        elif columns == 'User Address':
            # Visualization of User Address (Only displaying address without geographic plot)
            st.subheader("User Address")
            st.table(user_df[['name', 'alamat']])

        elif columns == 'Last Update Time':
            # Visualization of Last Update Time
            day = st.selectbox(label='Lastest Day',options=[1,3,7])
            time_threshold = datetime.datetime.now() - datetime.timedelta(days=day)
            user_df = user_df[user_df['updated_at'] > time_threshold]
            st.subheader("Last Update Time")
            user_df['updated_at'] = pd.to_datetime(user_df['updated_at'])
            st.write(user_df.sort_values('updated_at', ascending=False))

        elif columns == 'New Users':
            # Filter pengguna non-admin yang baru
            non_admin_users = user_df[[user_df['is_admin'] == '0'] and ['name','email','alamat','created_at']]

            day = st.selectbox(label='Days',options=[1,3,7])
            time_threshold = datetime.datetime.now() - datetime.timedelta(days=day)
            new_users = non_admin_users[non_admin_users['created_at'] > time_threshold]

            # Menampilkan tabel waktu pembuatan terakhir untuk pengguna baru
            st.subheader("New Users")
            latest_users = new_users.sort_values('created_at', ascending=True).groupby(new_users['created_at'].dt.date).last()
            st.table(latest_users)

    def asuserview(self):  
        self.menubar('user')

        if str(self.menu_id) == "Home":
            self.homeview()
        elif str(self.menu_id) == "heatmap":
            self.heatmapview()
        elif str(self.menu_id) == "graph":
            self.graphview()
        elif str(self.menu_id) == "data":
            self.dataview()
        elif str(self.menu_id) == "article":
            self.articleview()
        elif str(self.menu_id) == "Logout":
            self.logoutview()
    
    def asguestview(self):
        self.menubar('guest')

        if str(self.menu_id) == "Home":
            self.homeview()
        elif str(self.menu_id) == "heatmap":
            self.heatmapview()
        elif str(self.menu_id) == "graph":
            self.graphview()
        elif str(self.menu_id) == "article":
            self.articleview()
        elif str(self.menu_id) == "register":
            self.registerview()
        elif str(self.menu_id) == "Login":
            self.loginview()
    
    def asadminview(self):
        login_status, self.user_info = st.session_state.login
        with st.sidebar:
            st.subheader(f'Hallo _Selamat Datang_ :blue[Kembali] {self.user_info["name"]} :sunglasses:')
            selected = option_menu("QuakeVigilant Admin Dashboard", ["Dashboard","Earthquake Management","Article Management", "User Management",'Settings'], 
                icons=['house','list-task','list-task', 'person', 'gear'], menu_icon="bi bi-database", default_index=0)
            #st.write(selected)
        if selected == "Dashboard":
            self.dashboardadminview()
        elif selected == "Earthquake Management":
            self.earthquakemanagementadminview()
        elif selected == "Article Management":
            self.articlemanagementadminview()
        elif selected == "User Management":
            self.useremanagementadminview()
        elif selected == "Settings":
            self.settingsadminview()        
    
    def run(self):
        # Use the provided controller instance
        self.hidetopbar()
        self.css()
        
        if not st.session_state.get('login', False):
            self.asguestview()
        else:
            login_status, user_info = st.session_state.login
            if login_status == 'berhasil':
                if user_info.get('is_admin') == 1:
                    self.asadminview()
                else:
                    self.asuserview()
                
            else:
                st.write('tidak')
    
    def dashboardadminview(self):
        self.title("Dashboard")
        self.controller.Summarizeview_user()
        self.controller.graphview_user()
        st.markdown("---")
    
    def earthquakemanagementadminview(self):
        self.title("EarthQuake Management")
        editmode = st.toggle(label = "Edit Mode")  
        status = 'tidak'
        if editmode == True:  
            status = 'aktif'
            st.download_button(label="Export CSV",data=self.controller.df_heatmap.to_csv(),file_name="QuakeVigilant_earthquake.csv") 
        grid = self.table_admin(self.controller.df_heatmap, status)   
        selected_rows = grid['selected_rows']
        
        if editmode == True:
            if not grid.selected_rows:
                with st.form("create_form", clear_on_submit=True):
                    self.country_heatmap_create = st.text_input(label="Country")
                    self.Reference_Point_heatmap_create = st.text_input(label="Reference Point")
                    self.state_heatmap_create = st.text_input(label="State")
                    self.status_heatmap_create = st.selectbox(label="Status",options=['reviewed', 'automatic', 'manual'])
                    self.tsunami_heatmap_create = st.selectbox(label="Tsunami", options=[0, 1])
                    self.magnitudo_heatmap_create = st.number_input(label="Magnitudo")
                    self.significance_heatmap_create = st.number_input(label="Significance", step=1)
                    self.data_type_heatmap_create = st.selectbox(label="Data Type",options=['earthquake', 'quarry blast', 'explosion', 'other event', 'nuclear explosion', 'rock burst', 'ice quake', 'chemical explosion', 'sonic boom', 'mine collapse', 'rockslide', 'rock slide', 'accidental explosion', 'landslide', 'quarry', 'mining explosion', 'acoustic noise', 'not reported', 'experimental explosion', 'collapse', 'meteorite', 'induced or triggered event', 'volcanic eruption', 'ice quake', 'snow avalanche'])          
                    self.longitude_heatmap_create = st.number_input(label="Longitude")
                    self.latitude_heatmap_create = st.number_input(label="Latitude")
                    self.depth_heatmap_create = st.number_input(label="Depth")
                    date = st.date_input(label="Date")
                    time = st.time_input(label="Time")
                    combine = datetime.datetime.combine(date, time)
                    self.combine_formatted_heatmap_create = combine.strftime('%Y-%m-%dT%H:%M:%S')
                    submitted = st.form_submit_button("Submit")

                    if submitted:
                        self.controller.createdata_heatmap(self.country_heatmap_create, 
                            self.Reference_Point_heatmap_create, self.state_heatmap_create, self.status_heatmap_create, 
                            self.tsunami_heatmap_create,self.magnitudo_heatmap_create, self.significance_heatmap_create, 
                            self.data_type_heatmap_create, self.longitude_heatmap_create, self.latitude_heatmap_create, self.depth_heatmap_create, 
                            self.combine_formatted_heatmap_create
                        )
            else:
                id_heatmap = [row.get("id") for row in selected_rows]              
                if len(grid.selected_rows) == 1:
                    with st.form("update_form"):
                        st.text_input(label="id",placeholder=grid.selected_rows[0]['id'],disabled=True)
                        self.country_heatmap_update = st.text_input(label="Country", value=grid.selected_rows[0]['country'])
                        self.reference_point_heatmap_update = st.text_input(label="Reference Point", value=grid.selected_rows[0]['reference_point'])
                        self.state_heatmap_update = st.text_input(label="State", value=grid.selected_rows[0]['state'])
                        self.status_heatmap_update = st.selectbox(label="Status",options=['reviewed', 'automatic', 'manual'], index=0 if grid.selected_rows[0]['status'] == 'reviewed' else 1 if grid.selected_rows[0]['status'] == 'automatic' else 2)      
                        self.tsunami_heatmap_update = st.selectbox(label="Tsunami", options=[0, 1], index=0 if grid.selected_rows[0]['tsunami'] == 0 else 1)
                        self.magnitudo_heatmap_update = st.number_input(label="Magnitudo", value=grid.selected_rows[0]['magnitudo'])
                        self.significance_heatmap_update = st.number_input(label="Significance", step=1, value=grid.selected_rows[0]['significance'])
                        self.data_type_heatmap_update = st.selectbox(label="Data Type",options=['earthquake', 'quarry blast', 'explosion', 'other event', 'nuclear explosion', 'rock burst', 'ice quake', 'chemical explosion', 'sonic boom', 'mine collapse', 'rockslide', 'rock slide', 'accidental explosion', 'landslide', 'quarry', 'mining explosion', 'acoustic noise', 'not reported', 'experimental explosion', 'collapse', 'meteorite', 'induced or triggered event', 'volcanic eruption', 'ice quake', 'snow avalanche'], index = 0 if grid.selected_rows[0]['data_type'] == 'earthquake' else 1 if grid.selected_rows[0]['data_type'] == 'quarry blast' else 2 if grid.selected_rows[0]['data_type'] == 'explosion' else 3 if grid.selected_rows[0]['data_type'] == 'other event' else 4 if grid.selected_rows[0]['data_type'] == 'nuclear explosion' else 5 if grid.selected_rows[0]['data_type'] == 'rock burst' else 6 if grid.selected_rows[0]['data_type'] == 'ice quake' else 7 if grid.selected_rows[0]['data_type'] == 'chemical explosion' else 8 if grid.selected_rows[0]['data_type'] == 'sonic boom' else 9 if grid.selected_rows[0]['data_type'] == 'mine collapse' else 10 if grid.selected_rows[0]['data_type'] == 'rockslide' else 11 if grid.selected_rows[0]['data_type'] == 'rock slide' else 12 if grid.selected_rows[0]['data_type'] == 'accidental explosion' else 13 if grid.selected_rows[0]['data_type'] == 'landslide' else 14 if grid.selected_rows[0]['data_type'] == 'quarry' else 15 if grid.selected_rows[0]['data_type'] == 'mining explosion' else 16 if grid.selected_rows[0]['data_type'] == 'acoustic noise' else 17 if grid.selected_rows[0]['data_type'] == 'not reported' else 18 if grid.selected_rows[0]['data_type'] == 'experimental explosion' else 19 if grid.selected_rows[0]['data_type'] == 'collapse' else 20 if grid.selected_rows[0]['data_type'] == 'meteorite' else 21 if grid.selected_rows[0]['data_type'] == 'induced or triggered event' else 22 if grid.selected_rows[0]['data_type'] == 'volcanic eruption' else 23 if grid.selected_rows[0]['data_type'] == 'ice quake' else 24)          
                        self.longitude_heatmap_update = st.number_input(label="Longitude", value=grid.selected_rows[0]['longitude'])
                        self.latitude_heatmap_update = st.number_input(label="Latitude", value=grid.selected_rows[0]['latitude'])
                        self.depth_heatmap_update = st.number_input(label="Depth", value=grid.selected_rows[0]['depth'])
                        update_date = st.date_input(label="Date",value= datetime.datetime.strptime(grid.selected_rows[0]['date'], '%Y-%m-%dT%H:%M:%S').date())
                        update_time = st.time_input(label="Time", value = datetime.datetime.strptime(grid.selected_rows[0]['date'], '%Y-%m-%dT%H:%M:%S').time())
                        combine_datetime = datetime.datetime.combine(update_date, update_time)
                        self.datetime_heatmap_update = combine_datetime.strftime('%Y-%m-%dT%H:%M:%S')
                        
                        col1,col2 = st.columns(2)
                        with col1:
                            if len(grid.selected_rows) == 1:           
                                delete_button = st.form_submit_button("Delete")
                                if delete_button:            
                                    self.controller.deletedata_heatmap(id_heatmap)
                        with col2:
                            if len(grid.selected_rows) == 1:           
                                update_button = st.form_submit_button("Update")
                                if update_button:
                                    self.controller.updatedata_heatmap(
                                    self.country_heatmap_update,
                                    self.reference_point_heatmap_update,
                                    self.state_heatmap_update,
                                    self.status_heatmap_update,
                                    self.tsunami_heatmap_update,
                                    self.magnitudo_heatmap_update,
                                    self.significance_heatmap_update,
                                    self.data_type_heatmap_update,
                                    self.longitude_heatmap_update,
                                    self.latitude_heatmap_update,
                                    self.depth_heatmap_update,
                                    self.datetime_heatmap_update,
                                    str(id_heatmap[0])
                                )
                
                if len(grid.selected_rows) != 1:   
                    st.write([row.get("id") for row in selected_rows])
                    delete_button = st.button(f"Delete({len(grid.selected_rows)})")
                    if delete_button:            
                        self.controller.deletedata_heatmap(id_heatmap)
        
        st.markdown("---")

                     
    def articlemanagementadminview(self):
        self.title("Article Management")
        now = datetime.datetime.now()
        editmode = st.toggle(label = "Edit Mode")  
        status = 'tidak'
        if editmode == True:  
            status = 'aktif'
            st.download_button(label="Export CSV",data=self.controller.df_artikel.to_csv(),file_name="QuakeVigilant_artikel.csv") 
        grid = self.table_admin(self.controller.df_artikel, status)  
        selected_rows = grid['selected_rows']
        if editmode == True:
            if not grid.selected_rows:
                with st.form("add_form", clear_on_submit=True):
                    self.link_g_article_create = st.text_input(label="Link Gambar")
                    self.judul_article_create = st.text_input(label="Judul")
                    self.konten_article_create = st.text_area(label="Konten")
                    self.link_v_article_create = st.text_input(label="Link Vidio")
                    tanggal_p_input = now.strftime("%Y-%m-%d %H:%M:%S")
                    penulis = st.text_input(label="Penulis", value=self.user_info['name'],disabled=True)
                    penulis_id = self.user_info['id']

                    # Add the submit button here
                    submitted = st.form_submit_button("Submit")
                    if submitted:
                        self.controller.createdata_article(
                            self.link_g_article_create, self.judul_article_create,self.konten_article_create, self.link_v_article_create,tanggal_p_input,penulis_id
                        )
            else:
                id_article = [row.get("id") for row in selected_rows]              
                if len(grid.selected_rows) == 1:
                    with st.form("update_form"):
                        st.text_input(label="id",placeholder=grid.selected_rows[0]['id'],disabled=True)
                        self.link_g_article_update = st.text_input(label="Link Gambar",placeholder=grid.selected_rows[0]['link_gambar'])
                        self.judul_article_update = st.text_input(label="Judul",placeholder=grid.selected_rows[0]['judul'])
                        self.kontent_article_update = st.text_area(label="Konten",placeholder=grid.selected_rows[0]['konten'])
                        self.link_v_article_update = st.text_input(label="Link Vidio",placeholder=grid.selected_rows[0]['link_vidio'])
                        update_tanggal_p = now.strftime("%Y-%m-%d %H:%M:%S")
                        
                        col1,col2 = st.columns(2)
                        with col1:
                            if len(grid.selected_rows) == 1:           
                                delete_button = st.form_submit_button("Delete")
                                if delete_button:
                                    self.controller.deletedata_article(id_article)
                        with col2: 
                            if len(grid.selected_rows) == 1:   
                                update_button = st.form_submit_button("Update")
                                if update_button:
                                    self.controller.updatedata_article(self.link_g_article_update,self.judul_article_update,self.kontent_article_update,self.link_v_article_update,update_tanggal_p,str(id_article[0]))
                        
                if len(grid.selected_rows) != 1:   
                    st.write(id_article)
                    delete_button = st.button(f"Delete({len(grid.selected_rows)})")
                    if delete_button:            
                        self.controller.deletedata_article(id_article)
                    
        st.markdown("---")
    def useremanagementadminview(self):
        self.title("User Management")
        now = datetime.datetime.now()
        editmode = st.toggle(label = "Edit Mode")  
        status = 'tidak'
        if editmode == True:  
            status = 'aktif'
            st.download_button(label="Export CSV",data=self.controller.df_user.to_csv(),file_name="QuakeVigilant_user.csv") 
        grid = self.table_admin(self.controller.df_user, status)
        selected_rows = grid['selected_rows']
        if editmode == True:
            if not grid.selected_rows:
                with st.form("create_user",clear_on_submit=True):

                    self.name_user_create = st.text_input(label="Name")
                    self.email_user_create = st.text_input(label="Email")
                    self.password_user_create = st.text_input(label="Password")
                    home_address_input = st.text_area(label="Home Address")
                    city_input = st.text_input(label="City or Regency")
                    province_input = st.text_input(label="Province")
                    country_input = st.text_input(label="Country")
                    self.address_user_create =  f"{home_address_input}, {city_input}, {province_input}, {country_input}"
                    created_at_input = now.strftime("%Y-%m-%d %H:%M:%S")
                    update_at_input = now.strftime("%Y-%m-%d %H:%M:%S")
                    is_admin = st.radio('Admin',['0','1'])
                    self.is_admin_user_create = is_admin
                    submitted = st.form_submit_button("Submit")  

                    if submitted:
                        self.controller.createdata_user(
                            self.name_user_create, self.email_user_create, self.password_user_create, 
                            self.address_user_create, created_at_input, update_at_input, 
                            self.is_admin_user_create
                        )
            else:
                id_user = [row.get("id") for row in selected_rows] 
                if len(grid.selected_rows) == 1:
                    with st.form("update_user"):
                        st.text_input(label="id",placeholder=grid.selected_rows[0]['id'],disabled=True)
                        self.name_user_update = st.text_input(label="name",value=grid.selected_rows[0]['name'])
                        self.email_user_update = st.text_input(label="email",value=grid.selected_rows[0]['email'])
                        self.password_user_update= st.text_input(label="password",value=grid.selected_rows[0]['password'])
                        update_home_address_input = st.text_area(label="Home Address",value=grid.selected_rows[0]['alamat'].split(',')[0])
                        update_city_input = st.text_input(label="City or Regency",value=grid.selected_rows[0]['alamat'].split(',')[1])
                        update_province_input = st.text_input(label="Province",value=grid.selected_rows[0]['alamat'].split(',')[2])
                        update_country_input = st.text_input(label="Country",value=grid.selected_rows[0]['alamat'].split(',')[3])
                        self.address_user_update= f"{update_home_address_input}, {update_city_input}, {update_province_input}, {update_country_input}"
                        update_at_input = now.strftime("%Y-%m-%d %H:%M:%S")
                        if "0" ==  str(grid.selected_rows[0]['is_admin']):
                            index_is_admin = 0
                        else:
                            index_is_admin = 1
                        update_is_admin = st.radio('Admin',['0','1'],index_is_admin)
                        self.is_admin_user_update = update_is_admin

                        col1,col2 = st.columns(2)
                        with col1:
                            if len(grid.selected_rows) == 1:           
                                delete_button = st.form_submit_button("Delete")
                                if delete_button:            
                                    self.controller.deletedata_user(id_user)
                        with col2: 
                            if len(grid.selected_rows) == 1:   
                                update_button = st.form_submit_button("Update")
                                if update_button:
                                    self.controller.updatedata_user(
                                        self.name_user_update,
                                        self.email_user_update,
                                        self.password_user_update,
                                        self.address_user_update,
                                        update_at_input,
                                        self.is_admin_user_update,
                                        str(id_user[0])
                                    )
                if len(grid.selected_rows) != 1:   
                    st.write(id_user)
                    delete_button = st.button(f"Delete({len(grid.selected_rows)})")
                    if delete_button:            
                        self.controller.deletedata_user(id_user)

        st.markdown("---")

    def settingsadminview(self):
        self.title("Settings")
        self.logoutview()


        
    
    def homeview(self):
        self.title('QuakeVigilant Magnitudo 2.5+, 1 Week')
        if not st.session_state.get('login', False):
            pass
        else:
            login_status, user_info = st.session_state.login  
            with st.sidebar:
                st.subheader(f'Hallo _Selamat Datang_ :blue[Kembali] {user_info["name"]} :sunglasses:')


        self.controller.filtered_map_usgs()

        showtable = st.toggle(label="show table")
        if showtable:
            self.controller.table_usgs()
        else:
            self.controller.map_usgs()
        
        st.header('Summarize QuakeVigilant Magnitudo 2.5+, 1 Week') 
        col1,col2,col3,col4 = st.columns(4)
        with col1:
            st.metric(label="Total Earthquakes", value=len(self.controller.df))
        with col2:
            st.metric(label="Minimum Magnitude", value=self.controller.df['mag'].min())
        with col3:
            st.metric(label="Maximum Magnitude", value=self.controller.df['mag'].max())
        with col4:
            st.metric(label="Average Magnitude", value=f"{self.controller.df['mag'].mean():.2f}")
        st.markdown("---")
    
    def graphview(self):
        self.controller.filtered_graph()
        self.controller.title_graph()
        self.graphview_barchart(self.controller.df_heatmap)
        self.graphview_barchart2(self.controller.df_heatmap)
        st.markdown("---")
        
    
    def heatmapview(self):
        self.controller.filtered_map_heatmap()
        self.controller.title_heatmap()
        
        #self.controller.table_heatmap()
        self.controller.map_heatmap()
        

        # Display largest earthquake
        df = self.controller.df_heatmap
        self.controller.header_heatmap()
        col1,col2,col3,col4 = st.columns(4)
        largest_earthquake = df.loc[df['magnitudo'].idxmax()]
        average_highest_magnitude = df.groupby('reference_point')['magnitudo'].max().mean()
        smallest_earthquake = df.loc[df['magnitudo'].idxmin()]
        most_frequent_location = df['reference_point'].mode().iloc[0]
        average_lowest_magnitude = df.groupby('state')['magnitudo'].min().mean()
        least_frequent_location = df['state'].value_counts().idxmin()

        with col1:
            st.metric("Largest Earthquake", f"{largest_earthquake['magnitudo']} Magnitude", f"{largest_earthquake['reference_point']} - {largest_earthquake['date']}")
            st.metric("Most Frequent Location", f"{most_frequent_location}", f"Occurrences: {df[df['reference_point'] == most_frequent_location].shape[0]} times")
        
        
        with col2:
            st.metric("Smallest Earthquake", f"{smallest_earthquake['magnitudo']} Magnitude", f"{smallest_earthquake['reference_point']} - {smallest_earthquake['date']}")
            st.metric("Least Frequent Location", f"{least_frequent_location}", f"Occurrences: {df[df['state'] == least_frequent_location].shape[0]} times")
        with col3:       
            st.metric("Average Highest Magnitude", f"{average_highest_magnitude:.2f} Magnitude")  
            st.metric("Average Lowest Magnitude", f"{average_lowest_magnitude:.2f} Magnitude") 
        with col4:    
            st.metric(label='Total Tsunami', value=df[df['tsunami']==1].shape[0])
            st.metric(label='Total Earthquakes', value=df[df['tsunami']==0].shape[0])
        st.markdown("---")

    def dataview(self):
        self.controller.filtered_map_heatmap()
        self.controller.title_data()
        st.download_button(label="Download CSV",data=self.controller.df_heatmap.to_csv(),file_name="quake_vigilant.csv")
        self.controller.table_heatmap()
    
    def articleview(self):
        
        articles = self.controller.list_article()
        self.title('List of Articles Mitigasi Bencana Gempa Bumi')

        # Create a list of article titles for the selectbox
        article_titles = [article['element']['judul'] for article in articles]

        # Display selectbox to choose an article
        selected_article_title = st.selectbox("Select an Article", article_titles)

        # Find the selected article based on the title
        selected_article = next((article for article in articles if article['element']['judul'] == selected_article_title), None)

        # Display the selected article
        if selected_article:
            st.write(f"## {selected_article['element']['judul']}")
            col1,col2,col3 = st.columns(3)
            try:
                with col2:
                    st.image(selected_article['element']['link_gambar'], caption='Image', width=300)
            except:

                st.image('data:image/jpeg;base64,/9j/4AAQSkZJRgABAQAAAQABAAD/2wCEAAkGBw8NDQ0NDQ0PDQ0NDw0NDg8ODRANDQ0NFREWFhURFRUYHSggGBolGxgTITEhJSkrLi4uFx8zODMtNygtLisBCgoKBQUFDgUFDisZExkrKysrKysrKysrKysrKysrKysrKysrKysrKysrKysrKysrKysrKysrKysrKysrKysrK//AABEIAMkA+wMBIgACEQEDEQH/xAAbAAEBAQEBAQEBAAAAAAAAAAAAAQUGBAMCB//EADYQAQACAAIFCAkEAwEAAAAAAAABAgMRBAUSITETFUFRUpLB0SIyM1NhcYKRokJyobGBsuFi/8QAFAEBAAAAAAAAAAAAAAAAAAAAAP/EABQRAQAAAAAAAAAAAAAAAAAAAAD/2gAMAwEAAhEDEQA/AP6EigCZKgKioCgAAAgqSAoAAAIoAAAAAigIqKAAAIoCKgCgAioAQoAAAACAAoAIoAAAAAgoAkqkgCoAoAAAIqAoACZKgKioCgACSoIBIKAACAqKgKIoCKgKCSBAQSCiKAAAioCgAIqAqKgKAAACEkkgoPvgaFiYnq0nLtW9GoPgtazM5REzPVEZy2NH1NWN+JabfCvox5tDDwqYUejFaR08I+8gxdH1TiX9bLDj477fZpYGq8KmUzG3PXbfH24PzpGtcOm6ueJP/n1fu8uja1vfFrFoitLTs5Rv3zwnMHy11gbGJFojKLx0dqOPgz3Ra1wOUwbZetX04/xxj7ZudAAASVSQICAFAAAARUBQAEVAVFQFBAUerR9XYuJv2dmOu27+OLT0fU+HXfeZvPdr9gYmHh2vOVazafhGbQ0fU17b72ikdUelbybNa1plWIisdERlD9g8uj6vwsPhXOe1b0pfrSNNw8P1rxn1Rvt9nz0jRMTEzice1YnorWIj78Xl5jj3s92AfPSNczO7Drs/G2+fszsbGviTne02+fD7cGrzJHvZ7sHMce9nuwDHTP79HzbPMce9nuwcxx72e7ANDQ8blcOt+uN/z4S53TMHk8S9OiJzr+2d8N/QdE5Gs125tEznGcZZbnz07V8Y1q22prMRluiJzgHPDY5kj3s92EtqWIiZ5Wd0TPqwDISSFBIJABQAAARUBQAAQFRUBX10XG5PEpfoid/y4S+SA67PdnG/p3dLCx9b4lt1IjDjvW8mjqjH28GvXT0J/wAcP4ZOtcHYxrdV/Tj5zx/kH61ZebaRSbTNp9LfM5z6stjWGkzg4cXiItviuUzlxYuqfb0+r/WWlrz2P118Qebnu3u696fI57v7uvenyZTUwNTWtXO99iZ/TFdrL57wOe7e7r3p8l57t7uvenyeLTNEtg2ytlMTviY4S84NXnu3u696fI57t7uvenyZaA1ee7e7r3p8jnu3u696fJlKDTnXdvd170+TYvOdJnrrP9OTng6ufU+nwBykKkAKhACiQoAACKgBkAECoBIAAqA0NS4+zi7E8MSMvqjh4vdrvB2sPbjjhzn9M7p8GHS01mLRxrMTHzh1FLRi4cT+m9f4mAYOqPb0+r/WWlrz2P118Wfq7DmmlVpPGs3j8Z3tDXnsfrr4gxtFtFcTDtO6IvWZ+EZuqchk9WDp+LSNmt93RFoi2X3Boa/vGxSv6traj4VymJ/uGK/WJebzNrTNrTxmX5AbWqdBjYm+JG/EiaxE9FJ8/J4tV6Jyt87R6FMpnqmeirogcppGFOHe1J/TOWfXHRL5urtg0m23NKzaIyzmImcmJrvC2cXa6Lxn/mN0+AM6eDrJ9T6fBykusn1Pp8AclEKQSAAAEKCAAZAAoACKgKioCgANrUWNnS2HPGk5x+2f+/2xXo1djcni1nPKJ9G3yn/uQNbGwMtKwsSOF4tWf3RWfD+k157H66+LQmsTlnHCc4+E5ZPBrz2Mfvr4gwRM2zqrV+WWLiRv40r1fGfiD8aPqjaw5m8zW876xx2Y6p63ivoOJXEjDmu+05VmPVmOvN0wD5aNgRhUileEdPTM9MvqADO13hZ4W100mJ/xO6fBovxj4e3S1Z/VEx94ByduDq59T6fByl4yzieMZxPzh1c+p9PgDlIJIAAgBRFAAARUBQSAVFQFRUBQQFQAdNq7H5TCpbpy2bfujc+GvPY/XXxePUmkRW1qWmIi0bUTM5RtR/z+mxy1O3XvQDla2ymJjjE574zh6+dMbt/hXyb/AC1O3TvQctTt070AwOdMbt/hXyOdMbt/hXyb/LU7dO9By1O3TvQDA50xu3+FfI50xu3+FfJv8tTt070HLU7dO9AMDnTG7f4V8jnTG7f4V8m/y1O3TvQctTt070A5XEtNptaeM5zO7Le6qfU+nwOWp26d6H5xMamzb068J/VHUDloVI4AEBACiKAAAioCgmYKioCoqAoICiKCGQSBl8DKFQDL4GRmAZQZfBUAyMoADL4GSoCpISAEEgKigAAIAKIAoICiAKIAogCoAKIAogCiAKIAogCiKAIAoigCAKgACoCoqAAACoACggAAAAqAAACoAAACggACooICggAEBABAQABIAAASSSAEgBkKCAQAAAEAAAAAAAAAAEAAA//Z',caption='Image', use_column_width=True)
            st.write(f"{selected_article['element']['konten']}")
            col1,col2,col3 = st.columns(3)
            try:
                with col2:
                    st.video(selected_article['element']['link_vidio'])
                st.write(f"**Video Link:** {selected_article['element']['link_vidio']}")
            except:
                st.write(f"**Video Link:** ")
            st.write(f"**Title:** {selected_article['element']['judul']}")
            st.write(f"**Penulis:** {selected_article['element']['penulis']}")
            st.write(f"**Publication Date:** {selected_article['element']['tanggal_publikasi']}")
            st.markdown("---")
    
    def registerview(self):
        self.title('Register')
        now = datetime.datetime.now()
        indexCity = self.controller.get_city()

        if "temp_register" not in st.session_state:
            st.session_state.temp_register = []

        def step1():
            st.session_state["stage"] = "step1"

        def step2():
            st.session_state["stage"] = "step2"

        def step3():
            st.session_state["stage"] = "step3"

        def step4():
            st.session_state["stage"] = "step4"

        def finalstep():
            st.session_state["stage"] = "finalstep"

        def Confrimation():
            st.session_state["stage"] = "confirmation"

        if "stage" not in st.session_state:
            st.session_state["stage"] = "step1"

        if st.session_state["stage"] == "step1":
            with st.form("step1_form"):
                st.header('Step 1: Personal Information')
                name_user_register = st.text_input(label="name")
                email_user_register = st.text_input(label="email")
                password_user_register = st.text_input(label="password", type='password')
                confirm_pw_user_register = st.text_input(label="confirm password", type='password')

                submitted = st.form_submit_button(
                    "Next"
                )
                if submitted:
                    if password_user_register != confirm_pw_user_register:
                        st.info('password Tidak Sama')
                    else:
                        st.session_state.temp_register.append([name_user_register,email_user_register,password_user_register,confirm_pw_user_register])
                        step2()
                        st.experimental_rerun()

        elif st.session_state["stage"] == "step2":
            with st.form("step2_story_form"):
                st.header('Step 2: Country')
                country_input = st.selectbox(label="Country", options=['Indonesia'])
                submitted = st.form_submit_button("Next")
                if submitted:
                    st.session_state.temp_register.append([country_input])
                    step3()
                    st.experimental_rerun()
                prev = st.form_submit_button("Prev")
                if prev:
                    st.session_state.temp_register.pop()
                    step1()
                    st.experimental_rerun()
                    
        elif st.session_state["stage"] == "step3":
            with st.form("step3_params_form"):
                st.header('Step 3: Province')
                province_options = list(indexCity.keys())
                province_input = st.selectbox(label="Province", options=province_options)
                submitted = st.form_submit_button("Next")
                if submitted:
                    st.session_state.temp_register.append([province_input])
                    step4()
                    st.experimental_rerun()
                prev = st.form_submit_button("Prev")
                if prev:
                    st.session_state.temp_register.pop()
                    step2()
                    st.experimental_rerun()
                    
        elif st.session_state["stage"] == "step4":
            with st.form("step4_params_form"):
                st.header('Step 4: City')
                city_options = indexCity
                city_input = st.selectbox(label="City", options=city_options.get(st.session_state.temp_register[2][0], []))
                home_address_input = st.text_input(label="Home Address")
                submitted = st.form_submit_button("Next")
                if submitted:
                    st.session_state.temp_register.append([city_input,home_address_input])
                    finalstep()
                    st.experimental_rerun()
                prev = st.form_submit_button("Prev")
                if prev:
                    st.session_state.temp_register.pop()
                    step3()
                    st.experimental_rerun()

        elif st.session_state["stage"] == "finalstep":
            st.write(str(st.session_state.temp_register[2][0]))
            with st.form("finalstep_params_form"):
                st.header('Final Step: Confrimation User Infomation')
                self.name_user_register = st.text_input(label="name", value=st.session_state.temp_register[0][0], disabled=True)
                self.email_user_register = st.text_input(label="email", value=st.session_state.temp_register[0][1], disabled=True)
                self.password_user_register = st.text_input(label="password", value=st.session_state.temp_register[0][2], type='password', disabled=True)
                country_input = st.text_input(label="Country", value=st.session_state.temp_register[1][0], disabled=True)
                province_input = st.text_input(label="Province", value=st.session_state.temp_register[2][0], disabled=True)
                city_input = st.text_input(label="City", value=st.session_state.temp_register[3][0], disabled=True)
                home_address_input = st.text_input(label="Home Address" , value=st.session_state.temp_register[3][1], disabled=True)
                self.address_user_register = f"{home_address_input}, {city_input}, {province_input}, {country_input}"
                self.created_at_user_register = now.strftime("%Y-%m-%d %H:%M:%S")
                self.update_at_user_register = now.strftime("%Y-%m-%d %H:%M:%S")
                self.is_admin_user_register = 0                
                submitted = st.form_submit_button("Submit")
                if submitted:
                    self.controller.register_myuser(
                        self.name_user_register, self.email_user_register,self.password_user_register,
                        self.address_user_register, self.created_at_user_register, self.update_at_user_register, self.is_admin_user_register
                    )
                    st.write('Register')
                    Confrimation()
                    st.experimental_rerun()
                    
                prev = st.form_submit_button("Prev")
                if prev:
                    st.session_state.temp_register.pop()
                    step4()
                    st.experimental_rerun()

        elif st.session_state["stage"] == "confirmation":
            st.balloons()
            with st.form("confirmation_params_form"):
                st.header('Selamat Akun Anda Telah Dibuat')
                submitted = st.form_submit_button("Kembali")
                if submitted:
                    st.session_state.temp_register=[]
                    st.write('Kembali')
                    step1()
                    st.experimental_rerun()
        
        st.markdown("---")
                





    
    def loginview(self):
        self.title('Login')
        self.login_email = ""
        self.login_password = ""

        st.session_state.login = ""
        st.session_state.user = ""
        with st.form("login_user",clear_on_submit=True):
            self.login_email = st.text_input('Masukan Email')
            self.login_password = st.text_input('Masukan Password', type='password')  # Use password input for sensitive information
            login_btn = st.form_submit_button('Login')

        if login_btn:
            if self.login_email == "" and self.login_password =="":
                st.warning('Email and Password Cannot Be Empty')
                st.session_state.login = ""
                pass
            elif self.login_email == "" or self.login_password =="":
                st.warning('Email or Password Is Empty')
                st.session_state.login = ""
                pass
            else:
                st.session_state.login = self.controller.login_validation(self.login_email, self.login_password)
                login_status, self.user_info = st.session_state.login
                

                if str(login_status) == 'berhasil':
                    # Clear the input fields after successful login
                    st.info(str(login_status))
                    
                    st.experimental_rerun()
                    return True
                else:
                    st.session_state.login = ''
                    st.warning('Email or Password Is Wrong')


        if not st.session_state.get('login', False):
            return False
    
    def logoutview(self):
        st.header('Personal Information')
        now = datetime.datetime.now()
        login_status, user_info = st.session_state.login
        edit = st.toggle('Edit Profile')
        if edit:
            editmode = False
        else:
            editmode = True
        with st.form("edit_myuser"):            
            self.name_user= st.text_input(label='Name',value=user_info['name'],disabled=editmode)
            self.email_user = st.text_input(label='Email',value=user_info['email'],disabled=editmode)
            self.password_user = st.text_input(label='Password',value=user_info['password'] , type='password',disabled=editmode)
            self.address_user = st.text_input(label="Home Address",value=user_info['alamat'],disabled=editmode)  
            self.update_at_input_user = now.strftime("%Y-%m-%d %H:%M:%S")
            submitted = st.form_submit_button('Submit',disabled=editmode)
            if submitted:
                st.session_state.update = self.controller.update_myuser(self.name_user,self.email_user,self.password_user,self.address_user,self.update_at_input_user,user_info['id'])

        if login_status == 'berhasil':
            if st.button('Logout'):
                  # Check if the Logout button is clicked
                st.session_state.login = ""  # Clear the login session state
                st.experimental_rerun()
                
        else:
            st.warning("Login gagal. Mohon cek kembali email dan password.")
        
        st.markdown("---")

                
                

            

    
    
    
