# Use the official Python image as the base image
FROM python:3.12-slim

# Set the working directory
WORKDIR /app

# Copy the current directory contents into the container at /app
COPY . /app

# Install the dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Expose the port FastAPI is running on
EXPOSE 80

# Command to run the FastAPI app
CMD ["fastapi","run", "--port", "80"]
