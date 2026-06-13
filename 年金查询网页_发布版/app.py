import streamlit as st
import pandas as pd
from pathlib import Path

st.set_page_config(page_title="年金网下配售分析平台", layout="wide")

st.title("2026年以来A股IPO网下配售年金计划分析平台")

BASE_DIR = Path(__file__).parent

detail_file = BASE_DIR / "2026年以来_补全A股_企业年金职业年金明细.xlsx"
summary_file = BASE_DIR / "2026年以来_补全A股_年金计划投资者汇总.xlsx"

@st.cache_data
def load_data():
    detail_df = pd.read_excel(detail_file).fillna("").astype(str)
    summary_df = pd.read_excel(summary_file).fillna("").astype(str)
    return detail_df, summary_df

detail_df, summary_df = load_data()

investor_col = [c for c in detail_df.columns if "投资者名称" in c][0]
object_col = [c for c in detail_df.columns if "配售对象名称" in c][0]
stock_col = "股票名称"

tab1, tab2 = st.tabs(["基础查询", "机构对比分析"])

with tab1:
    st.subheader("基础查询")

    keyword = st.text_input("输入配售对象 / 投资者 / 股票名称", key="basic_keyword")

    filtered = detail_df.copy()

    if keyword:
        filtered = filtered[
            filtered.astype(str).apply(
                lambda row: row.str.contains(keyword, case=False, na=False).any(),
                axis=1
            )
        ]

    col1, col2 = st.columns(2)
    col1.metric("年金明细记录数", len(filtered))
    col2.metric("汇总计划数量", len(summary_df))

    st.dataframe(filtered, use_container_width=True)

with tab2:
    st.subheader("机构对比分析")

    st.write("输入两家机构名称，查看哪些股票或年金计划是一方覆盖、另一方没有覆盖，哪些是双方共同覆盖。")

    col_a, col_b = st.columns(2)

    with col_a:
        org_a = st.text_input("机构A", value="南方基金")

    with col_b:
        org_b = st.text_input("机构B", value="易方达基金")

    a_df = detail_df[
        detail_df[investor_col].astype(str).str.contains(org_a, case=False, na=False)
    ].copy()

    b_df = detail_df[
        detail_df[investor_col].astype(str).str.contains(org_b, case=False, na=False)
    ].copy()

    a_stocks = set(a_df[stock_col].dropna().astype(str))
    b_stocks = set(b_df[stock_col].dropna().astype(str))

    only_a_stocks = sorted(a_stocks - b_stocks)
    only_b_stocks = sorted(b_stocks - a_stocks)
    both_stocks = sorted(a_stocks & b_stocks)

    a_objects = set(a_df[object_col].dropna().astype(str))
    b_objects = set(b_df[object_col].dropna().astype(str))

    only_a_objects = sorted(a_objects - b_objects)
    only_b_objects = sorted(b_objects - a_objects)
    both_objects = sorted(a_objects & b_objects)

    m1, m2, m3, m4 = st.columns(4)
    m1.metric(f"{org_a}获配股票数", len(a_stocks))
    m2.metric(f"{org_b}获配股票数", len(b_stocks))
    m3.metric("双方共同获配股票数", len(both_stocks))
    m4.metric("双方共同覆盖年金计划数", len(both_objects))

    ctab1, ctab2, ctab3, ctab4 = st.tabs([
        f"{org_a}有、{org_b}没有",
        f"{org_b}有、{org_a}没有",
        "双方都有",
        "年金计划覆盖差异"
    ])

    with ctab1:
        st.subheader(f"{org_a}获配但{org_b}未获配的股票")
        result = a_df[a_df[stock_col].isin(only_a_stocks)]
        st.dataframe(result, use_container_width=True)

    with ctab2:
        st.subheader(f"{org_b}获配但{org_a}未获配的股票")
        result = b_df[b_df[stock_col].isin(only_b_stocks)]
        st.dataframe(result, use_container_width=True)

    with ctab3:
        st.subheader("两家机构共同获配的股票")
        result = detail_df[
            detail_df[stock_col].isin(both_stocks)
            & detail_df[investor_col].astype(str).str.contains(
                f"{org_a}|{org_b}", case=False, na=False
            )
        ]
        st.dataframe(result, use_container_width=True)

    with ctab4:
        st.subheader(f"{org_a}覆盖但{org_b}未覆盖的年金计划")
        st.dataframe(pd.DataFrame({"配售对象名称": only_a_objects}), use_container_width=True)

        st.subheader(f"{org_b}覆盖但{org_a}未覆盖的年金计划")
        st.dataframe(pd.DataFrame({"配售对象名称": only_b_objects}), use_container_width=True)

        st.subheader("两家机构共同覆盖的年金计划")
        st.dataframe(pd.DataFrame({"配售对象名称": both_objects}), use_container_width=True)
