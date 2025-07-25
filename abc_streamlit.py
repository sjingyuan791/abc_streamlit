import streamlit as st
import pandas as pd

st.set_page_config(page_title="ABC分析付きCSV出力", layout="wide")
st.title("🔖 商品別ABC分析＋CSVダウンロードアプリ")

uploaded_file = st.file_uploader(
    "商品別売上CSVファイルをアップロード（product, sales列必須）", 
    type=["csv"]
)

if uploaded_file:
    df = pd.read_csv(uploaded_file, encoding="utf-8-sig")
    st.write("アップロードデータ（サンプル）")
    st.dataframe(df.head(10))

    if "product" not in df.columns or "sales" not in df.columns:
        st.error("CSVに 'product' および 'sales' 列が必要です。")
        st.stop()

    df["sales"] = pd.to_numeric(df["sales"], errors="coerce").fillna(0)
    sales_by_item = df.groupby("product")["sales"].sum().sort_values(ascending=False)
    cumsum_ratio = sales_by_item.cumsum() / sales_by_item.sum()
    abc_rank = pd.cut(cumsum_ratio, bins=[0, 0.8, 0.95, 1], labels=["A", "B", "C"])
    abc_df = sales_by_item.reset_index()
    abc_df["ABCランク"] = abc_rank.values
    df = df.merge(abc_df[["product", "ABCランク"]], on="product", how="left")

    st.markdown("#### 商品ランク分布")
    st.dataframe(abc_df.groupby("ABCランク")["product"].count().rename("商品数"))

    # ▼ ここを「cp932」に変更
    csv_str = df.to_csv(index=False, encoding="cp932")  
    st.download_button(
        label="📥 ABC分析済みCSVをダウンロード",
        data=csv_str,
        file_name="abc_analyzed.csv",
        mime="text/csv"
    )

    st.markdown("（A：売上上位80%、B：上位80-95%、C：残り）")
else:
    st.info("まずはCSVファイルをアップロードしてください。")
