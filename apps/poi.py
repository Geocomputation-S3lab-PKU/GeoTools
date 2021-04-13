"""
Author: Ganmin Yin, Yi Bao
Date: 2021-04-12 15:09:17
LastEditTime: 2021-04-12 16:58:12
Description: A simple tool to get poi information from Amap.
"""

import requests
import streamlit as st
import geopandas as gpd
import pandas as pd
import time
import base64
import io
from fiona.io import ZipMemoryFile
from sqlalchemy import create_engine
from utils.trans import gcj02_to_wgs84

# POI的type-code对应字典
poi_type_code = {
    '全部': '010000|020000|030000|040000|050000|060000|070000|080000|090000|100000|110000|120000|130000|140000|150000'
          '|160000|170000|180000|190000|200000',
    '汽车服务': '010000', '汽车销售': '020000', '汽车维修': '030000', '摩托车服务': '040000',
    '餐饮服务': '050000', '购物服务': '060000', '生活服务': '070000', '体育休闲服务': '080000',
    '医疗保健服务': '090000', '住宿服务': '100000', '风景名胜': '110000', '商务住宅': '120000',
    '政府机构及社会团体': '130000', '科教文化服务': '140000', '交通设施服务': '150000', '金融保险服务': '160000',
    '公司企业': '170000', '道路附属设施': '180000', '地名地址信息': '190000', '公共设施': '200000',
}


def get_bound_by_name(name: str, key: str):
    """
    @description: 通过城市名，获取边界
    @param {str} name: 城市名
    @param {str} key: 高德Key
    @return {*}
    """

    url = f'https://restapi.amap.com/v3/config/district?keywords={name}&subdistrict=1&extensions=all&key={key}'
    res = requests.get(url).json()
    polyline = res['districts'][0]['polyline']
    points = polyline.split(";")

    lon_lst = []
    lat_lst = []

    for point in points:
        lon, lat = float(point.split(',')[0]), float(point.split(',')[1])
        lon_lst.append(lon)
        lat_lst.append(lat)

    min_lon, max_lon = min(lon_lst), max(lon_lst)
    min_lat, max_lat = min(lat_lst), max(lat_lst)

    return [[min_lon, min_lat, max_lon, max_lat]]


def get_bound_by_file(file):
    """
    @description: 通过上传文件，获得边界
    @param {*} file
    @return {*}
    """
    # streamlit.fileuploader转geodataframe
    zip_shp = io.BytesIO(file.read())
    with (ZipMemoryFile(zip_shp)) as memfile:
        with memfile.open() as src:
            crs = src.crs
            city = gpd.GeoDataFrame.from_features(src, crs=crs)

    # 遍历每一个geometry
    polygon_list = []
    for geo in city.geometry:
        min_lon, min_lat, max_lon, max_lat = geo.bounds
        min_lon = round(min_lon, 6)
        min_lat = round(min_lat, 6)
        max_lon = round(max_lon, 6)
        max_lat = round(max_lat, 6)

        polygon_list.append([min_lon, min_lat, max_lon, max_lat])
    return polygon_list


def download_file(data, name='data', file_label='File'):
    """
    @description: 下载文件到本地
    @param {*} data
    @param {*} name
    @param {*} file_label
    @return {*}
    """

    if isinstance(data, pd.DataFrame):
        data = data.to_csv(index=False)
    bin_str = base64.b64encode(data.encode()).decode()
    href = f'<a href="data:file/txt;base64,{bin_str}" download="{name}.csv">下载 {file_label}</a> '
    return href


# 抓取POI的类
class CrawlPOI:
    def __init__(self, key, polygon, keywords, types):
        self.key = key
        self.polygon = polygon
        self.keywords = keywords
        self.types = types

    def get_poi(self):
        page = 1
        poi_data = []
        while True:
            try:
                url = f'https://restapi.amap.com/v3/place/polygon?key={self.key}&polygon={self.polygon}&keywords={self.keywords}&types={self.types}&offset=20&page={page}&extensions=base'
                res = requests.get(url).json()
                # print(res['count'])
                if res['pois']:
                    pois = res['pois']
                    for poi in pois:
                        # print(poi)
                        poi_id = poi['id']
                        poi_name = poi['name']
                        poi_type = poi['type']
                        poi_typecode = poi['typecode']
                        poi_lon, poi_lat = list(map(float, poi['location'].split(',')))
                        # 坐标转换
                        poi_lon, poi_lat = gcj02_to_wgs84(poi_lon, poi_lat)

                        poi_info = [poi_id, poi_name, poi_type, poi_typecode, poi_lon, poi_lat]
                        poi_data.append(poi_info)

                    page += 1

                    # 判断下一页是否还有poi数据
                    if page > int(res['count']) // 20 + 1:
                        break

                else:
                    break

            except Exception as e:
                st.exception(e)

        return poi_data


def format_data(gap, polygon, key, keywords, types):
    """
    根据输入的gap 和 polygon边界
    @param gap:
    @param polygon:
    @param key:
    @param keywords:
    @param types:
    @return:
    """
    # geometry 正方形边界
    min_lon, min_lat, max_lon, max_lat = polygon

    # 拼接POI类型的字符串
    types_str = '|'.join([poi_type_code[t] for t in types])
    # 网格横向、纵向数量
    rows = int(((max_lat + gap) - min_lat) // gap)
    cols = int(((max_lon + gap) - min_lon) // gap)

    poi_lst = []

    for row in range(rows):
        for col in range(cols):
            ld = f'{min_lon + col * gap},{min_lat + row * gap}'
            lu = f'{min_lon + col * gap},{min_lat + (row + 1) * gap}'
            rd = f'{min_lon + (col + 1) * gap},{min_lat + row * gap}'
            ru = f'{min_lon + (col + 1) * gap},{min_lat + (row + 1) * gap}'
            # 每个网格作为一个小多边形
            subpolygon = '|'.join([ld, lu, ru, rd, ld])

            # 爬虫抓取POI
            crawler = CrawlPOI(key, subpolygon, keywords, types_str)
            sub_poi_lst = crawler.get_poi()
            poi_lst += sub_poi_lst

    # print(poi_lst)
    poi_df = pd.DataFrame(poi_lst, columns=['id', 'name', 'type', 'typecode', 'lon', 'lat'])

    return poi_df


def download_from_db(disk_engine, table_name, st_status):
    """
    访问数据库
    @param st_status:
    @param disk_engine:
    @param table_name: 下载中间数据
    @return:
    """
    df = pd.read_sql_query(f'SELECT * FROM {table_name}', disk_engine)
    st_status.markdown(download_file(df, name="poi_data", file_label='当前POI数据'), unsafe_allow_html=True)


def crawl():
    """
    @description: 抓取POI的函数
    @param {*}
    @return {*}
    """
    st.title("高德POI抓取系统")
    st.markdown("输入高德Key、抓取区域、关键词、POI类别即可抓取，支持下载与可视化(WGS-84)")

    # 输入key
    # key = st.text_input("输入高德API Key：", value='901f8abddd706c256363a8567912e3df')
    key = st.text_input("输入高德API Key：")
    # 选择输入区域方式，2种
    option = st.selectbox("选择抓取区域", ['1. 输入城市名', '2. 输入shp文件'])

    # 读取边界
    polygon = None
    if option == '1. 输入城市名':
        city = st.text_input("")
        # city = st.text_input("", value='北京')
        if key and city:
            polygon = get_bound_by_name(city, key)

    if option == '2. 输入shp文件':
        city = st.file_uploader("上传文件(GCJ-02), 直接将shapefile相关文件右键压缩，不要压缩文件夹", type='zip')
        if not city:
            st.info("Please upload a file of type: zip")
        else:
            polygon = get_bound_by_file(city)

    # 输入关键词
    keywords = st.text_input("输入关键词：")
    # 输入POI类别
    types = st.multiselect('选择POI类别：', list(poi_type_code.keys()))

    # 判断是否使用临时数据库
    if_db = st.checkbox("是否使用临时数据库(可以下载中间数据)")
    if if_db:
        table_name = st.text_input("输入数据库名:")
    else:
        table_name = ''

    # 网格边长0.01度
    gap = 0.01

    # 定义sqlite数据库
    disk_engine = create_engine('sqlite://', echo=True)

    # poi result
    poi_result = []

    if st.button("点击开始抓取"):
        with st.spinner("3秒后开始抓取"):
            time.sleep(3)

        # 初始化进度条文字信息
        status_txt = st.empty()
        # 初始化进度条
        pb = st.progress(0)
        tb_table = st.dataframe()
        st_status = st.empty()

        if polygon:
            count = 0
            for index, geo in enumerate(polygon):
                # 抓取一个geometry的数据
                poi_data = format_data(gap=gap, polygon=geo, key=key, keywords=keywords, types=types)
                poi_data['polygon_id'] = [index] * poi_data.shape[0]
                poi_result.append(poi_data)
                # 插入数据库
                if if_db:
                    poi_data.to_sql(table_name, disk_engine, if_exists='append')
                    print(pd.read_sql_table(table_name, disk_engine).shape[0])
                count += poi_data.shape[0]
                pb.progress(100 * (index + 1) // len(polygon))
                status_txt.text(
                    "已完成进度：{0}%，\t已抓取：{1}条".format(100 * (index + 1) // len(polygon), count))

                # 往st.dataframe 添加行数据
                tb_table.add_rows(poi_data)

                if if_db:
                    download_from_db(disk_engine, table_name, st_status)

            if keywords and tb_table:
                result = pd.concat(poi_result)
                result = result.drop_duplicates()
                st.markdown(download_file(result, name="poi_data", file_label='POI CSV'), unsafe_allow_html=True)
                st.subheader("POI地图：")
                st.map(tb_table)


def app():
    crawl()
