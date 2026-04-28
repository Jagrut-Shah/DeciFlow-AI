FROM node:20-alpine

WORKDIR /app

COPY package*.json ./
RUN npm install

COPY . .

# Set the API URL as a build argument (can be passed via --build-arg)
ARG NEXT_PUBLIC_API_URL=http://localhost:8000
ENV NEXT_PUBLIC_API_URL=${NEXT_PUBLIC_API_URL}


RUN npm run build

# Install simple static server
RUN npm install -g serve

EXPOSE 8080

CMD ["serve", "-s", "out", "-l", "8080"]