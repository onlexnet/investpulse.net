# Kafka - Diagnostyka i Testowanie

## Status

✅ **Kafka działa poprawnie** na `localhost:9092`

⚠️ Healthcheck pokazuje "unhealthy", ale to **nie przeszkadza w działaniu** - Kafka jest w pełni funkcjonalna.

## Szybka diagnostyka

```bash
# Sprawdzenie pełnego statusu
./scripts/kafka-check.sh

# Sprawdzenie czy kontener działa
docker ps | grep kafka

# Sprawdzenie logów
docker logs kafka --tail 50

# Test portu
nc -zv localhost 9092
```

## Podstawowe operacje

### Lista topików
```bash
docker exec kafka /opt/kafka/bin/kafka-topics.sh --bootstrap-server localhost:9092 --list
```

### Utworzenie topika
```bash
docker exec kafka /opt/kafka/bin/kafka-topics.sh \
  --bootstrap-server localhost:9092 \
  --create --topic test-topic \
  --partitions 3 \
  --replication-factor 1
```

### Wysłanie wiadomości (producer)
```bash
docker exec -it kafka /opt/kafka/bin/kafka-console-producer.sh \
  --bootstrap-server localhost:9092 \
  --topic test-topic
```

### Odbiór wiadomości (consumer)
```bash
docker exec -it kafka /opt/kafka/bin/kafka-console-consumer.sh \
  --bootstrap-server localhost:9092 \
  --topic test-topic \
  --from-beginning
```

## Test w Pythonie

```bash
# Instalacja biblioteki
pip install kafka-python

# Uruchomienie testu
python scripts/test-kafka.py
```

## Połączenie z aplikacji

### Python
```python
from kafka import KafkaProducer, KafkaConsumer

# Producer
producer = KafkaProducer(bootstrap_servers=['localhost:9092'])
producer.send('topic-name', b'test message')

# Consumer
consumer = KafkaConsumer('topic-name', bootstrap_servers=['localhost:9092'])
for message in consumer:
    print(message.value)
```

### Node.js / TypeScript
```javascript
const { Kafka } = require('kafkajs');

const kafka = new Kafka({
  clientId: 'my-app',
  brokers: ['localhost:9092']
});
```

### Java
```java
Properties props = new Properties();
props.put("bootstrap.servers", "localhost:9092");
```

## Typowe problemy

### Problem: "Connection refused" na localhost:9092
**Rozwiązanie:**
```bash
# Sprawdź czy kontener działa
docker ps | grep kafka

# Jeśli nie działa, uruchom ponownie
docker-compose -f .devcontainer/docker-compose.yaml up -d kafka
```

### Problem: Healthcheck pokazuje "unhealthy"
**Rozwiązanie:** To normalne i nie przeszkadza w działaniu. Healthcheck został zaktualizowany w pliku `docker-compose.yaml`, ale wymaga restartu:
```bash
docker-compose -f .devcontainer/docker-compose.yaml down
docker-compose -f .devcontainer/docker-compose.yaml up -d
```

### Problem: Nie mogę połączyć się z innego kontenera
**Rozwiązanie:** Użyj nazwy kontenera zamiast localhost:
```
bootstrap_servers=['kafka:9092']  # zamiast localhost:9092
```

## Konfiguracja

Kafka jest skonfigurowana w trybie KRaft (bez Zookeeper) z następującymi parametrami:
- **Port:** 9092
- **Partycje domyślne:** 3
- **Replication factor:** 1 (single node)
- **Broker ID:** 1

## Więcej informacji

- Dokumentacja Kafka: https://kafka.apache.org/documentation/
- KRaft mode: https://kafka.apache.org/documentation/#kraft
- Python client: https://kafka-python.readthedocs.io/
