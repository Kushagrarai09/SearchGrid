import asyncio, json, logging
from datetime import datetime, timezone
from sqlalchemy import select
from aiokafka import AIOKafkaProducer
from app.core.config import settings
from app.db.session import SessionLocal
from app.db.models import OutboxEvent
from app.services.search import index_document, delete_document, ensure_index

logging.basicConfig(level=logging.INFO)
log = logging.getLogger("searchgrid.indexer")

async def process_event(event: OutboxEvent, producer):
    payload = event.payload
    if event.event_type == "document.delete":
        delete_document(payload["id"])
    else:
        index_document(payload)
    await producer.send_and_wait(settings.kafka_topic, {
        "event_id": event.id, "event_type": event.event_type,
        "aggregate_id": event.aggregate_id, "payload": payload
    })
    event.published_at = datetime.now(timezone.utc)

async def main():
    producer = AIOKafkaProducer(bootstrap_servers=settings.kafka_bootstrap_servers,
                                value_serializer=lambda v: json.dumps(v, default=str).encode())
    while True:
        try:
            await producer.start()
            break
        except Exception as exc:
            log.warning("Kafka not ready: %s", exc)
            await asyncio.sleep(3)
    ensure_index()
    log.info("SearchGrid indexing worker started")
    while True:
        db = SessionLocal()
        try:
            events = db.scalars(select(OutboxEvent).where(OutboxEvent.published_at.is_(None))
                                .order_by(OutboxEvent.id).limit(100)).all()
            if not events:
                await asyncio.sleep(settings.outbox_poll_seconds)
                continue
            for event in events:
                try:
                    await process_event(event, producer)
                    db.commit()
                    log.info("Processed outbox event %s (%s)", event.id, event.event_type)
                except Exception:
                    db.rollback()
                    log.exception("Failed event %s; it will be retried", event.id)
                    await asyncio.sleep(2)
                    break
        except Exception:
            db.rollback()
            log.exception("Worker loop error")
            await asyncio.sleep(3)
        finally:
            db.close()

if __name__ == "__main__":
    asyncio.run(main())
