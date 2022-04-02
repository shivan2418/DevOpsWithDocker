FROM openjdk:8
EXPOSE 8080
WORKDIR /app
COPY . .
RUN ./mvnw package
#RUN ["chmod", "+x",  "/app/target/docker-example-1.1.3.jar"]

COPY . .
CMD ["java", "-jar", "/app/target/docker-example-1.1.3.jar"]

