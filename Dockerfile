# Use an official Python runtime as a parent image
FROM python:3.11-slim

RUN dpkg --add-architecture i386 

RUN apt-get update && apt-get install -y build-essential

RUN apt-get install -y libportaudio2 portaudio19-dev

RUN pip install --no-cache-dir PyAudio==0.2.11

# Set the working directory in the container to /code
WORKDIR /code 

# Copy the file with the requirements to the /code directory
COPY ./requirements.txt /code/requirements.txt

# Install the package dependencies in the requirements file
RUN pip install --no-cache-dir --upgrade -r /code/requirements.txt

# Copy the ./app directory inside the /code directory
COPY ./app /code/app

# Set the command to run the uvicorn server
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "80"]