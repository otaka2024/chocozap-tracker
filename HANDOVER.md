# ChocoLog — Claude Code 引き継ぎドキュメント

## プロジェクト概要

チョコザップ広島安佐南区八木店向けのトレーニング記録PWAアプリ。
単一HTMLファイル構成。GitHubにホストしてGitHub Pagesで公開済み。

**公開URL:** https://otaka2024.github.io/chocozap-tracker/
**リポジトリ:** https://github.com/otaka2024/chocozap-tracker

---

## ファイル構成

```
chocozap-tracker/
├── index.html          # アプリ本体（全機能。約1400行）
├── manifest.json       # PWA設定
├── sw.js               # Service Worker（オフライン対応）
├── icons/
│   ├── icon-192.png    # アプリアイコン
│   └── icon-512.png
├── .github/workflows/
│   └── deploy.yml      # mainブランチpush→GitHub Pages自動デプロイ
├── HANDOVER.md         # このファイル
└── README.md
```

---

## 現在のバージョン: v1.1.5

### バージョン管理ルール

`index.html` の先頭付近にある定数を変更するだけで全体に反映される：

```javascript
const APP_VER = '1.1.5';  // ← ここを変える
```

これにより以下が自動で変わる：
- ヘッダー右上のバージョン表示
- localStorage キー（`czlogs_1.1.5` / `czlast_1.1.5`）
- CSV出力ファイル名（`chocozap_v1.1.5_日時.csv`）

`sw.js` の CACHE_NAME も合わせて変更すること：
```javascript
const CACHE_NAME = 'chocolog-v1.1.5';  // ← APP_VERに合わせる
```

---

## アプリの機能

### タブ構成（BottomNav 4タブ）
1. **記録** — マシン選択→重量/負荷→回数/時間→セット→確認→記録
2. **履歴** — 日付別ログ一覧（新しい順）、削除ボタンあり
3. **カレンダー** — 月表示、記録日を緑でハイライト、月の使用日数表示、タップで詳細ポップアップ
4. **CSV出力** — 期間指定してダウンロード、UTF-8 BOM付き

### 記録フロー（重要）

```
マシン選択
  ├─ 前回値あり（フル） → 確認画面に直行
  └─ 前回値なし
       ├─ weight系: STEP1(重量) → STEP2(回数) → STEP3(セット) → 確認
       ├─ cardio系: STEP1(負荷1〜30) → STEP2(時間) → STEP3(セット) → 確認
       └─ abslevel系: STEP1(負荷低中高) → STEP2(回数) → STEP3(セット) → 確認
```

**確認画面での修正：**
各行の ✎ ボタンをタップ → 確認画面内にSTEPグリッドUIが展開 → 選択で即反映

### マシン一覧・カラー

| マシン | type | 重量/負荷 | color |
|--------|------|-----------|-------|
| レッグプレス | weight | 5〜100kg | purple |
| アダクション | weight | 5〜80kg | pink |
| アブダクション | weight | 5〜80kg | coral |
| アブベンチ | abslevel | 低/中/高 | teal |
| チェストプレス | weight | 5〜80kg | blue |
| ラットプルダウン | weight | 5〜60kg | cyan |
| ショルダープレス | weight | 5〜50kg | amber |
| バイセップスカール | weight | 5〜40kg | red |
| ランニングマシン | cardio | 5〜30（6段階） | green |
| エクササイズバイク | cardio | 5〜30（6段階） | lime |

### データ構造（localStorage）

```javascript
// ログデータ
czlogs_1.1.5 = [
  {
    id: 1234567890,        // Date.now()
    date: "2025-05-03",
    time: "10:30",
    machine: "leg",        // マシンID
    machineName: "レッグプレス",
    machineIcon: "🦵",
    type: "weight",        // weight / cardio / abslevel
    load: 60,              // 重量(kg) / 負荷(数値) / 負荷(低中高)
    reps: 12,              // 回数 / 時間(分)
    sets: 3
  }
]

// 前回選択値（マシンごと）
czlast_1.1.5 = {
  "leg": { load: 60, reps: 12, sets: 3 },
  "run": { load: 15, reps: 20, sets: 1 },
  ...
}
```

---

## 未完了の作業（このチャットで途中だったもの）

### ⚠️ v1.1.5 の確認画面が未完成

`index.html` の確認画面（`showConfirm` / `renderConfirmCard` / `cfOpenEdit`）を
「✎タップで確認画面内にSTEPグリッドを展開する」方式に書き換えた途中。

**プレビューウィジェットの描画が途中で途切れたため、実際のindex.htmlに
この変更が正しく反映されているか未検証。**

→ **まず動作確認から始めてください：**
```bash
# ローカルで確認
cd chocozap-tracker
python3 -m http.server 8080
# ブラウザで http://localhost:8080 を開く
```

確認すべき点：
1. マシン選択 → 確認画面への遷移
2. 確認画面で ✎ をタップ → グリッドが展開されるか
3. 初回（前回値なし）の STEP1→2→3→確認 フロー
4. 記録後に前回値が保持されるか

---

## CSS変数（テーマ）

```css
:root {
  --bg: #0f172a;          /* 背景 */
  --surface: #1e293b;     /* カード背景 */
  --surface2: #273344;    /* 入力欄・グリッドボタン */
  --accent: #22d3ee;      /* シアン（メインアクセント） */
  --text: #f1f5f9;
  --text2: #94a3b8;
  --text3: #64748b;
  --radius: 14px;

  /* マシンカラー（10色） */
  --mc-purple / --mc-pink / --mc-coral / --mc-teal / --mc-blue
  --mc-cyan / --mc-amber / --mc-red / --mc-green / --mc-lime
  /* 各色に -bd（ボーダー）と -tx（テキスト）バリアントあり */
}
```

---

## デプロイ方法

mainブランチにpushするだけで自動デプロイ（GitHub Actions）：

```bash
git add .
git commit -m "feat: 変更内容"
git push origin main
# 1〜2分後に https://otaka2024.github.io/chocozap-tracker/ に反映
```

---

## 今後やりたいこと（ユーザーから出た要望メモ）

特になし（このセッションでの未完了作業のみ）
