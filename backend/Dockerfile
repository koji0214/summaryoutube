# Pythonの公式イメージをベースにする
FROM python:3.12-slim

# ghcr.ioからuvの最新バイナリを一時的なステージとしてコピー
COPY --from=ghcr.io/astral-sh/uv:latest /uv /bin/uv

COPY . /app
# 作業ディレクトリを設定
WORKDIR /app

# 依存関係ファイルをコピーしてインストール
RUN uv sync

# FastAPIサーバーを起動
CMD ["/bin/bash", "-c", "source .venv/bin/activate && uvicorn main:app --host 0.0.0.0 --port 8000 --reload"]