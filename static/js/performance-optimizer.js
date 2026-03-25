// Performance Optimization for CodePulse PWA
class PerformanceOptimizer {
  constructor() {
    this.init();
  }

  init() {
    console.log('⚡ Initializing performance optimizations...');
    
    // Enable performance monitoring
    this.enablePerformanceMonitoring();
    
    // Optimize images
    this.optimizeImages();
    
    // Enable lazy loading
    this.enableLazyLoading();
    
    // Optimize API calls
    this.optimizeAPICalls();
    
    // Enable caching
    this.enableCaching();
    
    // Reduce initial load time
    this.reduceLoadTime();
  }

  enablePerformanceMonitoring() {
    // Monitor Core Web Vitals
    if ('PerformanceObserver' in window) {
      const observer = new PerformanceObserver((list) => {
        for (const entry of list.getEntries()) {
          if (entry.entryType === 'largest-contentful-paint') {
            console.log('🎨 Largest Contentful Paint:', entry.startTime);
          }
          if (entry.entryType === 'first-input') {
            console.log('⚡ First Input Delay:', entry.processingStart - entry.startTime);
          }
          if (entry.entryType === 'layout-shift') {
            console.log('🔄 Cumulative Layout Shift:', entry.value);
          }
        }
      });

      observer.observe({ entryTypes: ['largest-contentful-paint', 'first-input', 'layout-shift'] });
    }

    // Monitor memory usage
    if ('memory' in performance) {
      setInterval(() => {
        const memory = performance.memory;
        console.log('💾 Memory Usage:', {
          used: Math.round(memory.usedJSHeapSize / 1048576) + ' MB',
          total: Math.round(memory.totalJSHeapSize / 1048576) + ' MB',
          limit: Math.round(memory.jsHeapSizeLimit / 1048576) + ' MB'
        });
      }, 10000); // Every 10 seconds
    }
  }

  optimizeImages() {
    // Add loading="lazy" to all images
    const images = document.querySelectorAll('img[data-src]');
    images.forEach(img => {
      img.loading = 'lazy';
    });

    // Preload critical images
    const criticalImages = document.querySelectorAll('img[data-critical="true"]');
    criticalImages.forEach(img => {
      const link = document.createElement('link');
      link.rel = 'preload';
      link.as = 'image';
      link.href = img.dataset.src;
      document.head.appendChild(link);
    });
  }

  enableLazyLoading() {
    // Intersection Observer for lazy loading
    if ('IntersectionObserver' in window) {
      const imageObserver = new IntersectionObserver((entries, observer) => {
        entries.forEach(entry => {
          if (entry.isIntersecting) {
            const img = entry.target;
            if (img.dataset.src) {
              img.src = img.dataset.src;
              img.removeAttribute('data-src');
              observer.unobserve(img);
            }
          }
        });
      });

      // Observe all images with data-src
      document.querySelectorAll('img[data-src]').forEach(img => {
        imageObserver.observe(img);
      });
    }
  }

  optimizeAPICalls() {
    // Request deduplication
    const pendingRequests = new Map();

    // Override fetch for API optimization
    const originalFetch = window.fetch;
    window.fetch = async (url, options = {}) => {
      // Only optimize API calls
      if (url.includes('/api/') || url.includes('github')) {
        const requestKey = `${url}_${JSON.stringify(options)}`;
        
        if (pendingRequests.has(requestKey)) {
          console.log('⏳ Request deduplicated:', url);
          return pendingRequests.get(requestKey);
        }

        const promise = originalFetch(url, options);
        pendingRequests.set(requestKey, promise);

        // Clean up after request completes
        promise.finally(() => {
          pendingRequests.delete(requestKey);
        });

        return promise;
      }

      return originalFetch(url, options);
    };
  }

  enableCaching() {
    // Cache API responses
    if ('caches' in window) {
      this.setupAPICache();
    }
  }

  setupAPICache() {
    const CACHE_NAME = 'codepulse-api-v1';
    const CACHE_DURATION = 5 * 60 * 1000; // 5 minutes

    self.addEventListener('fetch', event => {
      const request = event.request;
      
      // Only cache GET requests to our API
      if (request.method === 'GET' && request.url.includes('/api/')) {
        event.respondWith(
          caches.open(CACHE_NAME).then(cache => {
            return cache.match(request).then(response => {
              if (response && !this.isCacheExpired(response)) {
                console.log('📦 Serving from cache:', request.url);
                return response;
              }

              // Fetch from network and cache
              return fetch(request).then(networkResponse => {
                if (networkResponse.ok) {
                  const responseClone = networkResponse.clone();
                  cache.put(request, responseClone);
                }
                return networkResponse;
              });
            });
          })
        );
      }
    });
  }

  isCacheExpired(response) {
    const dateHeader = response.headers.get('date');
    if (!dateHeader) return true;
    
    const cacheDate = new Date(dateHeader);
    const now = new Date();
    const cacheAge = (now - cacheDate) / 1000; // Age in seconds
    
    return cacheAge > CACHE_DURATION;
  }

  reduceLoadTime() {
    // Minimize DOM operations
    let domUpdateTimer;
    const scheduleDOMUpdate = (callback) => {
      clearTimeout(domUpdateTimer);
      domUpdateTimer = setTimeout(callback, 16); // ~60fps
    };

    // Batch DOM reads
    const batchDOMReads = (callback) => {
      requestAnimationFrame(callback);
    };

    // Optimize critical rendering path
    this.optimizeCriticalRenderingPath();
  }

  optimizeCriticalRenderingPath() {
    // Inline critical CSS
    const criticalCSS = `
      body { font-family: 'Inter', sans-serif; }
      .loading { opacity: 0; transition: opacity 0.3s; }
      .loaded { opacity: 1; }
    `;
    
    const style = document.createElement('style');
    style.textContent = criticalCSS;
    document.head.appendChild(style);

    // Add loading states
    document.body.classList.add('loading');
    
    window.addEventListener('load', () => {
      document.body.classList.remove('loading');
      document.body.classList.add('loaded');
    });
  }

  // Preload critical resources
  preloadCriticalResources() {
    const criticalResources = [
      '/static/css/critical.css',
      '/static/js/critical.js',
      '/static/icons/icon-192x192.svg'
    ];

    criticalResources.forEach(resource => {
      const link = document.createElement('link');
      link.rel = 'preload';
      link.href = resource;
      
      if (resource.endsWith('.css')) {
        link.as = 'style';
      } else if (resource.endsWith('.js')) {
        link.as = 'script';
      } else if (resource.includes('icon')) {
        link.as = 'image';
      }
      
      document.head.appendChild(link);
    });
  }

  // Service Worker registration with retry logic
  registerServiceWorker() {
    if ('serviceWorker' in navigator) {
      let retries = 0;
      const maxRetries = 3;
      
      const registerSW = () => {
        navigator.serviceWorker.register('/static/service-worker.js')
          .then(registration => {
            console.log('✅ Service Worker registered:', registration.scope);
            
            // Check for updates
            registration.addEventListener('updatefound', () => {
              const newWorker = registration.installing;
              if (newWorker) {
                newWorker.addEventListener('statechange', () => {
                  if (newWorker.state === 'installed' && navigator.serviceWorker.controller) {
                    console.log('🔄 Service Worker updated');
                    this.showUpdateNotification();
                  }
                });
              }
            });
          })
          .catch(error => {
            retries++;
            console.error(`❌ Service Worker registration failed (attempt ${retries}):`, error);
            
            if (retries < maxRetries) {
              setTimeout(registerSW, 1000 * retries);
            } else {
              console.error('❌ Service Worker registration failed after all retries');
            }
          });
      };

      registerSW();
    }
  }

  showUpdateNotification() {
    const notification = document.createElement('div');
    notification.className = 'fixed top-4 right-4 bg-green-500 text-white px-6 py-3 rounded-lg shadow-lg z-50 flex items-center gap-2';
    notification.innerHTML = `
      <svg class="w-5 h-5" fill="currentColor" viewBox="0 0 20 20">
        <path d="M4 4v12a2 2 0 002 2h12a2 2 0 002-2V6a2 2 0 00-2-2H4a2 2 0 00-2 2zm2.293-7.707a1 1 0 011.414 0L9 10.586V3a1 1 0 112 0v7.586l2.293-2.293a1 1 0 011.414 1.414l-4 4a1 1 0 01-1.414 0l-4-4a1 1 0 010-1.414z"/>
      </svg>
      <span class="font-medium">App Updated!</span>
    `;
    
    notification.addEventListener('click', () => {
      notification.remove();
      window.location.reload();
    });
    
    document.body.appendChild(notification);
    
    setTimeout(() => {
      notification.remove();
    }, 5000);
  }
}

// Initialize performance optimizations when DOM is loaded
document.addEventListener('DOMContentLoaded', () => {
  window.performanceOptimizer = new PerformanceOptimizer();
  
  // Enable performance monitoring
  if (window.performanceOptimizer) {
    console.log('⚡ Performance optimizations loaded');
  }
});
