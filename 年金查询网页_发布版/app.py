import streamlit as st
import pandas as pd
from pathlib import Path

st.set_page_config(page_title="年金打新分析", layout="wide")

st.title("2026年以来A股IPO网下配售年金计划分析平台")

BASE_DIR = Path(__file__).parent

detail_file = BASE_DIR / "2026年以来_补全A股_企业年金职业年金明细.xlsx"
summary_file = BASE_DIR / "2026年以来_补全A股_年金计划投资者汇总.xlsx"
performance_file = BASE_DIR / "股票上市表现.xlsx"

detail_df = pd.read_excel(detail_file).fillna("").astype(str)
summary_df = pd.read_excel(summary_file).fillna("").astype(str)

if performance_file.exists():
    performance_df = pd.read_excel(performance_file).fillna("").astype(str)
else:
    performance_df = pd.DataFrame()

investor_col = [c for c in detail_df.columns if "投资者名称" in c][0]
object_col = [c for c in detail_df.columns if "配售对象名称" in c][0]
stock_col = "股票名称"

if not performance_df.empty:
    detail_show_df = detail_df.merge(
        performance_df,
        on="股票名称",
        how="left"
    )
else:
    detail_show_df = detail_df.copy()

st.success("已加载：机构对比 + IPO上市当周收益分析")

st.sidebar.header("搜索筛选")

search_investor = st.sidebar.text_input("投资者名称", "")
search_object = st.sidebar.text_input("配售对象名称", "")
search_stock = st.sidebar.text_input("股票名称", "")
annuity_type = st.sidebar.selectbox("年金类型", ["全部", "企业年金", "职业年金"])
break_filter = st.sidebar.selectbox("是否破发", ["全部", "是", "否"])

filtered_df = detail_show_df.copy()

if search_investor:
    filtered_df = filtered_df[
        filtered_df[investor_col].str.contains(search_investor, case=False, na=False)
    ]

if search_object:
    filtered_df = filtered_df[
        filtered_df[object_col].str.contains(search_object, case=False, na=False)
    ]

if search_stock:
    filtered_df = filtered_df[
        filtered_df[stock_col].str.contains(search_stock, case=False, na=False)
    ]

if annuity_type != "全部":
    filtered_df = filtered_df[
        filtered_df[object_col].str.contains(annuity_type, na=False)
    ]

if break_filter != "全部" and "是否破发" in filtered_df.columns:
    filtered_df = filtered_df[
        filtered_df["是否破发"].astype(str) == break_filter
    ]

tab1, tab2, tab3 = st.tabs(["基础查询", "机构对比分析", "打新收益分析"])

with tab1:
    st.header("基础查询")

    c1, c2 = st.columns(2)
    c1.metric("筛选后明细记录数", len(filtered_df))
    c2.metric("汇总计划数量", len(summary_df))

    st.dataframe(filtered_df, use_container_width=True)

    st.download_button(
        "下载当前筛选结果",
        filtered_df.to_csv(index=False).encode("utf-8-sig"),
        "筛选结果.csv",
        "text/csv"
    )

with tab2:
    st.header("机构对比分析")

    col_a, col_b = st.columns(2)

    with col_a:
        org_a = st.text_input("机构A", "南方基金")

    with col_b:
        org_b = st.text_input("机构B", "易方达基金")

    a_df = detail_show_df[
        detail_show_df[investor_col].str.contains(org_a, case=False, na=False)
    ]

    b_df = detail_show_df[
        detail_show_df[investor_col].str.contains(org_b, case=False, na=False)
    ]

    a_stocks = set(a_df[stock_col])
    b_stocks = set(b_df[stock_col])

    only_a = sorted(a_stocks - b_stocks)
    only_b = sorted(b_stocks - a_stocks)
    both = sorted(a_stocks & b_stocks)

    c1, c2, c3 = st.columns(3)
    c1.metric(f"{org_a}获配股票数", len(a_stocks))
    c2.metric(f"{org_b}获配股票数", len(b_stocks))
    c3.metric("共同获配股票数", len(both))

    st.subheader(f"{org_a}有、{org_b}没有")
    st.dataframe(a_df[a_df[stock_col].isin(only_a)], use_container_width=True)

    st.subheader(f"{org_b}有、{org_a}没有")
    st.dataframe(b_df[b_df[stock_col].isin(only_b)], use_container_width=True)

    st.subheader("双方都有")
    both_df = detail_show_df[
        detail_show_df[stock_col].isin(both)
        & detail_show_df[investor_col].str.contains(f"{org_a}|{org_b}", case=False, na=False)
    ]
    st.dataframe(both_df, use_container_width=True)

with tab3:
    st.header("打新收益分析")

    if performance_df.empty:
        st.warning("还没有上传 股票上市表现.xlsx")
    else:
        st.subheader("股票上市当周表现")
        st.dataframe(performance_df, use_container_width=True)

        org = st.text_input("输入机构名称查看打新收益", "南方基金")

        org_df = detail_show_df[
            detail_show_df[investor_col].str.contains(org, case=False, na=False)
        ].copy()

        st.metric("该机构获配明细数", len(org_df))

        if "上市当周收益率" in org_df.columns:
            temp = org_df.copy()
            temp["上市当周收益率_num"] = pd.to_numeric(temp["上市当周收益率"], errors="coerce")
            avg_return = temp["上市当周收益率_num"].mean()
            st.metric("平均上市当周收益率", f"{avg_return:.2f}%" if pd.notna(avg_return) else "暂无")

        if "是否破发" in org_df.columns:
            broken = (org_df["是否破发"] == "是").sum()
            st.metric("破发记录数", int(broken))

        st.dataframe(org_df, use_container_width=True)
