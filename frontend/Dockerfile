FROM node:20-alpine

WORKDIR /app

COPY package*.json ./
RUN npm install

COPY . .

ENV NEXT_PUBLIC_API_URL=https://deciflow-ai-647556267131.europe-west1.run.app

RUN npm run build

# Install simple static server
RUN npm install -g serve

EXPOSE 8080

CMD ["serve", "-s", "out", "-l", "8080"]