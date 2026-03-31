FROM node:20-slim

WORKDIR /app/webui

COPY webui/package.json /app/webui/package.json
COPY webui/package-lock.json /app/webui/package-lock.json
RUN npm ci

COPY webui /app/webui

CMD ["npm", "run", "dev"]
