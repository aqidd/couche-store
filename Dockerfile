FROM nginx:alpine

WORKDIR /usr/share/nginx/html

# Copy static HTML and assets
COPY index.html .
COPY *.webp .
COPY *.jpeg .
COPY *.png .
COPY testimonial/ ./testimonial/

# Expose port 80
EXPOSE 80

# Start nginx in foreground mode
CMD ["nginx", "-g", "daemon off;"]