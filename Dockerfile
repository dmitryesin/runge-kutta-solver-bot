FROM python:3.13.3-slim

# Set the working directory
WORKDIR /diffy-bot

# Update package lists and install necessary packages including maven
RUN apt-get update && apt-get install -y maven

# Copy all files into the working directory
COPY . /diffy-bot

# Install Python dependencies
RUN pip install -r requirements.txt

# Install OpenJDK
COPY --from=openjdk:21-jdk-slim /usr/local/openjdk-21 /usr/local/openjdk-21

# Set JAVA_HOME
ENV JAVA_HOME=/usr/local/openjdk-21

RUN update-alternatives --install /usr/bin/java java /usr/local/openjdk-21/bin/java 1 \
    && update-alternatives --install /usr/bin/javac javac /usr/local/openjdk-21/bin/javac 1

# Input Telegram bot token
RUN cd /diffy-bot/solver-bot/src/main/python/config \
    && echo '{ "TELEGRAM_TOKEN": "YOUR_TOKEN" }' > config.json

# Run Maven clean install
RUN mvn clean install

# Run main script
CMD ["python", "solver-bot/src/main/python/main.py"]