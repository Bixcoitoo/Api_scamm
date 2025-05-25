// Middleware de autenticação
(async function() {
    const protectedRoutes = ['/pages/main.html', '/pages/profile.html'];
    const currentPath = window.location.pathname;
    
    if (protectedRoutes.some(route => currentPath.includes(route))) {
        document.documentElement.style.display = 'none';
        
        await new Promise((resolve) => {
            const unsubscribe = auth.onAuthStateChanged((user) => {
                if (user) {
                    // Verifica token tanto no localStorage quanto no sessionStorage
                    const token = localStorage.getItem('authToken') || sessionStorage.getItem('authToken');
                    if (token) {
                        console.log('✅ Usuário autenticado');
                        document.documentElement.style.display = 'block';
                    } else {
                        window.location.replace('/pages/404.html');
                    }
                } else {
                    window.location.replace('/pages/404.html');
                }
                unsubscribe();
                resolve();
            });
        });
    }
})(); 