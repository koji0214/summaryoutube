# Node.jsの公式イメージをベースにする
FROM node:20

# 作業ディレクトリを設定
WORKDIR /app

# package.jsonとpackage-lock.jsonをコピー
COPY package*.json ./

# 依存関係をインストール
RUN npm cache clean --force
RUN npm install

# アプリケーションコードをコピー
COPY . .



# 開発サーバーを起動
CMD ["sh", "-c", "npm install && npm run dev"]
