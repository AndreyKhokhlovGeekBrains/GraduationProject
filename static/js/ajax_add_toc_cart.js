$(document).ready(function() {
    $('.image-container a').on('click', function(event) {
        event.preventDefault();
        var positionId = $(this).attr('href').split('=')[1];
        var amount = 1; // default amount is 1
        var url = '/cart/add/?position_id=' + positionId + '&amount=' + amount;

        $.ajax({
            type: 'POST',
            url: url,
            success: function(data) {
                console.log(data);
                updateCart(); // Обновляем корзину после успешного добавления
            },
            error: function(xhr, status, error) {
                console.error("Ошибка AJAX:", status, error);
            }
        });
    });
});

// Функция для обновления содержимого корзины
function updateCart() {
    $.ajax({
        type: 'GET',
        url: '/cart/get/',
        success: function(data) {
            $('#cart').html(data); // Обновляем содержимое элемента с ID cart
        },
        error: function(xhr, status, error) {
            console.error("Ошибка при обновлении корзины:", status, error);
        }
    });
}