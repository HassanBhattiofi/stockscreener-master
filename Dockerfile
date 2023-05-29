FROM python:3.9

WORKDIR /app
COPY . /app
RUN pip install --no-cache-dir -r requirements.txt --index-url=https://pypi.org/simple/

EXPOSE 8000
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
