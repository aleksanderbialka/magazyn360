package config

import (
	"log"
	"os"
	"strings"
)

type Config struct {
	ServerPort    string
	KafkaBrokers  []string
	KafkaTopic    string
	KafkaGroupID  string
}

func LoadConfig() *Config {
	port := getEnv("WS_GATEWAY_PORT", "8080")
	brokers := strings.Split(getEnv("KAFKA_BROKERS", "kafka-broker:9092"), ",")
	topic := getEnv("KAFKA_TOPIC", "ws-topic")
	groupID := getEnv("KAFKA_GROUP_ID", "ws-consumer-group")

	log.Printf("Config loaded: port=%s topic=%s brokers=%v", port, topic, brokers)

	return &Config{
		ServerPort:    port,
		KafkaBrokers:  brokers,
		KafkaTopic:    topic,
		KafkaGroupID:  groupID,
	}
}

func getEnv(key string, fallback string) string {
	if value, exists := os.LookupEnv(key); exists && value != "" {
		return value
	}
	return fallback
}
