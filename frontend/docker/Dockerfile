FROM node:10 
COPY app_v2/ /app/
WORKDIR /app
RUN npm install && npm install --save vue-resource
RUN npm run build
CMD npm run serve
