FROM python:3.13-slim-bookworm

ENV DEBIAN_FRONTEND=noninteractive \
    PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

# 1) בסיס + unixODBC
RUN apt-get update && apt-get install -y --no-install-recommends \
    curl ca-certificates gnupg apt-transport-https \
    unixodbc unixodbc-dev && \
    rm -rf /var/lib/apt/lists/*

# 2) מוסיפים את מפתחות החתימה של מיקרוסופט בצורה תקנית (לא apt-key)
RUN curl -fsSL https://packages.microsoft.com/keys/microsoft.asc \
    | gpg --dearmor -o /usr/share/keyrings/microsoft-prod.gpg

# 3) מוסיפים את ה־repo עם signed-by
RUN echo "deb [arch=amd64 signed-by=/usr/share/keyrings/microsoft-prod.gpg] https://packages.microsoft.com/debian/12/prod bookworm main" \
    > /etc/apt/sources.list.d/microsoft-prod.list

# 4) מתקינים msodbcsql18 + mssql-tools18
RUN apt-get update && ACCEPT_EULA=Y apt-get install -y --no-install-recommends \
    msodbcsql18 mssql-tools18 && \
    rm -rf /var/lib/apt/lists/*

# המשך כרגיל
WORKDIR /opt/app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY . .

# משתמש לא-Root (אופציונלי)
RUN useradd -m appuser && chown -R appuser:appuser /opt/app
USER appuser

EXPOSE 10000
CMD ["sh","-c","uvicorn app:app --host 0.0.0.0 --port ${PORT:-10000}"]
