# Base image with Python 3.11 slim version
FROM python:3.11-slim

WORKDIR /app

#copy the requirements files to the working directory
COPY pyproject.toml uv.lock ./

# Install dependencies using uv and pip
RUN pip install --no-cache-dir --upgrade pip uv \
    && uv export --frozen --no-dev --format requirements-txt > requirements.txt \
    && pip install --no-cache-dir -r requirements.txt \
    && rm requirements.txt

# Copy the main application file to the working directory
COPY main.py ./

# Expose the port that the application will run on
EXPOSE 8000

# Command to run the application using uvicorn
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
