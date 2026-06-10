
import streamlit as st
import pandas as pd
from pathlib import Path

BASE_DIR = Path(__file__).parent

detail_file = BASE_DIR / "2026年以来_补全A股_企业年金职业年金明细.xlsx"
summary_file = BASE_DIR / "2026年以来_补全A股_年金计划投资者汇总.xlsx"

@st.cache_data
def load_data():
    detail_df = pd.read_excel(detail_file).fillna("").astype(str)
    summary_df = pd.read_excel(summary_file).fillna("").astype(str)
    return detail_df, summary_df
detail_df, summary_df = load_data()

st.sidebar.header("查询条件")

keyword = st.sidebar.text_input("输入配售对象 / 投资者 / 股票名称")
annuity_type = st.sidebar.selectbox("年金类型", ["全部", "企业年金", "职业年金"])

filtered_detail = detail_df.copy()
filtered_summary = summary_df.copy()

if keyword:
    filtered_detail = filtered_detail[
        filtered_detail.astype(str).apply(
            lambda row: row.str.contains(keyword, case=False, na=False).any(),
            axis=1
        )
    ]

    filtered_summary = filtered_summary[
        filtered_summary.astype(str).apply(
            lambda row: row.str.contains(keyword, case=False, na=False).any(),
            axis=1
        )
    ]

if annuity_type != "全部":
    filtered_detail = filtered_detail[
        filtered_detail.astype(str).apply(
            lambda row: row.str.contains(annuity_type, na=False).any(),
            axis=1
        )
    ]

    filtered_summary = filtered_summary[
        filtered_summary.astype(str).apply(
            lambda row: row.str.contains(annuity_type, na=False).any(),
            axis=1
        )
    ]

col1, col2 = st.columns(2)
col1.metric("年金明细记录数", len(filtered_detail))
col2.metric("汇总计划数量", len(filtered_summary))

tab1, tab2 = st.tabs(["按计划汇总", "明细数据"])

with tab1:
    st.subheader("各年金计划对应投资者")
    st.dataframe(filtered_summary, use_container_width=True)

    st.download_button(
        "下载当前汇总结果",
        filtered_summary.to_csv(index=False).encode("utf-8-sig"),
        "年金计划投资者汇总_查询结果.csv",
        "text/csv"
    )

with tab2:
    st.subheader("年金网下配售明细")
    st.dataframe(filtered_detail, use_container_width=True)

    st.download_button(
        "下载当前明细结果",
        filtered_detail.to_csv(index=False).encode("utf-8-sig"),
        "年金网下配售明细_查询结果.csv",
        "text/csv"
    )
