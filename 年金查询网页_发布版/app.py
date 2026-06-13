import streamlit as st
import pandas as pd
from pathlib import Path

st.set_page_config(page_title="年金打新机构对比", layout="wide")

st.title("2026年以来A股IPO网下配售年金计划分析平台")
st.success("新版机构对比分析功能已加载")

BASE_DIR = Path(__file__).parent

detail_file = BASE_DIR / "2026年以来_补全A股_企业年金职业年金明细.xlsx"
summary_file = BASE_DIR / "2026年以来_补全A股_年金计划投资者汇总.xlsx"

detail_df = pd.read_excel(detail_file).fillna("").astype(str)
summary_df = pd.read_excel(summary_file).fillna("").astype(str)

investor_col = [c for c in detail_df.columns if "投资者名称" in c][0]
object_col = [c for c in detail_df.columns if "配售对象名称" in c][0]
stock_col = "股票名称"

st.header("机构对比分析")

col_a, col_b = st.columns(2)

with col_a:
    org_a = st.text_input("机构A", "南方基金")

with col_b:
    org_b = st.text_input("机构B", "易方达基金")

a_df = detail_df[detail_df[investor_col].str.contains(org_a, case=False, na=False)]
b_df = detail_df[detail_df[investor_col].str.contains(org_b, case=False, na=False)]

a_stocks = set(a_df[stock_col])
b_stocks = set(b_df[stock_col])

only_a = sorted(a_stocks - b_stocks)
only_b = sorted(b_stocks - a_stocks)
both = sorted(a_stocks & b_stocks)

a_objects = set(a_df[object_col])
b_objects = set(b_df[object_col])

only_a_objects = sorted(a_objects - b_objects)
only_b_objects = sorted(b_objects - a_objects)
both_objects = sorted(a_objects & b_objects)

c1, c2, c3, c4 = st.columns(4)
c1.metric(f"{org_a}获配股票数", len(a_stocks))
c2.metric(f"{org_b}获配股票数", len(b_stocks))
c3.metric("共同获配股票数", len(both))
c4.metric("共同年金计划数", len(both_objects))

st.subheader(f"{org_a}有、{org_b}没有的股票")
st.dataframe(a_df[a_df[stock_col].isin(only_a)], use_container_width=True)

st.subheader(f"{org_b}有、{org_a}没有的股票")
st.dataframe(b_df[b_df[stock_col].isin(only_b)], use_container_width=True)

st.subheader("两家机构共同获配的股票")
both_df = detail_df[
    detail_df[stock_col].isin(both)
    & detail_df[investor_col].str.contains(f"{org_a}|{org_b}", case=False, na=False)
]
st.dataframe(both_df, use_container_width=True)

st.subheader(f"{org_a}覆盖但{org_b}未覆盖的年金计划")
st.dataframe(pd.DataFrame({"配售对象名称": only_a_objects}), use_container_width=True)

st.subheader(f"{org_b}覆盖但{org_a}未覆盖的年金计划")
st.dataframe(pd.DataFrame({"配售对象名称": only_b_objects}), use_container_width=True)

st.subheader("双方共同覆盖的年金计划")
st.dataframe(pd.DataFrame({"配售对象名称": both_objects}), use_container_width=True)

st.divider()

st.header("基础查询")

keyword = st.text_input("搜索配售对象 / 投资者 / 股票名称")

show_df = detail_df.copy()

if keyword:
    show_df = show_df[
        show_df.astype(str).apply(
            lambda row: row.str.contains(keyword, case=False, na=False).any(),
            axis=1
        )
    ]

st.metric("查询结果记录数", len(show_df))
st.dataframe(show_df, use_container_width=True)
