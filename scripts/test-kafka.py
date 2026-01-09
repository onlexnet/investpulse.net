#!/usr/bin/env python3
"""
Prosty skrypt do testowania połączenia z Kafka
Użycie: python scripts/test-kafka.py
"""

from kafka import KafkaProducer, KafkaConsumer, KafkaAdminClient
from kafka.admin import NewTopic
from kafka.errors import KafkaError
import json
import time

BOOTSTRAP_SERVERS = ['localhost:9092']

def test_connection():
    """Test podstawowego połączenia z Kafka"""
    print("🔍 Testowanie połączenia z Kafka...")
    try:
        admin = KafkaAdminClient(
            bootstrap_servers=BOOTSTRAP_SERVERS,
            request_timeout_ms=5000
        )
        topics = admin.list_topics()
        print(f"✅ Połączenie działa! Znalezione topiki: {topics}")
        admin.close()
        return True
    except Exception as e:
        print(f"❌ Błąd połączenia: {e}")
        return False

def create_test_topic():
    """Tworzenie testowego topika"""
    print("\n📝 Tworzenie testowego topika 'test-python'...")
    try:
        admin = KafkaAdminClient(bootstrap_servers=BOOTSTRAP_SERVERS)
        topic = NewTopic(name='test-python', num_partitions=3, replication_factor=1)
        admin.create_topics([topic])
        print("✅ Topik 'test-python' utworzony")
        admin.close()
        return True
    except Exception as e:
        if "already exists" in str(e):
            print("ℹ️  Topik 'test-python' już istnieje")
            return True
        print(f"❌ Błąd tworzenia topika: {e}")
        return False

def test_producer():
    """Test wysyłania wiadomości"""
    print("\n📤 Testowanie producenta...")
    try:
        producer = KafkaProducer(
            bootstrap_servers=BOOTSTRAP_SERVERS,
            value_serializer=lambda v: json.dumps(v).encode('utf-8')
        )
        
        for i in range(3):
            message = {'test': f'message-{i}', 'timestamp': time.time()}
            future = producer.send('test-python', message)
            result = future.get(timeout=10)
            print(f"  ✅ Wysłano: {message} -> partition {result.partition}, offset {result.offset}")
        
        producer.flush()
        producer.close()
        return True
    except Exception as e:
        print(f"❌ Błąd producenta: {e}")
        return False

def test_consumer():
    """Test odbierania wiadomości"""
    print("\n📥 Testowanie consumera...")
    try:
        consumer = KafkaConsumer(
            'test-python',
            bootstrap_servers=BOOTSTRAP_SERVERS,
            auto_offset_reset='earliest',
            enable_auto_commit=True,
            group_id='test-group',
            value_deserializer=lambda m: json.loads(m.decode('utf-8')),
            consumer_timeout_ms=5000
        )
        
        count = 0
        for message in consumer:
            print(f"  ✅ Odebrano: partition={message.partition}, offset={message.offset}, value={message.value}")
            count += 1
        
        consumer.close()
        print(f"ℹ️  Odebrano {count} wiadomości")
        return True
    except Exception as e:
        print(f"❌ Błąd consumera: {e}")
        return False

if __name__ == "__main__":
    print("=" * 60)
    print("KAFKA CONNECTION TEST")
    print("=" * 60)
    
    if not test_connection():
        print("\n❌ Nie można połączyć się z Kafka. Sprawdź czy kontener działa:")
        print("   docker ps | grep kafka")
        print("   docker logs kafka")
        exit(1)
    
    if create_test_topic():
        test_producer()
        test_consumer()
    
    print("\n" + "=" * 60)
    print("✅ Test zakończony!")
    print("=" * 60)
