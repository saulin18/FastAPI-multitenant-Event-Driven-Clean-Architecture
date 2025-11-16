import json
from typing import Any, Dict
from aio_pika import connect, Message, ExchangeType
from app.domain.interfaces.message_queue_service import IMessageQueueService
from app.shared.config import Settings


class RabbitMQService(IMessageQueueService):
    
    def __init__(self, settings: Settings):
        self.settings = settings
        self.connection = None
        self.channel = None
        self.exchange = None
    
    async def connect(self) -> None:
       
        try:
            self.connection = await connect(self.settings.rabbitmq_url)
            self.channel = await self.connection.channel()
            
            
            self.exchange = await self.channel.declare_exchange(
                self.settings.rabbitmq_exchange,
                ExchangeType.TOPIC,
                durable=True
            )
            
           
            queue = await self.channel.declare_queue(
                self.settings.rabbitmq_queue, 
                durable=True
            )
            
           
            await queue.bind(self.exchange, routing_key="user.*")
            
            print(f"Connected to RabbitMQ: {self.settings.rabbitmq_exchange}")
        except Exception as e:
            print(f"Error connecting to RabbitMQ: {e}")
            raise
    
    async def disconnect(self) -> None:
        
        try:
            if self.channel:
                await self.channel.close()
            if self.connection:
                await self.connection.close()
            print("Disconnected from RabbitMQ")
        except Exception as e:
            print(f"Error disconnecting from RabbitMQ: {e}")
    
    async def publish(self, routing_key: str, message: Dict[str, Any]) -> None:
        
        if not self.exchange:
            await self.connect()
        
        try:
            message_body = json.dumps(message).encode()
            await self.exchange.publish(
                Message(message_body),
                routing_key=routing_key
            )
            print(f"Message published to {routing_key}: {message}")
        except Exception as e:
            print(f"Error publishing message to RabbitMQ: {e}")
            raise

