import streamlit as st


def app():
    st.title('Home')

    st.subheader("Introduction")
    st.markdown("We are the **Spatio-Temporal Social Sensing Lab of Peking University ($S^3$-Lab).**")
    st.markdown("We are developing this tool platform based on [Python](https://python.org) and [Streamlit](https://streamlit.io), \
        the purpose is to facilitate GISers to quickly grab data, obtain information and finally complete the work.")
    
    st.subheader("Function")
    st.markdown("Currently, the existing functions of the platform are as follows:")
    st.markdown("- Visualization and download system of urban bus lines")
    st.markdown("- Amap POI Crawling System")
    st.markdown("- Amap/Bmap API Key")
    st.markdown("**If you have any questions or ideas, feel free to contact us!**")
    
    st.subheader("Contributors")
    st.markdown("@[CUGbaoyi](https://github.com/CUGbaoyi), @[sunshineYin](https://github.com/sunshineYin), @[HanwGeek](https://github.com/HanwGeek)")

    st.subheader("Affiliation")
    # st.write("<img src='https://i.loli.net/2021/04/12/qxTjodCSg72KksW.jpg' height='50%' width='50%'/>")
    st.image('https://i.loli.net/2021/04/12/qxTjodCSg72KksW.jpg')
