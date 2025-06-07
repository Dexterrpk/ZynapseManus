from fastapi import FastAPI, Request, Depends, HTTPException, status
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi.middleware.cors import CORSMiddleware
from sqlmodel import SQLModel

from .core.database import engine
from .core.config import settings
# Import all routers
from .routes import auth, users, plans, campaigns, ai_training, ai_interaction, whatsapp, bot_control
import os

# Criar tabelas no banco de dados
SQLModel.metadata.create_all(engine)

app = FastAPI(
    title="Zynapse API",
    description="API para o sistema Zynapse de automação comercial com WhatsApp e IA",
    version="1.1.2", # Increment version for router inclusion fix
)

# Configurar CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Em produção, especificar origens permitidas
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# --- Incluir rotas da API com prefixo /api/v1 ---
api_prefix = "/api/v1"

app.include_router(auth.router, prefix=api_prefix)
app.include_router(users.router, prefix=api_prefix)
app.include_router(plans.router, prefix=api_prefix)
app.include_router(campaigns.router, prefix=api_prefix)
app.include_router(ai_training.router, prefix=api_prefix)
app.include_router(ai_interaction.router, prefix=api_prefix)
app.include_router(whatsapp.router, prefix=api_prefix)
# Include bot_control router with the main API prefix.
# The internal prefix in bot_control.py is now just "/bot", so the final path will be /api/v1/bot/...
app.include_router(bot_control.router, prefix=api_prefix)

# Montar arquivos estáticos (fora da API)
static_dir = "static"
if not os.path.isdir(static_dir):
    static_dir_alt = os.path.join(os.path.dirname(__file__), "..", static_dir)
    if os.path.isdir(static_dir_alt):
        static_dir = static_dir_alt
    else:
        print(f"Warning: Static directory 	'{static_dir}'	 not found.")
if os.path.isdir(static_dir):
    app.mount("/static", StaticFiles(directory=static_dir), name="static")

# Configurar templates (fora da API)
templates_dir = "templates"
if not os.path.isdir(templates_dir):
    templates_dir_alt = os.path.join(os.path.dirname(__file__), "..", templates_dir)
    if os.path.isdir(templates_dir_alt):
        templates_dir = templates_dir_alt
    else:
         print(f"Warning: Templates directory 	'{templates_dir}'	 not found.")
if os.path.isdir(templates_dir):
    templates = Jinja2Templates(directory=templates_dir)
else:
    templates = None

# Rota raiz (fora da API)
@app.get("/", response_class=HTMLResponse)
async def root(request: Request):
    return HTMLResponse(content="""
    <html>
        <head>
            <title>Zynapse API</title>
            <meta http-equiv="refresh" content="0;url=/frontend/login.html">
        </head>
        <body>
            <p>Redirecionando para a página de login...</p>
        </body>
    </html>
    """)

# Montar frontend (fora da API)
frontend_dir = "frontend"
if not os.path.isdir(frontend_dir):
    frontend_dir_alt = os.path.join(os.path.dirname(__file__), "..", frontend_dir)
    if os.path.isdir(frontend_dir_alt):
        frontend_dir = frontend_dir_alt
    else:
        print(f"Error: Frontend directory 	'{frontend_dir}'	 not found. Cannot serve frontend.")
if os.path.isdir(frontend_dir):
    app.mount("/frontend", StaticFiles(directory=frontend_dir, html=True), name="frontend")

# Tratamento de erros
@app.exception_handler(404)
async def not_found_exception_handler(request: Request, exc: HTTPException):
    if request.url.path.startswith(api_prefix):
        return JSONResponse(
            status_code=status.HTTP_404_NOT_FOUND,
            content={"detail": "Recurso da API não encontrado"},
        )
    if os.path.isdir(frontend_dir):
         return HTMLResponse(content='	<meta http-equiv="refresh" content="0;url=/frontend/login.html">	', status_code=307)
    else:
        return JSONResponse(status_code=404, content={"detail": "Recurso não encontrado"})

@app.exception_handler(HTTPException)
async def http_exception_handler(request: Request, exc: HTTPException):
    return JSONResponse(
        status_code=exc.status_code,
        content={"detail": exc.detail},
        headers=getattr(exc, "headers", None),
    )

@app.exception_handler(Exception)
async def general_exception_handler(request: Request, exc: Exception):
    print(f"Unhandled exception: {exc}")
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={"detail": "Ocorreu um erro interno inesperado no servidor."},
    )

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("backend.main:app", host="0.0.0.0", port=8000, reload=True)

