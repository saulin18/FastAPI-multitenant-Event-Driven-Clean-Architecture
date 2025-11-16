from fastapi_events.handlers.base import BaseEventHandler
from fastapi_events.typing import Event

from app.domain.events.user_events import UserCreatedEvent, UserUpdatedEvent
from app.domain.interfaces.mail_service import IMailService
from app.domain.interfaces.message_queue_service import IMessageQueueService
from app.shared.templates.emails.load_templates import LoadTemplates


class UserCreatedEventHandler(BaseEventHandler):
    def __init__(self, email_service: IMailService, message_queue_service: IMessageQueueService = None):
        self.email_service = email_service
        self.message_queue_service = message_queue_service
        self.template_loader = LoadTemplates()

    async def handle(self, event: Event) -> None:
        event_name, payload = event

        user_event = UserCreatedEvent(
            user_id=payload["user_id"],
            email=payload["email"],
            username=payload["username"],
            tenant_id=payload["tenant_id"],
            full_name=payload.get("full_name"),
            event_id=payload["event_id"],
            occurred_at=payload["occurred_at"],
            event_type=payload["event_type"],
        )

        # Publish to RabbitMQ
        if self.message_queue_service:
            await self._publish_to_rabbitmq("user.created", user_event)
        
        await self._send_welcome_email(user_event)
    
    async def _publish_to_rabbitmq(self, routing_key: str, event: UserCreatedEvent) -> None:
        try:
            message = {
                "event_type": event.event_type,
                "user_id": str(event.user_id),
                "email": event.email,
                "username": event.username,
                "tenant_id": str(event.tenant_id),
                "full_name": event.full_name,
                "occurred_at": event.occurred_at.isoformat() if hasattr(event.occurred_at, 'isoformat') else str(event.occurred_at),
                "event_id": str(event.event_id) if hasattr(event, 'event_id') else None
            }
            await self.message_queue_service.publish(routing_key, message)
        except Exception as e:
            print(f"Failed to publish user.created event to RabbitMQ: {e}")

    async def _send_welcome_email(self, event: UserCreatedEvent) -> None:
        try:
            html_content = self.template_loader.render_welcome_email(
                full_name=event.full_name,
                email=event.email,
                username=event.username,
                tenant_id=event.tenant_id,
            )

            await self.email_service.send_email(
                to=event.email,
                subject=f"¡Bienvenido {event.full_name or event.username}!",
                html=html_content,
            )
        except Exception as e:
            print(f"Failed to send welcome email to {event.email}: {e}")


class UserUpdatedEventHandler(BaseEventHandler):
    def __init__(self, email_service: IMailService, message_queue_service: IMessageQueueService = None):
        self.email_service = email_service
        self.message_queue_service = message_queue_service
        self.template_loader = LoadTemplates()

    async def handle(self, event: Event) -> None:
        event_name, payload = event

        user_event = UserUpdatedEvent(
            user_id=payload["user_id"],
            tenant_id=payload["tenant_id"],
            email=payload.get("email"),
            username=payload.get("username"),
            full_name=payload.get("full_name"),
            is_active=payload.get("is_active"),
            event_id=payload["event_id"],
            occurred_at=payload["occurred_at"],
            event_type=payload["event_type"],
        )

      
        if self.message_queue_service:
            await self._publish_to_rabbitmq("user.updated", user_event)

        if user_event.email:
            print(f"   Email changed to: {user_event.email}")
        if user_event.username:
            print(f"   Username changed to: {user_event.username}")
        if user_event.full_name:
            print(f"   Full name changed to: {user_event.full_name}")
        if user_event.is_active is not None:
            print(f"   Active status: {user_event.is_active}")

        await self._send_update_notification(user_event)
    
    async def _publish_to_rabbitmq(self, routing_key: str, event: UserUpdatedEvent) -> None:
        
        try:
            message = {
                "event_type": event.event_type,
                "user_id": str(event.user_id),
                "tenant_id": str(event.tenant_id),
                "email": event.email,
                "username": event.username,
                "full_name": event.full_name,
                "is_active": event.is_active,
                "occurred_at": event.occurred_at.isoformat() if hasattr(event.occurred_at, 'isoformat') else str(event.occurred_at),
                "event_id": str(event.event_id) if hasattr(event, 'event_id') else None
            }
            await self.message_queue_service.publish(routing_key, message)
        except Exception as e:
            print(f"Failed to publish user.updated event to RabbitMQ: {e}")

    async def _send_update_notification(self, event: UserUpdatedEvent) -> None:
        try:
            changes = []
            if event.email:
                changes.append("Email actualizado")
            if event.username:
                changes.append("Username actualizado")
            if event.full_name:
                changes.append("Nombre completo actualizado")
            if event.is_active is not None:
                status = "activada" if event.is_active else "desactivada"
                changes.append(f"Cuenta {status}")

            if changes and event.email:
                html_content = self.template_loader.render_profile_updated_email(
                    changes=changes,
                    tenant_id=event.tenant_id,
                    updated_at=str(event.occurred_at),
                )

                await self.email_service.send_email(
                    to=event.email,
                    subject="Tu perfil ha sido actualizado",
                    html=html_content,
                )
        except Exception as e:
            print(f"Failed to send update notification: {e}")
