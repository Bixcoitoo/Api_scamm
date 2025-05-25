document.addEventListener('DOMContentLoaded', function() {
    let btn = document.querySelector("#btn");
    let sidebar = document.querySelector(".sidebar");
    
    // Garante que a sidebar comece fechada
    sidebar.classList.remove("active");
    
    btn.onclick = function() {
        sidebar.classList.toggle("active");
    }
}); 