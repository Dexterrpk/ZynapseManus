from fastapi import APIRouter, Depends, HTTPException, status
from typing import Dict, Any
from ..core.dependencies import get_current_active_user
from ..models.user import User
from ..core.config import settings
import os
import json

router = APIRouter(
    prefix="/api/v1/ai",
    tags=["ai"],
    responses={404: {"description": "Not found"}},
)

# Caminho para o arquivo de configuração da IA
AI_CONFIG_FILE = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), "whatsapp-bot", "ai_config.json")

# Função para carregar a configuração da IA
def load_ai_config():
    try:
        if os.path.exists(AI_CONFIG_FILE):
            with open(AI_CONFIG_FILE, "r", encoding="utf-8") as f:
                return json.load(f)
        else:
            # Configuração padrão
            default_config = {
                "prompt": "Você é um assistente virtual da Zynapse, uma empresa de automação comercial. Seja cordial, profissional e conciso. Limite suas respostas a 3-4 frases no máximo. Ofereça ajuda sobre produtos de automação comercial, atendimento ao cliente e agendamento de demonstrações.",
                "temperature": 0.7,
                "max_tokens": 150
            }
            
            # Salvar configuração padrão
            with open(AI_CONFIG_FILE, "w", encoding="utf-8") as f:
                json.dump(default_config, f, indent=2)
            
            return default_config
    except Exception as e:
        print(f"Erro ao carregar configuração da IA: {str(e)}")
        return {
            "prompt": "Você é um assistente virtual da Zynapse.",
            "temperature": 0.7,
            "max_tokens": 150
        }

# Função para salvar a configuração da IA
def save_ai_config(config):
    try:
        # Garantir que o diretório existe
        os.makedirs(os.path.dirname(AI_CONFIG_FILE), exist_ok=True)
        
        with open(AI_CONFIG_FILE, "w", encoding="utf-8") as f:
            json.dump(config, f, indent=2)
        
        return True
    except Exception as e:
        print(f"Erro ao salvar configuração da IA: {str(e)}")
        return False

# Endpoint para obter a configuração atual da IA
@router.get("/config", response_model=Dict[str, Any])
async def get_ai_config(current_user: User = Depends(get_current_active_user)):
    """
    Obtém a configuração atual da IA.
    """
    try:
        config = load_ai_config()
        return config
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Erro ao obter configuração da IA: {str(e)}"
        )

# Endpoint para atualizar o prompt da IA
@router.post("/prompt", response_model=Dict[str, Any])
async def update_ai_prompt(
    data: Dict[str, str],
    current_user: User = Depends(get_current_active_user)
):
    """
    Atualiza o prompt da IA.
    """
    try:
        prompt = data.get("prompt")
        
        if not prompt:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Prompt é obrigatório"
            )
        
        # Carregar configuração atual
        config = load_ai_config()
        
        # Atualizar prompt
        config["prompt"] = prompt
        
        # Salvar configuração
        if not save_ai_config(config):
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Erro ao salvar configuração da IA"
            )
        
        return {"success": True, "message": "Prompt da IA atualizado com sucesso"}
    
    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Erro ao atualizar prompt da IA: {str(e)}"
        )

# Endpoint para atualizar os parâmetros da IA
@router.post("/parameters", response_model=Dict[str, Any])
async def update_ai_parameters(
    data: Dict[str, Any],
    current_user: User = Depends(get_current_active_user)
):
    """
    Atualiza os parâmetros da IA (temperatura, max_tokens).
    """
    try:
        temperature = data.get("temperature")
        max_tokens = data.get("max_tokens")
        
        if temperature is None or max_tokens is None:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Temperatura e max_tokens são obrigatórios"
            )
        
        # Validar valores
        if not (0 <= temperature <= 1):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Temperatura deve estar entre 0 e 1"
            )
        
        if not (50 <= max_tokens <= 500):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="max_tokens deve estar entre 50 e 500"
            )
        
        # Carregar configuração atual
        config = load_ai_config()
        
        # Atualizar parâmetros
        config["temperature"] = temperature
        config["max_tokens"] = max_tokens
        
        # Salvar configuração
        if not save_ai_config(config):
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Erro ao salvar configuração da IA"
            )
        
        return {"success": True, "message": "Parâmetros da IA atualizados com sucesso"}
    
    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Erro ao atualizar parâmetros da IA: {str(e)}"
        )
