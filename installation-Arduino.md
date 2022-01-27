# Firmware Installation

## Preliminary Arrangements

M5Cameraのファームウェアを書き込むためには、[Arduino IDE](https://www.arduino.cc/en/Main/Software) ver.1.8.0以降を推奨します。
事前にダウンロード，およびインストールをお願いいたします。

## Setting the Arduino IDE

1. 「ファイル」→「環境設定」
2. 追加のボードマネージャーのURL　の右のボタン
3. URLの入力: https://dl.espressif.com/dl/package_esp32_index.json
4. Arduino再起動

## Install board

1. 「ツール」→「ボード…」→「ボードマネージャ…」
2. ボードマネージャで「esp32」と入力
3. esp32 をインストール
4. Arduino再起動

## Board select

1. 「ツール」→「ボード…」→ 「ESP32 Wrover Module」
2. 「ツール」→「シリアルポート」→　選択  (ポート名はユーザの環境ごとに異なります。)

## Installation Procedure

- `/m5camera-detect`
    - `m5camera-detect.ino`

1. “m5camera-detect.ino”をArduino IDEから開きます。
1. SSID,Paswordの変更
    お使いのWifiルーターのSSIDとPasswordに変更してください。
    ```
    const char* ssid = "SSID";
    const char* password = "PASSWORD";
    ```
2. M5CameraをUSBTypeCケーブルでパソコンに接続
3. アップロードボタン[→]をクリックします。