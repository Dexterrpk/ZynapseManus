const axios = require('axios');
const fs = require('fs');
const path = require('path');
const dotenv = require('dotenv');

// Carrega variáveis do .env da raiz do projeto
dotenv.config({ path: path.join(__dirname, '..', '.env') });

const apiKey = process.env.OPENAI_API_KEY; // Você pode manter esse nome com a chave Groq

if (!apiKey) {
  console.error('Erro: OPENAI_API_KEY não encontrada no arquivo .env');
  process.exit(1);
}

const conversations = {}; // Histórico de conversa por número de telefone

/**
 * Gera resposta da IA usando a API da Groq (LLaMA 3)
 */
async function generateAIResponse(phone, message) {
  try {
    // Inicializa histórico, se não existir
    if (!conversations[phone]) {
      conversations[phone] = [];
    }

    // Adiciona nova mensagem ao histórico
    conversations[phone].push({ role: 'user', content: message });

    // Limita o histórico a no máximo 10 mensagens
    if (conversations[phone].length > 10) {
      conversations[phone] = conversations[phone].slice(-10);
    }

    // Mensagens a serem enviadas para a IA
    const messages = [
      {
        role: 'system',
        content: 'Você é Dexter, o assistente virtual da Zynapse, uma plataforma de automação de atendimento via WhatsApp. Fale com cordialidade, clareza e profissionalismo. Mantenha as respostas curtas (3 a 4 frases). Use uma linguagem humanizada, pode ser engraçado as vezes, com leve toque informal, e emoji quando apropriado. Você oferece ajuda com: Informações sobre o sistema Zynapse, Ativação do bot para empresas, Zynapse está localizada em Santo Antônio de Jesus, BA. Quando não souber algo, ofereça ajuda para falar com um atendente humano. iNFORMAÇÕES UTEIS: SITE https://zinapseapp.netlify.app, Dev Cleiton Neri; Dê uma olhada no site pra conhecer mais e passar no atendimento '
      },
      ...conversations[phone]
    ];

    // Chamada à API da Groq
    const response = await axios.post(
      'https://api.groq.com/openai/v1/chat/completions',
      {
        model: 'llama3-70b-8192',
        messages: messages,
        max_tokens: 150,
        temperature: 0.7
      },
      {
        headers: {
          Authorization: `Bearer ${apiKey}`,
          'Content-Type': 'application/json'
        }
      }
    );

    const aiResponse = response.data.choices[0].message.content.trim();

    // Adiciona resposta da IA ao histórico
    conversations[phone].push({ role: 'assistant', content: aiResponse });

    // Log no terminal
    console.log(`[${new Date().toISOString()}] Conversa com ${phone}:`);
    console.log(`Usuário: ${message}`);
    console.log(`IA: ${aiResponse}`);

    return aiResponse;

  } catch (error) {
    console.error('Erro ao gerar resposta da IA:', error.message || error);
    if (error.response) {
      console.error(error.response.status, error.response.data);
    }

    return 'Desculpe, estou com dificuldades para processar sua solicitação no momento. Por favor, tente novamente mais tarde ou entre em contato com nosso suporte.';
  }
}

/**
 * Limpa o histórico de conversa de um número
 */
function clearConversationHistory(phone) {
  if (conversations[phone]) {
    conversations[phone] = [];
    return true;
  }
  return false;
}

module.exports = {
  generateAIResponse,
  clearConversationHistory
};
