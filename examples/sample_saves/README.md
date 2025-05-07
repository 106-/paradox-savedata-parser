# サンプルセーブファイル

このディレクトリには、テスト用の小さなサンプルセーブファイルを配置します。
実際のゲームのセーブファイルは数百MBになることがあるため、Git管理には適していません。

## サンプルファイル

- `sample.ck3` - Crusader Kings 3のサンプル
- `sample.eu4` - Europa Universalis IVのサンプル
- `sample.hoi4` - Hearts of Iron IVのサンプル
- `sample.sav` - Stellarisのサンプル

## 使用方法

```python
from paradox_savedata.parser import parse_save_file
import os

# サンプルファイルのパスを取得
script_dir = os.path.dirname(os.path.abspath(__file__))
sample_path = os.path.join(script_dir, "sample.hoi4")

# サンプルセーブデータを解析
save_data = parse_save_file(sample_path)
```

## 注意事項

実際のゲームセーブファイルを追加する場合は、`.gitignore`に追加されていることを確認してください。
大容量ファイルの追加はリポジトリのサイズを肥大化させる可能性があります。