#!/usr/bin/env python
# -*- coding:utf-8 -*-
# Author: baoyi
# Datetime: 2021/4/9 15:20

import streamlit as st


def app():
    """
    高德key 列表
    :return:
    """
    gaode_key = [
        '901f8abddd706c256363a8567912e3df',
        '833a2b9ddc84d0cd90b099495047870e',
        'd5f97a92d78647719590ee9f63649a84',
        '07426221af0f5aa9f195eedeeda211bb'
    ]

    baidu_key = [
        'g1d3kEqUqIHVj2NykEDTnTzuV4hjEaQn',
        'yuGIkVIXKtk3vufXgTYGoxjCCRt6kl1I',
        'g10grGAmympbLU4a784fy4hRvtkyC19s',
        '74Fin4u49bzBkqh4BQaHidTBm1ScwGY9'
    ]

    st.title('高德Key')
    st.write(gaode_key)
    st.text("")
    st.title('百度Key')
    st.write(baidu_key)
