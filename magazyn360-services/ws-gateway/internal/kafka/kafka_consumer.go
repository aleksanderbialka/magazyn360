package kafka

import (
	"context"
	"log"
	"time"

	"github.com/segmentio/kafka-go"
	"ws-gateway/internal/ws"
)

type Consumer struct {
	reader *kafka.Reader
	hub    *ws.Hub
}

func NewConsumer(brokers []string, topic, groupID string, hub *ws.Hub) *Consumer {
	reader := kafka.NewReader(kafka.ReaderConfig{
		Brokers: brokers,
		Topic:   topic,
		GroupID: groupID,
	})
	return &Consumer{reader: reader, hub: hub}
}

func (c *Consumer) Start(ctx context.Context) {
	defer c.reader.Close()
	log.Printf("Kafka consumer started on topic %s", c.reader.Config().Topic)

	for {
		m, err := c.reader.ReadMessage(ctx)
		if err != nil {
			log.Printf("Kafka read error: %v", err)
			time.Sleep(time.Second)
			continue
		}
		log.Printf("Kafka message: %s", string(m.Value))
		c.hub.Broadcast <- m.Value
	}
}
