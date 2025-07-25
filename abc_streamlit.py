import streamlit as st
import pandas as pd

st.set_page_config(page_title="ABC分析付きCSV出力", layout="wide")
st.title("🔖 商品別ABC分析＋CSVダウンロードアプリ")

uploaded_file = st.file_uploader(
    "商品別売上CSVファイルをアップロード（product, sales列必須）", 
    type=["csv"]
)

if uploaded_file:
    # データ読込
    df = pd.read_csv(uploaded_file, encoding="utf-8-sig")
    st.write("アップロードデータ（サンプル）")
    st.dataframe(df.head(10))

    # --- 必須列チェック ---
    if "product" not in df.columns or "sales" not in df.columns:
        st.error("CSVに 'product' および 'sales' 列が必要です。")
        st.stop()

    # sales型変換・欠損は0
    df["sales"] = pd.to_numeric(df["sales"], errors="coerce").fillna(0)
    # product名欠損は削除
    df = df.dropna(subset=["product"])

    # --- 商品ごと累計売上・ABC分析 ---
    sales_by_item = df.groupby("product")["sales"].sum().sort_values(ascending=False)
    cumsum_ratio = sales_by_item.cumsum() / sales_by_item.sum()
    abc_rank = pd.cut(cumsum_ratio, bins=[0, 0.8, 0.95, 1.0], labels=["A", "B", "C"], include_lowest=True)
    abc_df = sales_by_item.reset_index()
    abc_df["ABCランク"] = abc_rank.values

    # 元データにABCランクを付与
    df = df.merge(abc_df[["product", "ABCランク"]], on="product", how="left")

    # --- ABC別集計サマリも表示 ---
    st.markdown("#### 商品ランク分布")
    st.dataframe(abc_df.groupby("ABCランク")["product"].count().rename("商品数"))

    # --- ABC分析済みCSVのダウンロードボタン（Shift-JIS対応）---
    csv_sjis = df.to_csv(index=False, encoding="cp932")  # ←Excelに強いShift-JIS
    st.download_button(
        label="📥 ABC分析済みCSVをダウンロード（Excel用）",
        data=csv_sjis,
        file_name="abc_analyzed.csv",
        mime="text/csv"
    )

    # --- Aランクのみ抽出＆ダウンロードボタン ---
    df_A = df[df["ABCランク"] == "A"]
    if not df_A.empty:
        a_csv_sjis = df_A.to_csv(index=False, encoding="cp932")
        st.download_button(
            label="⭐ Aランク商品のみCSVをダウンロード（Excel用）",
            data=a_csv_sjis,
            file_name="abc_rank_A_only.csv",
            mime="text/csv"
        )
    else:
        st.info("Aランク商品がありません。")

    st.markdown("（A：売上上位80%、B：上位80-95%、C：残り）")
else:
    st.info("まずはCSVファイルをアップロードしてください。")
