# Pythonの公式イメージをベースにする
FROM python:3.12-slim

# ghcr.ioからuvの最新バイナリを一時的なステージとしてコピー
COPY --from=ghcr.io/astral-sh/uv:0.7.16 /uv /uvx /bin/

COPY . /app
# 作業ディレクトリを設定
WORKDIR /app/src

# 依存関係ファイルをコピーしてインストール
RUN uv sync

# 仮想環境を設定
ENV PATH="/app/.venv/bin:$PATH"
ENV PYTHONPATH="/app:$PYTHONPATH"

# FastAPIサーバーを起動
CMD ["/bin/bash", "-c", "source /app/.venv/bin/activate && uvicorn src.main:app --host 0.0.0.0 --port 8000"]