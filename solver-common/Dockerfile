FROM openjdk:21-jdk-slim

WORKDIR /solver-server

RUN apt-get update && apt-get install -y maven

COPY solver-common /solver-server
COPY .env .env

RUN mvn dependency:go-offline

RUN mvn clean install

CMD ["java", "-jar", "target/solver-0.1.jar"]