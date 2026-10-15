FROM nginx:alpine

WORKDIR /usr/share/nginx/html

# Copiar la página, los estilos/imágenes y el JavaScript
COPY index.html .
COPY css ./css
COPY js ./js

# Dar permiso de lectura a nginx sobre todos los archivos
RUN chmod -R a+rX /usr/share/nginx/html

EXPOSE 80

CMD ["nginx", "-g", "daemon off;"]
