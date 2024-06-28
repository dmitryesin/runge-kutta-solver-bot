FROM python:3.9-slim

# Set the working directory
WORKDIR /runge-kutta-solver-bot

# Update package lists and install necessary packages including maven
RUN apt-get update && apt-get install -y maven

# Copy all files into the working directory
COPY . /runge-kutta-solver-bot

# Install Python dependencies
RUN pip install -r requirements.txt

# Install OpenJDK 8
COPY --from=openjdk:8-jdk-slim /usr/local/openjdk-8 /usr/local/openjdk-8

# Set JAVA_HOME
ENV JAVA_HOME /usr/local/openjdk-8

RUN update-alternatives --install /usr/bin/java java /usr/local/openjdk-8/bin/java 1 \
    && update-alternatives --install /usr/bin/javac javac /usr/local/openjdk-8/bin/javac 1

# Input Telegram bot token
RUN cd /runge-kutta-solver-bot/solver-bot/src/main/python/config \
    && echo '{ "TELEGRAM_TOKEN": "YOUR_TOKEN" }' > config.json

# Run Maven clean install
RUN mvn clean install

# Run main script
CMD ["python", "solver-bot/src/main/python/main.py"]
