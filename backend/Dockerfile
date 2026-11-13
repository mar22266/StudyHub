FROM python:3.12-slim
WORKDIR /app
COPY requirements.txt .
RUN python -m pip install --no-cache-dir --upgrade pip==26.3 && python -m pip install --no-cache-dir -r requirements.txt
COPY app ./app
RUN useradd --system --create-home appuser
USER appuser
EXPOSE 6001
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "6001"]
