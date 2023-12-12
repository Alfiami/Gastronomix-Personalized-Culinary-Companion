# Gunakan image resmi Python
FROM python:3.8

# Atur direktori kerja
WORKDIR /app

# Salin file requirements.txt ke direktori kerja
COPY requirements.txt .

# Install dependensi Python
RUN pip install --no-cache-dir -r requirements.txt

# Salin semua file dari direktori proyek ke direktori kerja
COPY . .

# Tambahkan entri poin untuk menjalankan aplikasi Flask
CMD ["python", "app.py"]
