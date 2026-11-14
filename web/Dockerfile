FROM node:24-slim

WORKDIR /app

COPY package.json package-lock.json* ./
RUN if [ -f package-lock.json ]; then npm ci; else npm install; fi

EXPOSE 3000
CMD ["npx", "nuxt", "dev", "--host", "0.0.0.0"]
