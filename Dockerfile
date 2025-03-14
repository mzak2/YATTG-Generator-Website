FROM python:3.9-slim

# Set environment variables to avoid interaction during installation
ENV DEBIAN_FRONTEND=noninteractive
ENV DB_URL="postgresql://postgres:1111@pg_4:5432/dnd_generator"

# Set the working directory
WORKDIR /app

# Copy only the requirements file first to leverage Docker cache
COPY ./app/requirements.txt .

# Install dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy the rest of the application files
COPY ./app .

# Expose the port your app will run on
EXPOSE 8888

# Run the app using Uvicorn (ASGI server)
CMD ["uvicorn", "app:app", "--host", "0.0.0.0", "--port", "8888", "--workers", "4"]
