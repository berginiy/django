document.getElementById('purchase-form').onsubmit = async function(event) {
    event.preventDefault(); // предотвращаем обычное поведение формы

    const apiPurchaseUrl = this.dataset.apiPurchaseUrl; // Получаем URL из атрибута data
    const response = await fetch(apiPurchaseUrl, {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
            'X-CSRFToken': '{{ csrf_token }}' // добавляем CSRF-токен для безопасности
        },
        body: JSON.stringify({
            // если нужно передать дополнительные данные, добавьте их сюда
        })
    });

    if (response.ok) {
        // если запрос успешен, перенаправляем на страницу успешной покупки
        window.location.href = "/purchase_success/";
    } else {
        // обработка ошибок
        console.error('Произошла ошибка при оформлении заказа.');
    }
};
