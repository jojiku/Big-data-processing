### Kafka настройка


```bash
docker-compose build
```


```bash
docker-compose up -d
```

```bash
docker-compose ps
```
```
http://localhost:8081/#/overview

```
```bash
docker-compose down -v
```

```bash
docker-compose exec kafka kafka-topics.sh --bootstrap-server kafka:9092 --create --topic itmo2023 --partitions 1 --replication-factor 1
```
```bash
docker-compose exec kafka kafka-topics.sh --bootstrap-server kafka:9092 --describe itmo2023  
```
```bash
docker-compose exec kafka kafka-topics.sh --bootstrap-server kafka:9092 --alter --topic itmo2023 --partitions 2
```

### Hadoop
1. Сначала запускаем неймноду с командой command: ["hdfs", "namenode", "-format", "-force"]
```bash
docker-compose up -d namenode
```
Так запуститься надо только в первый раз (либо, после того, как вы снесли образ и примонтированный раздел)

3. После того, как контейнер отработал и завершился, запускаемся с командой command: ["hdfs", "namenode"]
```bash
docker-compose up -d namenode
```
5. После неймноды поднимаем датаноды, нодменеджеры и т.д.
```bash
docker-compose up -d datanode1 nodemanager1 resourcemanager 
```

Для запуска hive:

1. Сначала поднимаем постгрес.
```bash
docker-compose up -d postgres
```
3. Затем поднимаем метастор с командой command: ["schematool", "--dbType", "postgres", "--initSchema"]
```bash
docker-compose up -d metastore
```
Так запуститься надо только в первый раз (либо, после того, как вы снесли образ и примонтированный раздел)

5. После того, как контейнер отработал и завершился, запускаемся с командой command: [ "hive", "--service", "metastore" ]
```bash
docker-compose up -d metastore
```
7. После метастора запускаем hiveserver2
```bash
docker-compose up -d hiveserver2
```

### Запуск _job(s).py

```bash
docker-compose exec jobmanager ./bin/flink run -py /opt/pyflink/device_job.py -d  
```

```bash
docker-compose exec jobmanager ./bin/flink run -py /opt/pyflink/device_job_tumbling.py -d
```

```bash
docker-compose exec jobmanager ./bin/flink run -py /opt/pyflink/device_job_sliding.py -d
```

```bash
docker-compose exec jobmanager ./bin/flink run -py /opt/pyflink/device_job_session.py -d
```

