import os
import uvicorn
from fastapi import FastAPI, Depends, HTTPException, status, Form
from typing import Annotated
from keycloak import KeycloakOpenID

from sqlalchemy.orm import Session

from database import database as database
from database.database import Ticket

from model.ticket import TicketModel

app = FastAPI()
database.Base.metadata.create_all(bind=database.engine)

# Данные для подключения к Keycloak
KEYCLOAK_URL = "http://keycloak:8080/"
KEYCLOAK_CLIENT_ID = "boyarkov"
KEYCLOAK_REALM = "myrealm"
KEYCLOAK_CLIENT_SECRET = "T678RfL6Jxtk5zmNQygPAn7ahcTnPzTr"

keycloak_openid = KeycloakOpenID(server_url=KEYCLOAK_URL,
                                  client_id=KEYCLOAK_CLIENT_ID,
                                  realm_name=KEYCLOAK_REALM,
                                  client_secret_key=KEYCLOAK_CLIENT_SECRET)

def get_db():
    db = database.SessionLocal()
    try:
        yield db
    finally:
        db.close()


db_dependency = Annotated[Session, Depends(get_db)]

user_token = ""


#######
#Jaeger
from opentelemetry import trace
from opentelemetry.exporter.jaeger.thrift import JaegerExporter
from opentelemetry.sdk.resources import SERVICE_NAME, Resource
from opentelemetry.sdk.trace import  TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor
from opentelemetry.instrumentation.fastapi import FastAPIInstrumentor

resource = Resource(attributes={
    SERVICE_NAME: "ticket-service"
})

jaeger_exporter = JaegerExporter(
    agent_host_name="jaeger",
    agent_port=6831
)

provider = TracerProvider(resource=resource)
processor = BatchSpanProcessor(jaeger_exporter)
provider.add_span_processor(processor)
trace.set_tracer_provider(provider)

FastAPIInstrumentor.instrument_app(app)

###########
#Prometheus
from prometheus_fastapi_instrumentator import Instrumentator
Instrumentator().instrument(app).expose(app)

@app.post("/get-token")
async def get_token(username: str = Form(...), password: str = Form(...)):
    try:
        # Получение токена
        token = keycloak_openid.token(grant_type=["password"],
                                      username=username,
                                      password=password)
        global user_token
        user_token = token
        return token
    except Exception as e:
        print(e)  # Логирование для диагностики
        raise HTTPException(status_code=400, detail="Не удалось получить токен")

def check_user_roles():
    global user_token
    token = user_token
    try:
        userinfo = keycloak_openid.userinfo(token["access_token"])
        token_info = keycloak_openid.introspect(token["access_token"])
        if "testRole" not in token_info["realm_access"]["roles"]:
            raise HTTPException(status_code=403, detail="Access denied")
        return token_info
    except Exception as e:
        raise HTTPException(status_code=401, detail="Invalid token or access denied")

@app.get("/health", status_code=status.HTTP_200_OK)
async def statistics_alive():
    if (check_user_roles()):
        return {'message': 'service is active'}
    else:
        return "Wrong JWT Token"


@app.get("/get_tickets")
async def get_tickets(db: db_dependency):
    if (check_user_roles()):
        try:
            result = db.query(Ticket).limit(100).all()
            return result
        except Exception as e:
            return "Cant access database!"
    else:
        return "Wrong JWT Token"



@app.get("/get_ticket_by_id")
async def get_ticket_by_id(ticket_id: int, db: db_dependency):
    if (check_user_roles()):
        try:
            result = db.query(Ticket).filter(Ticket.id == ticket_id).first()
            return result
        except Exception as e:
            raise HTTPException(status_code=404, detail="Ticket not found")
        return result
    else:
        return "Wrong JWT Token"



@app.post("/add_ticket")
async def add_ticket(ticket: TicketModel, db: db_dependency):
    if (check_user_roles()):
        ticket_db = Ticket(passenger_name=ticket.passenger_name,
                           passport=ticket.passport,
                           id_airplane=ticket.id_airplane,
                           direction=ticket.direction)
        try:
            db.add(ticket_db)
            db.commit()
            db.refresh(ticket_db)
            return "Success"
        except Exception:
            return "cant add ticket"
    else:
        return "Wrong JWT Token"



@app.delete("/delete_ticket")
async def delete_ticket(ticket_id: int, db: db_dependency):
    if (check_user_roles()):
        try:
            ticket = db.query(Ticket).filter(Ticket.id == ticket_id).first()
            db.delete(ticket)
            return "Success"
        except Exception as e:
            return "cant find ticket"
    else:
        return "Wrong JWT Token"



if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=int(os.getenv('PORT', 80)))
