#!/bin/bash
# Skrypt do diagnostyki Kafka

echo "=== Sprawdzanie stanu kontenera Kafka ==="
docker ps -a | grep -E 'CONTAINER|kafka'

echo -e "\n=== Sprawdzanie portu 9092 ==="
nc -zv localhost 9092 2>&1

echo -e "\n=== Lista topików Kafka ==="
docker exec kafka /opt/kafka/bin/kafka-topics.sh --bootstrap-server localhost:9092 --list

echo -e "\n=== Metadata brokera ==="
docker exec kafka /opt/kafka/bin/kafka-metadata.sh --snapshot /tmp/kraft-combined-logs/__cluster_metadata-0/00000000000000000000.log --print-records 2>/dev/null | head -20 || echo "Metadata niedostępna"

echo -e "\n=== Status klastra ==="
docker exec kafka /opt/kafka/bin/kafka-broker-api-versions.sh --bootstrap-server localhost:9092 2>&1 | head -5

echo -e "\n=== Ostatnie logi Kafka ==="
docker logs kafka --tail 10

echo -e "\n✅ Kafka jest dostępna pod adresem: localhost:9092"
echo "📝 Aby stworzyć testowy topik:"
echo "   docker exec kafka /opt/kafka/bin/kafka-topics.sh --bootstrap-server localhost:9092 --create --topic test-topic --partitions 3 --replication-factor 1"
echo "📤 Aby wysłać wiadomość:"
echo "   docker exec -it kafka /opt/kafka/bin/kafka-console-producer.sh --bootstrap-server localhost:9092 --topic test-topic"
echo "📥 Aby odebrać wiadomość:"
echo "   docker exec -it kafka /opt/kafka/bin/kafka-console-consumer.sh --bootstrap-server localhost:9092 --topic test-topic --from-beginning"
