document.addEventListener('DOMContentLoaded', async function() {
    try {
        const response = await fetch('/components/footer.html');
        const footerHtml = await response.text();
        
        // Insere o footer antes do fechamento do body
        document.body.insertAdjacentHTML('beforeend', footerHtml);
    } catch (error) {
        console.error('Erro ao carregar o footer:', error);
    }
}); 