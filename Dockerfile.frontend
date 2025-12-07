FROM node:18-alpine

WORKDIR /opt/frontend

COPY package*.json ./
RUN npm ci

COPY bundles-src ./bundles-src

RUN npm run build

CMD ["sh", "-c", "tail -f /dev/null"]
