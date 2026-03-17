from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.db import init_db
from app.routes import collect, context, draft, evaluate, history, send, sessions
from app.utils.logging import configure_logging

app = FastAPI(title='EzLink Outreach Agent MVP')

app.add_middleware(
    CORSMiddleware,
    allow_origins=['*'],
    allow_credentials=True,
    allow_methods=['*'],
    allow_headers=['*'],
)


@app.on_event('startup')
def startup() -> None:
    configure_logging()
    init_db()


@app.get('/health')
def health():
    return {'status': 'ok'}


app.include_router(context.router)
app.include_router(sessions.router)
app.include_router(collect.router)
app.include_router(evaluate.router)
app.include_router(draft.router)
app.include_router(send.router)
app.include_router(history.router)
