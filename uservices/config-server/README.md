# Spring Cloud Config Server

Ten projekt to Spring Cloud Config Server, który serwuje konfigurację dla innych mikrousług.

## Konfiguracja

Config Server działa na porcie **8888** i używa profilu `native` do serwowania plików konfiguracyjnych z katalogu classpath.

## Wartości konfiguracyjne

Serwer dostarcza następującą wartość:

- `TWITTER_KEY` - klucz API do Twitter/X

### Edycja wartości

Aby zmienić wartość klucza API, edytuj plik:
```
src/main/resources/config/application.properties
```

## Uruchamianie

```bash
cd /investpulse.net/uservices/config-server
mvn spring-boot:run
```

Lub po zbudowaniu projektu:
```bash
java -jar target/config-server-0.0.1-SNAPSHOT.jar
```

## Testowanie

Po uruchomieniu serwera, możesz sprawdzić konfigurację pod adresem:
```
http://localhost:8888/application/default
```

Odpowiedź będzie zawierać wartość `TWITTER_KEY` oraz inne konfiguracje.

## Integracja z innymi serwisami

Aby podłączyć inne mikrousługi do Config Server, dodaj do nich:

1. Zależność:
```xml
<dependency>
    <groupId>org.springframework.cloud</groupId>
    <artifactId>spring-cloud-starter-config</artifactId>
</dependency>
```

2. Konfigurację w `application.properties`:
```properties
spring.config.import=optional:configserver:http://localhost:8888
```

Wtedy wartość `TWITTER_KEY` będzie dostępna poprzez `@Value("${TWITTER_KEY}")` lub `Environment`.
