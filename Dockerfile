FROM python:3.12-alpine

WORKDIR /app

COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

ENV PORT=80

COPY app.py ./
COPY index.html ./
COPY testimoni.html ./
COPY *.webp ./
COPY *.jpeg ./
COPY *.png ./
COPY testimonial/ ./testimonial/
COPY catalog/ ./catalog/

EXPOSE 80

CMD ["python", "app.py"]