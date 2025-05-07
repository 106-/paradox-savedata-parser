# [WIP]Paradox Save Data Parser

高速なParadoxゲーム（Crusader Kings、Europa Universalis、Hearts of Iron、Stellarisなど）のセーブデータパーサーです。

Vibe Codingにより生まれた産物なのでまだ動かないことがあります。

## 特徴

- Rustで実装された高速なパーサー
- Pythonからのシンプルなインターフェース
- 大容量のセーブファイル（数百MB）も効率的に処理
- Pythonオブジェクト同様のアクセス（ドット記法）
- セーブデータの編集と保存機能

## インストール

### 必要条件

- Python 3.7以上
- Rust（cargo）

```bash
pip install paradox-savedata-parser
```

## 使い方

### 読み込みと参照

```python
from paradox_savedata.parser import parse_save_file

# セーブファイルを解析
save_data = parse_save_file("path/to/save.ck3")

# 属性アクセス（ドット記法）でデータにアクセス
country = save_data.country
ruler_name = save_data.country.ruler.name
print(f"支配者の名前: {ruler_name}")

# 辞書形式でのアクセスも可能
player_id = save_data["player"]["id"]
character = save_data["character"][player_id]
print(f"キャラクター名: {character.name}")  # 混合アクセスも可能

# json.dumpなどでシリアライズ可能
import json
with open("save_data.json", "w") as f:
    json.dump(save_data.data, f, indent=2)
```

### 編集と保存

```python
from paradox_savedata.parser import parse_save_file, save_to_file

# セーブファイルを解析
save_data = parse_save_file("path/to/save.eu4")

# データを編集
# 属性アクセスで変更
save_data.countries.FRA.treasury = 1000.0

# 辞書アクセスで変更
save_data["countries"]["ENG"]["monarch"]["adm"] = 6

# 変更を保存
save_to_file(save_data, "path/to/modified_save.eu4")
```

## 例

- `examples/simple_example.py`: 基本的な読み込みと表示の例
- `examples/edit_example.py`: データの編集と保存の例

## パフォーマンス

RustのNOMパーサーコンビネータライブラリを使用して実装されているため、数百MBのセーブファイルでも高速に処理できます。

## ライセンス

MIT