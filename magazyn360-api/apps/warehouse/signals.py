from django.db.models.signals import post_save
from django.dispatch import receiver

from apps.core.kafka import KafkaEventProducer as Producer

from .models import WarehouseDocument


@receiver(post_save, sender=WarehouseDocument)
def warehouse_document_created(sender, instance, created, **kwargs):
    if created:
        event = {
            "event_type": "document_created",
            "document_id": str(instance.id),
            "doc_type": instance.doc_type,
            "status": instance.status,
            "timestamp": instance.created_at.isoformat(),
        }
        Producer.send_event("ws-topic", event)
