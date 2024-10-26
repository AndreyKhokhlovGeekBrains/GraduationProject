  document.querySelectorAll('.add-to-cart').forEach(button => {
    button.addEventListener('click', function() {
      const itemId = this.getAttribute('data-item-id');
      fetch(`/add-offer/?item_id=${itemId}`, {
        method: 'POST', // или 'GET', в зависимости от вашего сервера
        headers: {
          'Content-Type': 'application/json',
          // Добавьте другие заголовки, если необходимо, например, для авторизации
        },
        body: JSON.stringify({}) // Если нужно отправить дополнительные данные
      })
      .then(response => response.json())
      .then(data => {
        // Обработка ответа от сервера
        console.log(data);
        alert('Товар добавлен в корзину!');
      })
      .catch((error) => {
        console.error('Ошибка:', error);
      });
    });
  });