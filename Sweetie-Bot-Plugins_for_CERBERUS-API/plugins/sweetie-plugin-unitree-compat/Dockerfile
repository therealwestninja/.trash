FROM python:3.11-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY app ./app
COPY sweetie_plugin_sdk ./sweetie_plugin_sdk
ENV PORT=7101
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "7101"]
