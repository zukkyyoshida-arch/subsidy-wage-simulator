import streamlit as st
import pandas as pd
import numpy as np
import datetime

# Plotlyのインポートとフォールバック処理
try:
    import plotly.graph_objects as go
    import plotly.express as px
    HAS_PLOTLY = True
except ImportError:
    HAS_PLOTLY = False

# ==========================================================================
// 47都道府県 最低賃金データベース (令和6年度 / 2024年10月改定 最新データ)
# ==========================================================================
PREFECTURE_MIN_WAGES = {
    "北海道": 1010, "青森県": 953, "岩手県": 952, "宮城県": 973, "秋田県": 951,
    "山形県": 955, "福島県": 955, "茨城県": 1005, "栃木県": 1004, "群馬県": 985,
    "埼玉県": 1078, "千葉県": 1076, "東京都": 1163, "神奈川県": 1162, "新潟県": 985,
    "富山県": 998, "石川県": 998, "福井県": 984, "山梨県": 988, "長野県": 998,
    "岐阜県": 1001, "静岡県": 1034, "愛知県": 1077, "三重県": 1023, "滋賀県": 1017,
    "京都府": 1058, "大阪府": 1114, "兵庫県": 1052, "奈良県": 982, "和歌山県": 980,
    "鳥取県": 957, "島根県": 962, "岡山県": 982, "広島県": 1020, "山口県": 979,
    "徳島県": 980, "香川県": 970, "愛媛県": 956, "高知県": 952, "福岡県": 992,
    "佐賀県": 956, "長崎県": 953, "熊本県": 952, "大分県": 954, "宮崎県": 952,
    "鹿児島県": 953, "沖縄": 952
}

# ==========================================================================
# ページ設定 (リッチなワイドレイアウト & ダークモード親和性)
# ==========================================================================
st.set_page_config(
    page_title="デジタル化・AI導入補助金 賃上げ要件シミュレーター",
    page_icon="📈",
    layout="wide",
    initial_sidebar_state="expanded"
)

# カスタムCSSでUIデザインの更なるプレミアム化
st.markdown("""
<style>
    .reportview-container {
        background: #0f172a;
    }
    .metric-card {
        background: rgba(30, 41, 59, 0.5);
        border: 1px solid rgba(255, 255, 255, 0.05);
        border-radius: 12px;
        padding: 20px;
        text-align: center;
        box-shadow: 0 4px 15px rgba(0, 0, 0, 0.1);
    }
    .success-text {
        color: #10b981;
        font-weight: bold;
    }
    .fail-text {
        color: #ef4444;
        font-weight: bold;
    }
    .warning-text {
        color: #f59e0b;
        font-weight: bold;
    }
    .badge-info {
        background-color: rgba(99, 102, 241, 0.15);
        color: #818cf8;
        padding: 4px 10px;
        border-radius: 20px;
        font-size: 12px;
        font-weight: bold;
        border: 1px solid rgba(99, 102, 241, 0.3);
    }
    .badge-required {
        background-color: rgba(239, 68, 68, 0.15);
        color: #f87171;
        padding: 4px 10px;
        border-radius: 20px;
        font-size: 12px;
        font-weight: bold;
        border: 1px solid rgba(239, 68, 68, 0.3);
    }
</style>
""", unsafe_allow_html=True)

# ==========================================================================
# サイドバー設定エリア
# ==========================================================================
st.sidebar.image("https://img.icons8.com/nolan/96/trending-up.png", width=60)
st.sidebar.title("WageBoost Pro")
st.sidebar.caption("デジタル化・AI導入補助金 賃上げ判定")

st.sidebar.markdown("---")

st.sidebar.header("Step 1: 申請枠の設定")
subsidy_frame = st.sidebar.selectbox(
    "申請予定の枠",
    ["通常枠（補助額 150万円以上）※賃上げ必須", 
     "通常枠（補助額 150万円未満）※加点項目", 
     "特別枠（複数社連携・その他）※加点項目"]
)

is_past_recipient = st.sidebar.checkbox(
    "過去（2022〜2025年）に補助金交付を受けている",
    value=False,
    help="過去に交付を受けて再申請を行う場合、補助額に関わらず賃上げ計画の策定・表明が『必須』となります。"
)

# 必須要件かどうかのフラグ
is_required = ("150万円以上" in subsidy_frame) or is_past_recipient

if is_required:
    st.sidebar.markdown('<span class="badge-required">要件ステータス: 必須要件</span>', unsafe_allow_html=True)
    if is_past_recipient:
        st.sidebar.warning("⚠️ 過去の交付履歴があるため、金額に関わらず賃上げ計画が必須となります。")
else:
    st.sidebar.markdown('<span class="badge-info">要件ステータス: 加点要件</span>', unsafe_allow_html=True)

st.sidebar.markdown("---")

st.sidebar.header("Step 2: 事業場内最低賃金の確認")
prefecture = st.sidebar.selectbox(
    "事業所の所在地",
    list(PREFECTURE_MIN_WAGES.keys()),
    index=list(PREFECTURE_MIN_WAGES.keys()).index("東京都")
)

ref_min_wage = PREFECTURE_MIN_WAGES[prefecture]
st.sidebar.info(f"📍 {prefecture}の地域最低賃金: **{ref_min_wage}円** (令和6年度)")

target_level = st.sidebar.selectbox(
    "上乗せ目標",
    [30, 50],
    format_func=lambda x: f"地域最低賃金 ＋ {x}円以上"
)
target_min_wage = ref_min_wage + target_level

current_min_wage = st.sidebar.number_input(
    "自社の事業場内最低時給 (現在)",
    value=ref_min_wage + 10,
    min_value=500,
    max_value=5000,
    step=10,
    help="事業場内で最も低い時間給で働く従業員（パート・アルバイト含む）の時給を入力してください。"
)

# ==========================================================================
# メイン画面ダッシュボード
# ==========================================================================
st.title("📈 賃上げ要件シミュレーター & AI診断")
st.write("事業計画期間（3年）における給与支給総額および最低賃金のクリア状況を瞬時に判定し、コンサルティング提案資料を自動作成します。")

col_inputs, col_results = st.columns([1.1, 0.9])

with col_inputs:
    st.subheader("📝 給与・人員計画 (3年事業計画)")
    
    # 基準年度の入力
    st.markdown("##### 基準年度 (現在) の数値入力")
    c1, c2 = st.columns(2)
    with c1:
        base_employees = st.number_input("被保険者数 (基準年度)", value=10, min_value=1, max_value=1000)
    with c2:
        base_salary = st.number_input("給与支給総額 (基準年度)", value=36000000, min_value=100000, step=500000)
        st.caption(f"現在の総額: **{base_salary // 10000:,.0f}万円**")
        
    st.markdown("##### 各計画年度の計画値")
    st.write("ダブルクリックして各セルの数値を直接編集し、計画を変更できます。")

    # 初期データの作成
    init_df = pd.DataFrame({
        "年度": ["1年後", "2年後", "3年後 (目標年)"],
        "被保険者数": [base_employees, base_employees + 1, base_employees + 1],
        "給与支給総額 (円)": [
            int(base_salary * 1.015),
            int(base_salary * 1.03),
            int(base_salary * 1.045)
        ]
    })

    # インタラクティブデータエディタ
    edited_df = st.data_editor(
        init_df,
        num_rows="fixed",
        use_container_width=True,
        column_config={
            "年度": st.column_config.TextColumn("年度", disabled=True),
            "被保険者数": st.column_config.NumberColumn("被保険者数 (名)", min_value=1, max_value=1000, step=1),
            "給与支給総額 (円)": st.column_config.NumberColumn("給与支給総額 (円)", min_value=100000, step=100000, format="%d")
        }
    )

    # 1人当たり平均給与の計算と反映
    plan_data = []
    st.markdown("##### 計画データ詳細 (自動計算)")
    
    details = []
    for idx, row in edited_df.iterrows():
        yr = row["年度"]
        emp = int(row["被保険者数"])
        sal = int(row["給与支給総額 (円)"])
        avg_sal = sal // emp
        details.append({
            "年度": yr,
            "被保険者数": f"{emp} 名",
            "給与支給総額": f"{sal // 10000:,.0f}万円",
            "1人当たり平均": f"{avg_sal:,.0f}円/人"
        })
        plan_data.append({"year": idx + 1, "employees": emp, "salary": sal, "avg": avg_sal})
        
    st.table(pd.DataFrame(details))

# ---- 計算と判定 ----
year3_salary = plan_data[2]["salary"]
year3_employees = plan_data[2]["employees"]
year3_avg = plan_data[2]["avg"]

# 1. CAGR計算
cagr = 0.0
if base_salary > 0 and year3_salary > 0:
    cagr = (year3_salary / base_salary) ** (1/3) - 1
cagr_pct = cagr * 100

is_cagr_pass = cagr_pct >= 1.5

# 2. 最低賃金判定
is_min_wage_pass = current_min_wage >= target_min_wage

# 3. 総合判定
if is_min_wage_pass and is_cagr_pass:
    overall_status = "PASS"
    status_color = "success-text"
    status_label = "要件達成（適格）" if is_required else "加点要件達成"
elif not is_required and (is_min_wage_pass or is_cagr_pass):
    overall_status = "WARNING"
    status_color = "warning-text"
    status_label = "一部達成（加点弱）"
else:
    overall_status = "FAIL"
    status_color = "fail-text"
    status_label = "要件未達（不適格）" if is_required else "加点対象外"

# 結果カラムの表示
with col_results:
    st.subheader("📊 診断結果")
    
    # 総合判定巨大バッジ
    st.markdown(f"""
    <div style="background: rgba(30, 41, 59, 0.4); border-radius: 16px; border: 2px solid rgba(255,255,255,0.05); padding: 25px; text-align: center; margin-bottom: 25px;">
        <span style="font-size: 13px; color: #9ca3af; text-transform: uppercase; letter-spacing: 2px;">総合判定</span>
        <h1 class="{status_color}" style="font-size: 40px; margin: 10px 0; font-weight: 800;">{status_label}</h1>
        <p style="font-size: 14px; margin-bottom: 0; color: #e2e8f0;">
            {'通常枠等の必須条件を満たしています。' if overall_status == 'PASS' else '計画の調整、または時給の引き上げが必要です。'}
        </p>
    </div>
    """, unsafe_allow_html=True)
    
    # メトリクスグリッド
    m_col1, m_col2 = st.columns(2)
    
    with m_col1:
        cagr_status_str = "✅ 達成" if is_cagr_pass else "❌ 未達"
        st.markdown(f"""
        <div class="metric-card">
            <span style="font-size:12px; color:#9ca3af;">支給総額CAGR (年平均)</span>
            <h2 style="font-family:'Outfit'; font-size:26px; margin: 5px 0;">{cagr_pct:.2f}%</h2>
            <span class="{'success-text' if is_cagr_pass else 'fail-text'}" style="font-size:12px;">{cagr_status_str} (目標1.5%以上)</span>
        </div>
        """, unsafe_allow_html=True)
        
    with m_col2:
        wage_status_str = "✅ 達成" if is_min_wage_pass else "❌ 未達"
        st.markdown(f"""
        <div class="metric-card">
            <span style="font-size:12px; color:#9ca3af;">事業場内最低賃金</span>
            <h2 style="font-family:'Outfit'; font-size:26px; margin: 5px 0;">{current_min_wage}円</h2>
            <span class="{'success-text' if is_min_wage_pass else 'fail-text'}" style="font-size:12px;">{wage_status_str} (目標{target_min_wage}円)</span>
        </div>
        """, unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)

    # 4. 可視化グラフ
    st.markdown("##### 📈 計画推移と目標の対比")
    
    # グラフデータ構築
    years_labels = ["基準年度", "1年後", "2年後", "3年後"]
    actual_salaries = [base_salary, plan_data[0]["salary"], plan_data[1]["salary"], plan_data[2]["salary"]]
    target_salaries = [
        base_salary,
        int(base_salary * (1.015**1)),
        int(base_salary * (1.015**2)),
        int(base_salary * (1.015**3))
    ]
    
    if HAS_PLOTLY:
        fig = go.Figure()
        
        # 計画値ライン
        fig.add_trace(go.Scatter(
            x=years_labels, 
            y=actual_salaries,
            mode='lines+markers',
            name='計画給与支給総額',
            line=dict(color='#6366f1', width=4),
            marker=dict(size=8, color='#6366f1'),
            hovertemplate='計画額: %{y:,.0f}円<extra></extra>'
        ))
        
        # 目標値ライン
        fig.add_trace(go.Scatter(
            x=years_labels, 
            y=target_salaries,
            mode='lines',
            name='要件目標 (年1.5%増)',
            line=dict(color='#10b981', width=2, dash='dash'),
            hovertemplate='目標額: %{y:,.0f}円<extra></extra>'
        ))
        
        fig.update_layout(
            paper_bgcolor='rgba(0,0,0,0)',
            plot_bgcolor='rgba(0,0,0,0)',
            margin=dict(l=0, r=0, t=10, b=0),
            height=260,
            legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1, font=dict(color='#9ca3af', size=10)),
            xaxis=dict(gridcolor='rgba(255,255,255,0.05)', tickfont=dict(color='#9ca3af')),
            yaxis=dict(gridcolor='rgba(255,255,255,0.05)', tickfont=dict(color='#9ca3af'))
        )
        st.plotly_chart(fig, use_container_width=True, config={'displayModeBar': False})
    else:
        # Altair/Streamlit標準のフォールバック
        chart_df = pd.DataFrame({
            "年度": years_labels,
            "計画給与支給総額": actual_salaries,
            "目標ライン": target_salaries
        }).set_index("年度")
        st.line_chart(chart_df)

# ==========================================================================
// 💡 AI分析 & コンサルタント提案レポートの生成
# ==========================================================================
st.markdown("---")
st.header("🧠 コンサルタントAI分析 & アクションプラン")

advice_html = ""

if is_min_wage_pass and is_cagr_pass:
    st.success("🎉 **おめでとうございます！すべての要件を完璧にクリアしています。**")
    advice_html += f"""
    *   **現在の診断結果**: 非常に安定して実効性の高い計画が立てられています。このまま補助金交付申請の手続きに進んでください。
    *   **🔑 超重要アクション - 従業員への表明義務**: 
        *   補助金の申請を正式に提出（交付申請）する前に、必ず本賃上げ計画を**全従業員に表明（文書、口頭、または掲示板への掲載等）**してください。
        *   表明を行った事実を客観的に証明するため、「表明した日付、方法、対象者、説明内容」を記載した**表明書面（または説明会写真、従業員の署名・受領簿など）**を作成し、手元に大切に保管してください。
    *   **📊 実績報告のクリアに向けて**:
        *   3年目の事業終了時（実績報告時）に本要件（CAGR 1.5%）を下回っていると、返還ペナルティ等の対象となります。ITツール導入による「業務効率化」と「売上増加」を確実に進め、給与総額を健全に引き上げられる事業基盤を作りましょう。
    """
else:
    st.warning("⚠️ **計画のクリアに向けて、以下の修正・調整を提案します。**")
    
    col_adv1, col_adv2 = st.columns(2)
    
    with col_adv1:
        st.markdown("##### 📍 最低賃金に関する改善策")
        if is_min_wage_pass:
            st.write("✅ **最低賃金要件はすでにクリアしています。** 現在の最低時給水準を維持・引き上げて計画を運用してください。")
        else:
            shortage = target_min_wage - current_min_wage
            st.error(f"❌ **事業場内最低賃金が不足しています (不足: {shortage}円)**")
            st.write(f"""
            *   現在の事業場内最低時給である **{current_min_wage}円** は、{prefecture}の地域最低賃金（{ref_min_wage}円）に目標の{raiseLevel}円を上乗せした **{target_min_wage}円** に達していません。
            *   👉 **具体的な改善プラン**: 事業場内で最も時間給の低い労働者（パート・アルバイト含む）全員の時給を、計画初年度の運用開始日までに一律 **{target_min_wage}円以上** に引き上げるよう、サイドバーの「自社の事業場内最低時給」を修正してください。
            """)
            
    with col_adv2:
        st.markdown("##### 📈 給与総額CAGRに関する改善策")
        if is_cagr_pass:
            st.write("✅ **給与総額増加率はクリアしています (現在: {:.2f}%)**".format(cagr_pct))
        else:
            req_year3_salary = int(base_salary * (1.015**3))
            deficit = req_year3_salary - year3_salary
            st.error(f"❌ **支給総額CAGRが不足しています (現在: {cagr_pct:.2f}% / 不足額: {deficit:,.0f}円)**")
            st.write(f"""
            年率平均 1.5% 以上の増加をクリアするためには、3年目の給与支給総額を最低でも **{req_year3_salary // 10000:,.0f}万円** ({req_year3_salary:,.0f}円) に引き上げる必要があります。
            
            🧠 **ずっきー参謀による2つのアプローチ案**:
            *   **【案A】1人当たりの給与ベースアップ (人数は維持)**
                *   3年目の被保険者数 **{year3_employees}名** を変更せず、昇給や賞与を調整します。
                *   → 3年目の1人当たり年間給与を平均 **{req_year3_salary // year3_employees:,.0f}円** (現在計画から約 **{(req_year3_salary - year3_salary) // year3_employees:,.0f}円/人** 引き上げる)。
            *   **【案B】採用計画の強化 (給与水準は維持)**
                *   1人当たりの給料は変えずに、採用人数を増やして総支給額を増やします。
                *   → 3年目の被保険者数を現在の計画からさらに **{int(np.ceil(req_year3_salary / (year3_salary / year3_employees))) - year3_employees}名** 追加採用し、総員を増やします。
            """)

st.markdown(advice_html)

# ==========================================================================
# 提案書レポート印刷・出力用セクション
# ==========================================================================
st.markdown("---")
st.subheader("🖨️ レポート作成 / 印刷用プレビュー")
st.write("ブラウザの印刷機能（Ctrl+P / Cmd+P）を使って、このページをそのままA4報告書としてPDF保存または印刷できます。")

# プレビュー用のシンプルなサマリー表
report_date = datetime.date.today().strftime("%Y年%m月%d日")
report_df = pd.DataFrame([
    ["作成日", report_date],
    ["対象事業所所在地", f"{prefecture} (最低賃金 {ref_min_wage}円)"],
    ["申請予定枠", subsidy_frame],
    ["要件区分", "必須要件 (返還リスク有)" if is_required else "加点要件 (ペナルティ有)"],
    ["事業場内最低時給 (現在)", f"{current_min_wage}円 (目標: {target_min_wage}円) -> {'適合' if is_min_wage_pass else '不適合'}"],
    ["給与支給総額CAGR (年平均)", f"{cagr_pct:.2f}% (目標: 1.50%以上) -> {'適合' if is_cagr_pass else '不適合'}"],
    ["総合判定ステータス", status_label]
], columns=["項目", "内容"])

st.table(report_df)

st.caption("※本報告書は最新の公募要領に基づいてシミュレーションされたものです。最終的な申請内容については、必ず公募要領を確認の上、専門家またはIT導入支援事業者とご相談ください。")
