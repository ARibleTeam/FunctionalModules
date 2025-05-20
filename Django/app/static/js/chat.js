document.addEventListener('DOMContentLoaded', function() {
    const sendBtn = document.getElementById('sendBtn');
    const chatMessageInput = document.getElementById('chatMessageInput');
    const messagesContainer = document.getElementById('messagesContainer');
    const csrfToken = document.querySelector('meta[name="csrf-token"]').getAttribute('content'); // Получаем CSRF токен
    const app_name = document.querySelector('meta[name="app_name"]').getAttribute('content');
    const app_type = document.querySelector('meta[name="app_type"]').getAttribute('content');
    const app_slug = document.querySelector('meta[name="app_slug"]').getAttribute('content');
    const app_hello_message = document.querySelector('meta[name="app_hello_message"]').getAttribute('content');
    const chatTitle = document.getElementById('chatTitle');  // Получаем элемент <h2> по id
    const fileInput = document.getElementById('fileInput');
    const fileNameDisplay = document.getElementById('fileName');

    let isError = false;
    let blockInput = true;

    const wsHost = window.location.hostname;
    let socket; // Используем let вместо const, чтобы можно было переприсваивать

    // Функция для создания и настройки WebSocket соединения
    function connectWebSocket() {
        socket = new WebSocket(`ws://${wsHost}:8001/ws/messages`);

        socket.onopen = () => {
            removeWaitingMessage();

            // Отправка сообщения после установки соединения
            const message = {
                app_slug: app_slug,
            };
            socket.send(JSON.stringify(message));

            addWaitingMessage();
        };

        socket.onmessage = (event) => {
            const data = JSON.parse(event.data);
            if (data.status == "error") {
                removeWaitingMessage();
                blockInput = true;
                addMessageToChat(data.output + " Перезагрузите страницу или выберите другой модуль!", 'incoming');
                isError = true;
            }
            if (data.status == "received") {
                removeWaitingMessage();
                addMessageToChat(data.output, 'incoming');
                blockInput = false;
            }
            if (data.status == "file") {
                removeWaitingMessage();
                addFileToChat(data.file_name, 'incoming');
                blockInput = true;
            }
        };

        socket.onclose = (event) => {
            blockInput = true;
            
            // Пытаемся переподключиться через 3 секунды
            if (isError == false) {
                addWaitingMessage();
                setTimeout(connectWebSocket, 3000);
            }
        };

        socket.onerror = (error) => {
            socket.close(); // Это вызовет onclose, где уже есть логика переподключения
        };
    }

    function sendSocketMessage(messageText) {
        if (socket.readyState === WebSocket.OPEN) {
            const message = {
                value: messageText,
                status: "input",
            };
            socket.send(JSON.stringify(message));
            blockInput = true;
        }
    }

    // Прокрутка страницы в самый низ при загрузке
    function scrollPageToBottom() {
        window.scrollTo({
            top: document.body.scrollHeight,
            behavior: 'smooth' // Плавная прокрутка
        });
    }

    addMessageToChat(app_hello_message, 'incoming');
    // Инициализируем первое соединение
    connectWebSocket();
    // Вызываем сразу и с небольшой задержкой для надёжности
    scrollPageToBottom();
    setTimeout(scrollPageToBottom, 100);

    
    if (fileInput) {
        fileInput.addEventListener('change', function () {
            if (fileInput.files.length > 0) {
                fileNameDisplay.textContent = "Выбран файл: " + fileInput.files[0].name;
            } else {
                fileNameDisplay.textContent = 'Прикрепите файл';
            }
        });
    }


    sendBtn.addEventListener('click', function() {

        if (blockInput) {
            return
        }

        // пупупупупупуппупу
        if ((app_type == 'file2file' || app_type == 'file2text') && fileInput.files.length > 0) {

            if (chatTitle) {
                chatTitle.remove(); // Удаляем элемент <h2>
            }
            
            // Затем начинаем отправку
            sendMessageWithFile(fileInput, app_name, csrfToken)
            .then(data => {
                if (data.success) {
                    blockInput = true;
                    
                    fileInput.value = ''; // убираем выбранный файл
                    fileNameDisplay.textContent = 'Прикрепите файл';

                    // Добавляем исходящий файл в чат
                    addFileToChat(data.response, 'outgoing');
        
                    // Показываем "ожидание" (например, спиннер)
                    addWaitingMessage();
        
                    // отправляем название файла на сервер
                    const message = {
                        value: data.response,
                        status: "input",
                    };
                    socket.send(JSON.stringify(message));
        
                } else {
                    removeWaitingMessage();
                    addMessageToChat("Ошибка при отправке файла", 'incoming');
                }
            })
            .catch(error => {
                removeWaitingMessage();
                addMessageToChat(`Ошибка: ${error.message}`, 'incoming');
            });
        
            
            return;
        }
        
        const message = chatMessageInput.value.trim();

        if (message == "") {
            return
        }

        blockInput = true;

        // Обработка обычных текстовых сообщений
        addMessageToChat(message, 'outgoing');
        chatMessageInput.value = '';
        
        if (chatTitle) {
            chatTitle.remove();
        }

        addWaitingMessage();
        sendSocketMessage(message);
        
    });

    // тут надо будет смотреть на содержание в респонсе ошибок. Если есть, что отправить смс а не файл.
    function addFileToChat(response, type) {

        const messageDiv = document.createElement('div');
        messageDiv.classList.add('message', type);
        const fileExtension = response.split('.').pop().toLowerCase();

        // Проверяем, является ли файл изображением
        const isImage = ['png', 'jpg', 'jpeg'].includes(fileExtension);

        if (isImage) {
            // Показываем само изображение
            const img = document.createElement('img');
            img.src = "/download/" + response;
            img.alt = "Изображение";
            img.classList.add('chat-image'); // Можно задать стили
        
            // Оборачиваем в ссылку для скачивания
            const imageLink = document.createElement('a');
            imageLink.href = "/download/" + response;
            imageLink.download = response;
        
            imageLink.appendChild(img);
            messageDiv.appendChild(imageLink);
        } else {
            // Обычная иконка файла
            const fileLink = document.createElement('a');
            fileLink.href = "/download/" + response;
            fileLink.download = response;
        
            const fileIcon = document.createElement('img');
            fileIcon.src = "https://cdn-icons-png.flaticon.com/512/1092/1092004.png";
            fileIcon.alt = "Файл";
            fileIcon.classList.add('file-icon');
            fileIcon.style.width = '30px';
            fileIcon.style.height = '30px';
        
            fileLink.appendChild(fileIcon);
            messageDiv.appendChild(fileLink);
        }
        messagesContainer.appendChild(messageDiv);
        setTimeout(scrollPageToBottom, 100);
        return
    }

    // Функция для добавления сообщения в чат
    function addMessageToChat(message, type) {
      
        const messageDiv = document.createElement('div');
        messageDiv.classList.add('message', type); // Добавляем класс для типа сообщения
        messageDiv.innerText = message;
        messagesContainer.appendChild(messageDiv);

        setTimeout(scrollPageToBottom, 100);
    }

    // Функция для добавления сообщения "Ожидание ответа"
    function addWaitingMessage() {
        blockInput = true;
        const waitingMessageDiv = document.createElement('div');
        waitingMessageDiv.id = 'waitingMessage';
    
        // Создаём элемент изображения
        const loadingGif = document.createElement('img');
        loadingGif.src = loadingGifPath; // Теперь используется правильный путь
        loadingGif.alt = 'Загрузка...';
        loadingGif.style.width = '25px';
        loadingGif.style.height = '25px';
    
        // Вставляем гифку внутрь блока
        waitingMessageDiv.appendChild(loadingGif);
    
        // Добавляем блок в контейнер
        messagesContainer.appendChild(waitingMessageDiv);
    
        // Прокрутка вниз
        setTimeout(scrollPageToBottom, 100);
    }
    
    function sendMessageWithFile(fileInput, app_name, csrfToken) {
        const formData = new FormData();
    
        // Добавляем файл, если он выбран
        if (fileInput.files.length > 0) {
            const file = fileInput.files[0];
            formData.append('file', file);
        }
    
        // Добавляем другие данные
        formData.append('app_name', app_name);
    
        // Отправляем запрос на сервер
        return fetch('/upload/', {
            method: 'POST',
            headers: {
                'X-CSRFToken': csrfToken,
            },
            body: formData,
        })
        .then(response => response.json())
        .then(data => {
            return data; // Возвращаем результат
        })
        .catch(error => {
            throw new Error('Ошибка отправки сообщения');
        });
    }

    function removeWaitingMessage() {
        if (document.getElementById('waitingMessage')) {
            const waitingMessage = document.getElementById('waitingMessage');
        
            // Удаляем сообщение об ожидании
            messagesContainer.removeChild(waitingMessage);
        }
    }

});
