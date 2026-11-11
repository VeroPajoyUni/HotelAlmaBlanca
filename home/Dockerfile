FROM nginx:alpine

WORKDIR /usr/share/nginx/html

# Copiar toda la página (HTML, css, js e img); lo que no se copia está en .dockerignore
COPY . .

# Dar permiso de lectura a nginx sobre todos los archivos
RUN chmod -R a+rX /usr/share/nginx/html

EXPOSE 80

CMD ["nginx", "-g", "daemon off;"]
