import streamlit as st
from multiapp import MultiApp
from apps import home, busline, poi, gaodekey

app = MultiApp()

st.markdown("""
# PKU $S^{3}$ lab GeoTools

""")

# Add all your application here
app.add_app("Home", home.app)
app.add_app("城市公交线路可视化及下载系统", busline.app)
app.add_app("高德POI抓取系统", poi.app)
app.add_app("高德APP Key", gaodekey.app)

# The main app
app.run()
