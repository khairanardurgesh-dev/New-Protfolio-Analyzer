// PWA Install Handler for CodePulse
class PWAInstaller {
  constructor() {
    this.deferredPrompt = null;
    this.installButton = null;
    this.init();
  }

  init() {
    // Listen for beforeinstallprompt event
    window.addEventListener('beforeinstallprompt', (e) => {
      console.log('📱 Install prompt detected');
      e.preventDefault();
      this.deferredPrompt = e;
      this.showInstallButton();
    });

    // Listen for app installed event
    window.addEventListener('appinstalled', (e) => {
      console.log('✅ App installed successfully');
      this.hideInstallButton();
      this.showInstallSuccess();
    });

    // Check if app is already installed
    if (window.matchMedia('(display-mode: standalone)').matches) {
      console.log('📱 App is already installed');
      this.hideInstallButton();
    }
  }

  showInstallButton() {
    // Remove existing button if any
    if (this.installButton) {
      this.installButton.remove();
    }

    // Create install button
    this.installButton = document.createElement('div');
    this.installButton.className = 'fixed bottom-4 right-4 bg-gradient-to-r from-blue-600 to-purple-600 text-white px-6 py-3 rounded-lg shadow-lg cursor-pointer transform transition-all duration-300 hover:scale-105 z-50 flex items-center gap-2';
    this.installButton.innerHTML = `
      <svg class="w-5 h-5" fill="currentColor" viewBox="0 0 20 20">
        <path d="M3 17a1 1 0 011-1h12a1 1 0 110 2H4a1 1 0 01-1-1zm3.293-7.707a1 1 0 011.414 0L9 10.586V3a1 1 0 112 0v7.586l2.293-2.293a1 1 0 011.414 1.414l-4 4a1 1 0 01-1.414 0l-4-4a1 1 0 010-1.414z"/>
      </svg>
      <span class="font-medium">Install CodePulse</span>
    `;
    
    this.installButton.addEventListener('click', () => this.installApp());
    document.body.appendChild(this.installButton);
  }

  hideInstallButton() {
    if (this.installButton) {
      this.installButton.remove();
      this.installButton = null;
    }
  }

  async installApp() {
    if (!this.deferredPrompt) {
      console.log('❌ Install prompt not available');
      return;
    }

    console.log('📱 Showing install prompt');
    this.deferredPrompt.prompt();
    
    const { outcome } = await this.deferredPrompt.userChoice;
    console.log('📱 Install outcome:', outcome);
    
    if (outcome === 'accepted') {
      console.log('✅ User accepted install');
      this.hideInstallButton();
    }
    
    this.deferredPrompt = null;
  }

  showInstallSuccess() {
    // Show success notification
    const successDiv = document.createElement('div');
    successDiv.className = 'fixed top-4 right-4 bg-green-500 text-white px-6 py-3 rounded-lg shadow-lg z-50 flex items-center gap-2';
    successDiv.innerHTML = `
      <svg class="w-5 h-5" fill="currentColor" viewBox="0 0 20 20">
        <path fill-rule="evenodd" d="M16.707 5.293a1 1 0 010 1.414l-8 8a1 1 0 01-1.414 0l-4-4a1 1 0 011.414-1.414L8.586 10H3a1 1 0 110-2h5.586l4.293-4.293a1 1 0 010 1.414z" clip-rule="evenodd"/>
      </svg>
      <span class="font-medium">Successfully Installed!</span>
    `;
    
    document.body.appendChild(successDiv);
    
    setTimeout(() => {
      successDiv.remove();
    }, 3000);
  }

  // Check for PWA features
  checkPWAFeatures() {
    const features = {
      standalone: window.matchMedia('(display-mode: standalone)').matches,
      installed: !!window.navigator.standalone,
      serviceWorker: 'serviceWorker' in navigator,
      pushManager: !!window.PushManager,
      syncManager: !!window.SyncManager
    };
    
    console.log('🔧 PWA Features:', features);
    return features;
  }
}

// Initialize PWA installer when DOM is loaded
document.addEventListener('DOMContentLoaded', () => {
  window.pwaInstaller = new PWAInstaller();
  
  // Check PWA features
  const features = window.pwaInstaller.checkPWAFeatures();
  
  // Show install button only if not installed
  if (!features.standalone && !features.installed) {
    console.log('📱 App not installed - showing install button');
  }
});

// Handle online/offline status
window.addEventListener('online', () => {
  console.log('🌐 App is online');
  document.body.classList.remove('offline-mode');
});

window.addEventListener('offline', () => {
  console.log('📵 App is offline');
  document.body.classList.add('offline-mode');
  
  // Show offline notification
  const offlineDiv = document.createElement('div');
  offlineDiv.className = 'fixed top-4 left-4 bg-yellow-500 text-black px-6 py-3 rounded-lg shadow-lg z-50 flex items-center gap-2';
  offlineDiv.innerHTML = `
    <svg class="w-5 h-5" fill="currentColor" viewBox="0 0 20 20">
      <path fill-rule="evenodd" d="M8.111 2.554a1 1 0 01.916.558l7.425 4.84a1 1 0 011.418 1.144l-4.16 4.223a1 1 0 01-1.05.042l-4.5-4.25a1 1 0 01-.032-1.418L8.111 2.554zM15 8.5a1 1 0 100 2 1 1 0 000-2z" clip-rule="evenodd"/>
    </svg>
    <span class="font-medium">You're offline. Some features may be limited.</span>
  `;
  
  document.body.appendChild(offlineDiv);
  
  window.addEventListener('online', () => {
    offlineDiv.remove();
  }, { once: true });
});
