from fastapi import APIRouter, Depends, HTTPException, status
from typing import List, Dict, Any
import requests
import json
from datetime import datetime
from ..core.dependencies import get_current_active_user
from ..models.user import User
from ..core.config import settings
import os

router = APIRouter(
    prefix="/api/v1/whatsapp",
    tags=["whatsapp"],
    responses={404: {"description": "Not found"}},
)

# Simulação de banco de dados para conversas (em produção, use um banco de dados real)
conversations_db = {}

# Endpoint para listar todas as conversas
@router.get("/conversations", response_model=List[Dict[str, Any]])
async def list_conversations(current_user: User = Depends(get_current_active_user)):
    """
    Lista todas as conversas do WhatsApp.
    """
    try:
        # Em produção, isso seria uma chamada para o serviço do WhatsApp ou banco de dados
        # Por enquanto, vamos simular algumas conversas
        if not conversations_db:
            # Dados de exemplo se não houver conversas
            return [
                {
                    "phone": "5511987654321",
                    "name": "Cliente Exemplo",
                    "last_message": "Olá, gostaria de saber mais sobre os serviços.",
                    "timestamp": datetime.now().isoformat(),
                    "unread": 2
                },
                {
                    "phone": "5511912345678",
                    "name": "Empresa ABC",
                    "last_message": "Podemos agendar uma demonstração?",
                    "timestamp": (datetime.now().isoformat()),
                    "unread": 0
                }
            ]
        
        # Converter o dicionário de conversas em uma lista
        conversations = []
        for phone, data in conversations_db.items():
            messages = data.get("messages", [])
            last_message = messages[-1]["content"] if messages else ""
            
            conversations.append({
                "phone": phone,
                "name": data.get("name", "Desconhecido"),
                "last_message": last_message,
                "timestamp": messages[-1]["timestamp"] if messages else datetime.now().isoformat(),
                "unread": data.get("unread", 0)
            })
        
        return conversations
    
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Erro ao listar conversas: {str(e)}"
        )

# Endpoint para obter mensagens de uma conversa específica
@router.get("/conversations/{phone}/messages", response_model=List[Dict[str, Any]])
async def get_conversation_messages(
    phone: str,
    current_user: User = Depends(get_current_active_user)
):
    """
    Obtém todas as mensagens de uma conversa específica.
    """
    try:
        # Verificar se a conversa existe
        if phone not in conversations_db:
            # Se não existir, criar uma conversa vazia
            conversations_db[phone] = {
                "name": "Contato",
                "messages": [],
                "unread": 0
            }
            
            # Em produção, isso seria uma chamada para o serviço do WhatsApp
            # Por enquanto, vamos retornar algumas mensagens de exemplo
            return [
                {
                    "role": "user",
                    "content": "Olá, gostaria de saber mais sobre os serviços da Zynapse.",
                    "timestamp": (datetime.now().isoformat())
                },
                {
                    "role": "assistant",
                    "content": "Olá! Sou o assistente virtual da Zynapse. Oferecemos soluções de automação comercial com WhatsApp e IA. Como posso ajudar você hoje?",
                    "timestamp": (datetime.now().isoformat())
                }
            ]
        
        # Marcar mensagens como lidas
        conversations_db[phone]["unread"] = 0
        
        # Retornar mensagens
        return conversations_db[phone]["messages"]
    
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Erro ao obter mensagens: {str(e)}"
        )

# Endpoint para enviar uma mensagem
@router.post("/send", response_model=Dict[str, Any])
async def send_message(
    data: Dict[str, str],
    current_user: User = Depends(get_current_active_user)
):
    """
    Envia uma mensagem para um número de telefone.
    """
    try:
        phone = data.get("phone")
        message = data.get("message")
        
        if not phone or not message:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Número de telefone e mensagem são obrigatórios"
            )
        
        # Em produção, isso seria uma chamada para o serviço do WhatsApp
        # Por enquanto, vamos simular o envio
        
        # Verificar se a conversa existe
        if phone not in conversations_db:
            conversations_db[phone] = {
                "name": "Contato",
                "messages": [],
                "unread": 0
            }
        
        # Adicionar mensagem ao histórico
        conversations_db[phone]["messages"].append({
            "role": "assistant",
            "content": message,
            "timestamp": datetime.now().isoformat()
        })
        
        # Simular resposta do usuário (em produção, isso viria do webhook do WhatsApp)
        # Apenas para fins de demonstração
        conversations_db[phone]["messages"].append({
            "role": "user",
            "content": "Obrigado pela informação!",
            "timestamp": datetime.now().isoformat()
        })
        conversations_db[phone]["unread"] = 1
        
        return {"success": True, "message": "Mensagem enviada com sucesso"}
    
    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Erro ao enviar mensagem: {str(e)}"
        )

# Endpoint para limpar o histórico de uma conversa
@router.post("/conversations/{phone}/clear", response_model=Dict[str, Any])
async def clear_conversation(
    phone: str,
    current_user: User = Depends(get_current_active_user)
):
    """
    Limpa o histórico de uma conversa específica.
    """
    try:
        # Verificar se a conversa existe
        if phone not in conversations_db:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Conversa não encontrada"
            )
        
        # Limpar mensagens
        conversations_db[phone]["messages"] = []
        conversations_db[phone]["unread"] = 0
        
        # Em produção, isso seria uma chamada para o serviço do WhatsApp ou banco de dados
        
        return {"success": True, "message": "Histórico de conversa limpo com sucesso"}
    
    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Erro ao limpar conversa: {str(e)}"
        )
