import os
import streamlit as st
import google.generativeai as genai
from PIL import Image

# 画面タイトルと設定
st.set_page_config(page_title="ボタニカルナビ - 観葉植物＆実生診断", page_icon="🌱")

# ヘッダー・フッター非表示CSS
hide_style = """
    <style>
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}
    .stAppHeader {display: none;}
    .stAppViewerBadge {display: none !important;}
    [data-testid="stStatusWidget"] {display: none !important;}
    div[class*="viewerBadge"] {display: none !important;}
    a[href*="streamlit.io"] {display: none !important;}
    div[data-testid="stToolbar"] {display: none !important;}
    div[data-testid="stDecoration"] {display: none !important;}
    </style>
"""
st.markdown(hide_style, unsafe_allow_html=True)

st.title("🌱 観葉植物＆実生（種から育成）ナビ")
st.caption("名前の特定から、種の発芽・葉のトラブル診断までAIが完全サポート！")

# モード選択
mode = st.radio(
    "診断・相談モードを選んでください",
    ["🌿 成株（苗・鉢植え）の育て方・トラブル診断", "🌱 種まき・発芽（実生）サポート"],
    horizontal=True
)

# 写真アップロード
st.subheader("📷 写真を撮る・えらぶ")
uploaded_file = st.file_uploader(
    "植物、葉っぱの異変、種、新芽などの写真を読み込めます", 
    type=["jpg", "jpeg", "png"]
)

image = None
if uploaded_file is not None:
    image = Image.open(uploaded_file)
    st.image(image, caption="読み込んだ写真", use_container_width=True)

# テキスト入力欄
plant_name = st.text_input("植物の名前（分かれば入力、不明なら空欄でOK）", placeholder="例：パキラ、アガベ、不明など")
problem_text = st.text_area(
    "状態や気になること・質問メモ", 
    placeholder="例：葉っぱが黄色くなってきた、種まきして1週間経つけど発芽しない、腰水のタイミングなど"
)

# 実行ボタン
if st.button("AIプロ診断を受ける", type="primary"):
    if uploaded_file is None and not plant_name and not problem_text:
        st.warning("写真をアップロードするか、植物の名前・質問を入力してください！")
    else:
        api_key = os.environ.get("GEMINI_API_KEY")
        if not api_key and hasattr(st, "secrets"):
            api_key = st.secrets.get("GEMINI_API_KEY", None)
        
        if not api_key:
            st.error("APIキーが設定されていません。")
        else:
            try:
                genai.configure(api_key=api_key)
                model = genai.GenerativeModel("gemini-3.5-flash")

                if "種まき" in mode:
                    prompt = f"""
あなたは観葉植物・多肉植物・塊根植物の「実生（種からの育成）」に詳しいプロのボタニカルアドバイザーです。
以下の情報（写真・植物名・質問）から、種まき〜発芽〜幼苗管理のアドバイスを行ってください。

【植物名】{plant_name if plant_name else "写真から判別（不明な場合は推定）"}
【質問・状態】{problem_text if problem_text else "特になし（画像や一般的な種まき管理を解説）"}

【出力フォーマット】
1. **植物名・タイプ判定**（写真や入力から特定。実生難易度も添える）
2. **種まき・発芽のポイント**（適温、休眠打破・浸水が必要か、腰水の有無など）
3. **現在の状態・診断**（写真がある場合：発芽成功／徒長気味／カビ懸念など）
4. **今すぐやるべきアクション**（水やり・光・風の具体的な指示）
"""
                else:
                    prompt = f"""
あなたは観葉植物のプロのボタニカルアドバイザーです。
以下の情報（写真・植物名・質問）から、植物の種類特定および育て方・トラブル診断を行ってください。

【植物名】{plant_name if plant_name else "写真から判別（不明な場合は推定）"}
【質問・状態】{problem_text if problem_text else "特になし（画像の状態を診断）"}

【出力フォーマット】
1. **植物の名前＆タイプ判定**（写真から判定。乾燥好き／湿気好きなど）
2. **現在の状態診断**（元気／水不足／根腐れ気味／日照不足／害虫など）
3. **育て方の基本**（☀️日当たり・置き場所 / 💧水やり・葉水 / 🪴土・肥料）
4. **今すぐやるべき救急アクション**（具体的な処置）
"""

                contents = [prompt]
                if image is not None:
                    contents.append(image)

                with st.spinner("植物の状態を診断中...🌱"):
                    response = model.generate_content(contents)
                    st.success("診断完了！")
                    st.markdown(response.text)

            except Exception as e:
                st.error(f"エラーが発生しました: {e}")
