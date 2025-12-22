# Use an official Python runtime as a parent image
FROM python:3.9-slim-buster

# Set the working directory in the container
WORKDIR /app

# Copy the requirements file into the container
COPY requirements.txt .

# Install any needed packages specified in requirements.txt
# Using --no-cache-dir to keep the image size smaller
RUN pip install --no-cache-dir -r requirements.txt

# Copy the current directory contents into the container at /app
# This includes app.py, the templates directory, and any other necessary files
COPY . .

# Make sure the upload and reordered folders exist and are writable by the application
RUN mkdir -p /app/uploads /app/reordered

# Make port 5000 available to the world outside this container
EXPOSE 5000

# Run the application using Flask's built-in development server
# --host=0.0.0.0 makes the server accessible from outside the container
# --port=5000 is the port we've exposed
# --debug=True is useful for development, but should be False in production
CMD ["flask", "run", "--host=0.0.0.0", "--port=5000", "--debug"]