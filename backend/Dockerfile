FROM python:3.9
WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt --no-cache-dir
COPY . .
ENV PYTHONUNBUFFERED=1
CMD ["gunicorn", "--bind", "0.0.0.0:8000", "--log-level", "DEBUG", "core.wsgi"]