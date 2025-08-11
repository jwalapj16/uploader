# python 
FROM python:3.13


#  Set environment variables (avoid Python writing pyc files, enable stdout flushing)
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# 3️⃣ Set the working directory
WORKDIR /Uploader

# 4️⃣ Install system dependencies (needed for psycopg2)
RUN apt-get update && apt-get install -y \
    build-essential \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*


# 5️⃣ Copy dependency file first for caching
COPY requirements.txt .

# 6️⃣ Install dependencies
RUN pip install --no-cache-dir -r requirements.txt

# 7️⃣ Copy the project files
COPY . .

# 8️⃣ Expose FastAPI port
EXPOSE 8000

# 9️⃣ Start FastAPI with uvicorn
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]