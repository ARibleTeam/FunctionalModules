const sidebar = document.getElementById('sidebar');
const toggleBtn = document.getElementById('toggleBtn');
const mainContent = document.getElementById('mainContent');
const pulsingBall = document.querySelector('.pulsing-ball');

const handleResize = () => {

    if (window.innerWidth <= 768) {
        pulsingBall.style.display = 'block';
        sidebar.classList.add('hidden');
        toggleBtn.style.display = 'block';
    } else {
        pulsingBall.style.display = 'none';  // Отображаем шар на более широких экранах
        sidebar.classList.remove('hidden');
        toggleBtn.style.display = 'none';
        mainContent.classList.remove('blurred');
    }
};

toggleBtn.addEventListener('click', function() {
    sidebar.classList.toggle('hidden');
    if (!sidebar.classList.contains('hidden')) {
        mainContent.classList.add('blurred');
    } else {
        mainContent.classList.remove('blurred');
    }
    pulsingBall.classList.add('hidden'); // Скрыть пульсирующий фон после первого клика
});

window.addEventListener('resize', handleResize);
window.addEventListener('load', handleResize);