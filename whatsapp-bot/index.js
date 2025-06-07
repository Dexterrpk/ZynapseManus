const { Client, LocalAuth } = require('whatsapp-web.js');
const qrcode = require('qrcode-terminal');
const axios = require('axios');
const { generateAIResponse } = require('./ai-integration');

// Configuração do cliente WhatsApp
const client = new Client({
    authStrategy: new LocalAuth(),
    puppeteer: {
        args: ['--no-sandbox', '--disable-setuid-sandbox'],
    }
});

// Evento quando o QR code é recebido
client.on('qr', (qr) => {
    console.log('QR CODE RECEBIDO:');
    qrcode.generate(qr, { small: true });
    console.log('Escaneie o QR code acima com seu WhatsApp para fazer login');
});

// Evento quando o cliente está pronto
client.on('ready', () => {
    console.log('Cliente WhatsApp conectado com sucesso!');
    console.log('Bot Zynapse com IA está ativo e pronto para responder mensagens.');
});

// Evento para lidar com mensagens recebidas
client.on('message', async (message) => {
    // Ignorar mensagens de grupos
    if (message.isGroupMsg) return;
    
    const messageContent = message.body;
    const phoneNumber = message.from.split('@')[0]; // Extrai o número de telefone
    
    console.log(`Mensagem recebida de ${phoneNumber}: ${messageContent}`);
    
    try {
        // Gerar resposta usando a IA
        const aiResponse = await generateAIResponse(phoneNumber, messageContent);
        
        // Enviar resposta
        await message.reply(aiResponse);
        
        console.log(`Resposta enviada para ${phoneNumber}: ${aiResponse}`);
    } catch (error) {
        console.error('Erro ao processar mensagem:', error);
        
        // Resposta de fallback em caso de erro
        await message.reply('Desculpe, estou com dificuldades técnicas no momento. Por favor, tente novamente mais tarde.');
    }
});

// Evento para lidar com erros de autenticação
client.on('auth_failure', (msg) => {
    console.error('Falha na autenticação:', msg);
});

// Evento para lidar com desconexões
client.on('disconnected', (reason) => {
    console.log('Cliente desconectado:', reason);
    // Reiniciar o cliente
    client.initialize();
});

// Inicializar o cliente
client.initialize();
