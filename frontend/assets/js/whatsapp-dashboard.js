/**
 * WhatsApp Dashboard - Componente para gerenciamento de conversas WhatsApp
 * Parte do sistema Zynapse
 */

document.addEventListener('alpine:init', () => {
  Alpine.data('whatsappDashboard', () => ({
    messages: [],
    conversations: {},
    stats: {
      totalMessages: 0,
      incomingMessages: 0,
      outgoingMessages: 0,
      activeConversations: 0,
      responseRate: 0,
      averageResponseTime: 0
    },
    loading: true,
    selectedPhone: '',
    sending: false,
    phone: '',
    message: '',
    currentConversation: null,
    showConversationView: false,
    searchTerm: '',
    dateFilter: 'all',
    
    init() {
      this.loadMessages();
      // Atualizar a cada 30 segundos
      setInterval(() => this.loadMessages(), 30000);
    },
    
    loadMessages() {
      this.loading = true;
      let url = '/api/v1/whatsapp/messages';
      if (this.selectedPhone) {
        url += `?phone=${this.selectedPhone}`;
      }
      
      // Simulação de dados para desenvolvimento
      setTimeout(() => {
        this.messages = this.getMockMessages();
        this.processConversations();
        this.calculateStats();
        this.loading = false;
      }, 500);
      
      // Código real para produção (comentado)
      /*
      fetch(url, {
        headers: { 'Authorization': `Bearer ${Alpine.store('auth').token}` }
      })
      .then(response => response.json())
      .then(data => {
        if (data.success) {
          this.messages = data.data;
          this.processConversations();
          this.calculateStats();
        }
      })
      .finally(() => {
        this.loading = false;
      });
      */
    },
    
    processConversations() {
      // Agrupar mensagens por número de telefone
      this.conversations = {};
      
      this.messages.forEach(msg => {
        if (!this.conversations[msg.phone]) {
          this.conversations[msg.phone] = {
            phone: msg.phone,
            messages: [],
            lastMessage: null,
            lastActivity: null,
            unread: 0
          };
        }
        
        this.conversations[msg.phone].messages.push(msg);
        
        // Atualizar última mensagem e atividade
        if (!this.conversations[msg.phone].lastActivity || 
            new Date(msg.created_at) > new Date(this.conversations[msg.phone].lastActivity)) {
          this.conversations[msg.phone].lastMessage = msg.message;
          this.conversations[msg.phone].lastActivity = msg.created_at;
          
          // Contar mensagens não lidas (apenas recebidas)
          if (msg.direction === 'incoming' && msg.status !== 'read') {
            this.conversations[msg.phone].unread++;
          }
        }
      });
      
      // Converter para array e ordenar por última atividade
      this.conversationList = Object.values(this.conversations).sort((a, b) => {
        return new Date(b.lastActivity) - new Date(a.lastActivity);
      });
    },
    
    calculateStats() {
      // Calcular estatísticas básicas
      this.stats.totalMessages = this.messages.length;
      this.stats.incomingMessages = this.messages.filter(m => m.direction === 'incoming').length;
      this.stats.outgoingMessages = this.messages.filter(m => m.direction === 'outgoing').length;
      this.stats.activeConversations = Object.keys(this.conversations).length;
      
      // Taxa de resposta (mensagens respondidas / mensagens recebidas)
      this.stats.responseRate = this.stats.incomingMessages > 0 
        ? Math.round((this.stats.outgoingMessages / this.stats.incomingMessages) * 100) 
        : 0;
      
      // Tempo médio de resposta (simulado)
      this.stats.averageResponseTime = '2m 30s';
    },
    
    openConversation(phone) {
      this.currentConversation = this.conversations[phone];
      this.showConversationView = true;
      this.phone = phone;
      
      // Marcar mensagens como lidas
      if (this.currentConversation) {
        this.currentConversation.unread = 0;
        
        // Em produção, enviar requisição para marcar como lidas
        /*
        fetch('/api/v1/whatsapp/mark-read', {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
            'Authorization': `Bearer ${Alpine.store('auth').token}`
          },
          body: JSON.stringify({ phone })
        });
        */
      }
    },
    
    closeConversation() {
      this.showConversationView = false;
      this.currentConversation = null;
    },
    
    sendMessage() {
      if (!this.phone || !this.message) {
        alert('Preencha o número de telefone e a mensagem');
        return;
      }
      
      this.sending = true;
      
      // Simulação para desenvolvimento
      setTimeout(() => {
        // Adicionar mensagem ao estado local
        const newMsg = {
          id: Date.now(),
          phone: this.phone,
          message: this.message,
          direction: 'outgoing',
          status: 'sent',
          created_at: new Date().toISOString()
        };
        
        this.messages.push(newMsg);
        this.processConversations();
        this.calculateStats();
        
        // Se estiver em uma conversa, atualizar
        if (this.currentConversation && this.currentConversation.phone === this.phone) {
          this.currentConversation.messages.push(newMsg);
        }
        
        this.message = '';
        this.sending = false;
      }, 1000);
      
      // Código real para produção (comentado)
      /*
      fetch('/api/v1/whatsapp/send-message', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${Alpine.store('auth').token}`
        },
        body: JSON.stringify({
          phone: this.phone,
          message: this.message
        })
      })
      .then(response => response.json())
      .then(data => {
        if (data.success) {
          this.message = '';
          this.loadMessages();
        } else {
          alert('Erro ao enviar mensagem: ' + data.message);
        }
      })
      .catch(error => {
        alert('Erro ao enviar mensagem: ' + error);
      })
      .finally(() => {
        this.sending = false;
      });
      */
    },
    
    formatDate(dateString) {
      const date = new Date(dateString);
      return date.toLocaleString();
    },
    
    formatPhone(phone) {
      // Formatar número de telefone para exibição
      if (!phone) return '';
      
      // Exemplo: 5511999999999 -> +55 (11) 99999-9999
      if (phone.length === 13) {
        return `+${phone.slice(0, 2)} (${phone.slice(2, 4)}) ${phone.slice(4, 9)}-${phone.slice(9)}`;
      }
      
      return phone;
    },
    
    // Dados de exemplo para desenvolvimento
    getMockMessages() {
      return [
        {
          id: 1,
          phone: '5511999999999',
          message: 'Olá, gostaria de saber mais sobre os serviços de automação.',
          direction: 'incoming',
          status: 'read',
          created_at: '2025-06-03T14:30:00Z'
        },
        {
          id: 2,
          phone: '5511999999999',
          message: 'Olá! Sou o assistente virtual da Zynapse. Temos soluções de automação para diversos segmentos. Em qual área você tem interesse?',
          direction: 'outgoing',
          status: 'delivered',
          created_at: '2025-06-03T14:32:00Z'
        },
        {
          id: 3,
          phone: '5511999999999',
          message: 'Estou interessado em automação para e-commerce.',
          direction: 'incoming',
          status: 'read',
          created_at: '2025-06-03T14:35:00Z'
        },
        {
          id: 4,
          phone: '5511999999999',
          message: 'Excelente escolha! Nossa solução para e-commerce inclui chatbots inteligentes, automação de atendimento e integração com plataformas como Shopify e WooCommerce. Gostaria de agendar uma demonstração?',
          direction: 'outgoing',
          status: 'delivered',
          created_at: '2025-06-03T14:37:00Z'
        },
        {
          id: 5,
          phone: '5511888888888',
          message: 'Bom dia, preciso de suporte técnico.',
          direction: 'incoming',
          status: 'read',
          created_at: '2025-06-04T09:15:00Z'
        },
        {
          id: 6,
          phone: '5511888888888',
          message: 'Bom dia! Sou o assistente virtual da Zynapse. Em que posso ajudar com suporte técnico hoje?',
          direction: 'outgoing',
          status: 'delivered',
          created_at: '2025-06-04T09:16:00Z'
        },
        {
          id: 7,
          phone: '5511777777777',
          message: 'Olá, vi o anúncio de vocês e gostaria de saber os preços.',
          direction: 'incoming',
          status: 'unread',
          created_at: '2025-06-04T10:45:00Z'
        }
      ];
    }
  }));
});
