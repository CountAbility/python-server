from uuid import UUID

from datetime import datetime
from sqlalchemy.orm import Session
from starlette.websockets import WebSocket

import crud
import schemas


def serialize_alert(alert: schemas.Alert):
    return {
        "surgery_id": str(alert.surgery_id),
        "message": alert.message,
        "severity": alert.severity,
        "time_started": datetime.isoformat(alert.time_started),
        "time_resolved": datetime.isoformat(alert.time_resolved),
        "overridden": alert.overridden,
        "resolved": alert.resolved,
        "id": str(alert.id)
    }


class AlertManager:
    def __init__(self):
        self.active_connections: list[WebSocket] = []

    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.active_connections.append(websocket)

    def disconnect(self, websocket: WebSocket):
        self.active_connections.remove(websocket)

    async def broadcast_alerts(self, db: Session, surgery_id: UUID):
        alerts = list(map(serialize_alert, crud.get_surgery_alerts(db, surgery_id)))

        for connection in self.active_connections:
            await connection.send_json({"type": "alerts", "data": alerts})

