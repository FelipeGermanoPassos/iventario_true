(function(){
  // Register Service Worker
  let swRegistration = null;

  if ('serviceWorker' in navigator) {
    window.addEventListener('load', () => {
      navigator.serviceWorker.register('/sw.js')
        .then(reg => {
          console.log('Service Worker registrado', reg.scope);
          swRegistration = reg;
          
          // Verifica se já tem permissão para notificações
          if (Notification.permission === 'granted') {
            console.log('Permissão de notificação já concedida');
          }
        })
        .catch(err => console.warn('SW falhou:', err));
    });
  }

  // Optional: handle install prompt
  let deferredPrompt;
  window.addEventListener('beforeinstallprompt', (e) => {
    e.preventDefault();
    deferredPrompt = e;
    console.log('PWA: pronto para instalar');
    // Exemplo: você pode exibir um botão "Instalar"
    // e chamar deferredPrompt.prompt() ao clicar
  });

  // ===== PUSH NOTIFICATIONS =====
  
  /**
   * Converte uma chave pública VAPID de base64 para Uint8Array
   */
  function urlBase64ToUint8Array(base64String) {
    const padding = '='.repeat((4 - base64String.length % 4) % 4);
    const base64 = (base64String + padding)
      .replace(/\-/g, '+')
      .replace(/_/g, '/');
    
    const rawData = window.atob(base64);
    const outputArray = new Uint8Array(rawData.length);
    
    for (let i = 0; i < rawData.length; ++i) {
      outputArray[i] = rawData.charCodeAt(i);
    }
    return outputArray;
  }

  /**
   * Solicita permissão para notificações push
   */
  async function requestNotificationPermission() {
    if (!('Notification' in window)) {
      console.warn('Este navegador não suporta notificações');
      return false;
    }

    if (!('PushManager' in window)) {
      console.warn('Este navegador não suporta push notifications');
      return false;
    }

    try {
      const permission = await Notification.requestPermission();
      
      if (permission === 'granted') {
        console.log('Permissão de notificação concedida');
        return true;
      } else {
        console.log('Permissão de notificação negada');
        return false;
      }
    } catch (error) {
      console.error('Erro ao solicitar permissão:', error);
      return false;
    }
  }

  /**
   * Subscreve o usuário para receber push notifications
   */
  async function subscribeToPush() {
    if (!swRegistration) {
      console.error('Service Worker não registrado');
      return false;
    }

    try {
      // Busca a chave pública VAPID do servidor
      const response = await fetch('/push/vapid-public-key');
      const data = await response.json();
      
      if (!data.publicKey) {
        console.error('Chave pública VAPID não disponível');
        return false;
      }

      const applicationServerKey = urlBase64ToUint8Array(data.publicKey);

      // Subscreve para push
      const subscription = await swRegistration.pushManager.subscribe({
        userVisibleOnly: true,
        applicationServerKey: applicationServerKey
      });

      console.log('Push subscription criada:', subscription);

      // Envia a subscrição para o servidor
      const saveResponse = await fetch('/push/subscribe', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json'
        },
        body: JSON.stringify({
          subscription: subscription.toJSON(),
          userAgent: navigator.userAgent
        })
      });

      const result = await saveResponse.json();
      
      if (result.success) {
        console.log('Subscrição salva com sucesso');
        return true;
      } else {
        console.error('Erro ao salvar subscrição:', result.error);
        return false;
      }

    } catch (error) {
      console.error('Erro ao subscrever para push:', error);
      return false;
    }
  }

  /**
   * Remove a subscrição de push notifications
   */
  async function unsubscribeFromPush() {
    if (!swRegistration) {
      return false;
    }

    try {
      const subscription = await swRegistration.pushManager.getSubscription();
      
      if (subscription) {
        // Remove do servidor
        await fetch('/push/unsubscribe', {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json'
          },
          body: JSON.stringify({
            endpoint: subscription.endpoint
          })
        });

        // Remove do navegador
        await subscription.unsubscribe();
        console.log('Push subscription removida');
        return true;
      }
      
      return false;
    } catch (error) {
      console.error('Erro ao remover subscrição:', error);
      return false;
    }
  }

  /**
   * Verifica se o usuário está subscrito
   */
  async function isPushSubscribed() {
    if (!swRegistration) {
      return false;
    }

    try {
      const subscription = await swRegistration.pushManager.getSubscription();
      return subscription !== null;
    } catch (error) {
      console.error('Erro ao verificar subscrição:', error);
      return false;
    }
  }

  /**
   * Inicializa as notificações push (solicita permissão e subscreve)
   */
  async function initializePushNotifications() {
    const hasPermission = await requestNotificationPermission();
    
    if (hasPermission) {
      const isSubscribed = await isPushSubscribed();
      
      if (!isSubscribed) {
        await subscribeToPush();
      } else {
        console.log('Usuário já está subscrito para push notifications');
      }
    }
  }

  // Expõe funções globalmente para uso em outras partes do app
  window.PushNotifications = {
    requestPermission: requestNotificationPermission,
    subscribe: subscribeToPush,
    unsubscribe: unsubscribeFromPush,
    isSubscribed: isPushSubscribed,
    initialize: initializePushNotifications
  };

})();
