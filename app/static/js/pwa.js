(function(){
  // Register Service Worker
  if ('serviceWorker' in navigator) {
    window.addEventListener('load', () => {
      navigator.serviceWorker.register('/sw.js')
        .then(reg => console.log('Service Worker registrado', reg.scope))
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
})();
