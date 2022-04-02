FROM node:16.13.2
WORKDIR /app
EXPOSE 5000
COPY package.json package-lock.json ./
RUN npm install && npm install -g serve
ENV REACT_APP_BACKEND_URL http://localhost:8080
COPY . ./
RUN npm run build


CMD serve -s -l 5000 build
