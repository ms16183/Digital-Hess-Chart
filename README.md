# Digital Hess Chart

## 概要
- デジタルHessチャートはPCとマウスによってHess赤緑試験を行うことができる．
- 次の方法で座標値を比較する．
  1. 固定点の角度を入力→Matplotlib上の座標に変換
  1. クリックされたグラフ上の位置を取得→Matplotlib上の座標に変換
  1. 座標値の差を比較する．
- ユーザによる事前設定が必要な値は次の通りである．
  - モニターのインチ数
  - Hessチャートのサイズ

## インストール
python 3.8以降を想定している．
主に`PySimpleGUI`と`Matplotlib`が必要になる．

```
git clone https://github.com/ms16183/Digital-Hess-Chart
cd Digital-Hess-Chart
pip3 install -r requirements.txt
```

## 実行方法

```
python3 main.py
```