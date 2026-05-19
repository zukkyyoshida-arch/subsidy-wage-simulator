# 📈 デジタル化・AI導入補助金 賃上げ要件シミュレーター (Streamlit版)

IT導入補助金（デジタル化・AI導入補助金）の難所である**「賃上げ要件」**のクリア判定を一瞬で診断し、要件達成に向けた具体的な昇給・採用アクションプランを自動生成するプレミアムなWebアプリケーションです。

---

## ✨ 主な機能

1. **47都道府県 最低賃金データベース内蔵**: 令和6年度改定（最新）の最低賃金データを自動参照し、目標値（最低賃金+30円または50円）をクリアしているか自動判定。
2. **給与総額CAGR (年平均成長率) 計算**: 3年計画の給与総額と従業員数からCAGRを自動計算し、1.5%基準を満たしているか判定。
3. **インタラクティブ・チャート (Plotly)**: 計画の推移と、要件をクリアする目標ラインの対比を美しいグラフィックスで可視化。
4. **AIコンサルタントによる改善提案**: 未達成時、「ベースアップ（案A）」「採用人数追加（案B）」の具体的なリカバリー数値を自動算出。
5. **A4レポート出力**: ブラウザの印刷機能（Cmd+P / Ctrl+P）でそのまま美しいA4報告書としてPDF化・印刷可能。

---

## 🛠️ ローカルでの起動方法

このリポジトリをお手元のPC（Mac/Windows）で起動する方法です。

### 1. 必要なライブラリのインストール
ターミナルを起動し、このフォルダに移動して以下のコマンドを実行します。
```bash
pip3 install -r requirements.txt
```

### 2. アプリケーションの起動
以下のコマンドでブラウザが自動的に立ち上がり、シミュレーターが起動します。
```bash
streamlit run app.py
```

---

## 🚀 GitHubへの登録とStreamlit Cloudへのデプロイ手順

このシミュレーターをGitHubに登録し、インターネット上に**無料公開（デプロイ）**して誰でもアクセスできるようにする手順です。

### STEP 1: Gitリポジトリの初期化とコミット
ターミナルでこのフォルダを開き、以下のコマンドを順番に実行します。

```bash
# 1. Gitの初期化
git init

# 2. ファイルをすべてステージング
git add .

# 3. 初回コミット
git commit -m "Initial commit: Streamlit Subsidy Wage Simulator"
```

### STEP 2: GitHubに新しいリポジトリを作成
1. [GitHub](https://github.com/) にログインします。
2. 画面右上の「＋」アイコンから **「New repository」** を選択します。
3. リポジトリ名（例：`subsidy-wage-simulator`）を入力します。
   * **Public** (公開) または **Private** (非公開) を選択します。
   * 「Initialize repository with...」のチェックボックスはすべて**オフ**のままにします。
4. **「Create repository」** ボタンを押します。
5. 作成後に表示される画面から、以下のようなコマンド（特に `remote add` の行）をターミナルにコピーして実行します。

```bash
git branch -M main
git remote add origin https://github.com/【あなたのアカウント名】/【リポジトリ名】.git
git push -u origin main
```

これで、GitHubへの移設（アップロード）は完了です！

### STEP 3: Streamlit Community Cloudで無料デプロイ
1. [Streamlit Community Cloud](https://share.streamlit.io/) にアクセスし、アカウントをお持ちでない場合はGitHubアカウントでサインアップします。
2. ログイン後、画面右上の **「New app」** ボタンを押します。
3. 以下の項目を設定します：
   * **Repository**: 先ほど作成したGitHubリポジトリ（例：`【アカウント名】/subsidy-wage-simulator`）
   * **Branch**: `main`
   * **Main file path**: `app.py`
4. **「Deploy!」** ボタンを押します。

**数分でデプロイが完了し、公開URLが発行されます！** 
発行されたURLをクライアントやチームに共有すれば、誰でもスマホやPCからこのシミュレーターを動かすことができるようになります。
