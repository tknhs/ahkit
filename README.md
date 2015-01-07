# ahkit
Active History of Research for K.I.T.

## Requirements
- [Git](http://git-scm.com/)
- [Python 2.7](https://www.python.org/)
- [Firefox](https://www.mozilla.org/firefox/) or [Google Chrome](https://www.google.com/chrome/)

Recommended browser is Firefox. If you use Google Chrome, install [ChromeDriver](https://code.google.com/p/selenium/wiki/ChromeDriver).

## Installation
```
pip install git+https://github.com/tknhs/ahkit
```

## Usage
```
$ ahkit -h
Active History of Research for K.I.T.

usage:
    ahkit new_report [--date=yyyymmdd]
    ahkit deploy [--file=filename]
    ahkit -h | --help
    ahkit --version

options:
    -h, --help          ヘルプ表示
    --version           バージョン表示
    [--date=yyyymmdd]   yyyymmdd の週初から週末までのレポートファイル作成
                        デフォルト：現在の週初から週末までのレポートファイル作成
    [--file=filename]   指定したファイルに基づいて活動記録に登録する
                        デフォルト：コミットしていないすべてのファイル
```