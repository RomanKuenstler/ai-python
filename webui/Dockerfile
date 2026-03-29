FROM node:20-alpine

WORKDIR /app/webui

COPY webui/package.json /app/webui/package.json
RUN npm install

COPY webui /app/webui

CMD ["npm", "run", "dev"]
