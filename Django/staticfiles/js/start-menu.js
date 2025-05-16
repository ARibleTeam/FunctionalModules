const loadApp = (slug) => {
    const appLinks = document.querySelectorAll('.app-box');
    appLinks.forEach(link => link.classList.remove('active')); // снимаем выделение со всех

    const appBox = document.querySelector(`.app-box[data-slug="${slug}"]`);
    appBox.classList.add('active'); // подсвечиваем активное приложение

    window.location.href = `/chat/${slug}/`;
};