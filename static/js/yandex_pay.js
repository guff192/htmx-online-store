function onYaPayLoad() {
    const YaPay = window.YaPay;

    // Данные платежа
    const paymentData = {
        // Для отладки нужно явно указать `SANDBOX` окружение,
        // для продакшена параметр можно убрать или указать `PRODUCTION`
        env: YaPay.PaymentEnv.Sandbox,

        // Версия 4 указывает на тип оплаты сервисом Яндекс Пэй
        // Пользователь производит оплату на форме Яндекс Пэй,
        // и мерчанту возвращается только результат проведения оплаты
        version: 4,

        // Код валюты в которой будете принимать платежи
        currencyCode: YaPay.CurrencyCode.Rub,

        // Идентификатор продавца, который получают при регистрации в Яндекс Пэй
        merchantId: '<YOUR_MERCHANT_ID>',

        // Сумма к оплате
        // Сумма которая будет отображена на форме зависит от суммы переданной от бэкенда
        // Эта сумма влияет на отображение доступности Сплита
        totalAmount: '15980.00',

        // Доступные для использования методы оплаты
        // Доступные на форме способы оплаты также зависят от информации переданной от бэкенда
        // Данные передаваемые тут влияют на внешний вид кнопки или виджета
        availablePaymentMethods: ['CARD', 'SPLIT'],
    };

    // Обработчик на клик по кнопке
    // Функция должна возвращать промис которые резолвит ссылку на оплату полученную от бэкенда Яндекс Пэй
    // Подробнее про создание заказа: https://pay.yandex.ru/ru/docs/custom/backend/yandex-pay-api/order/merchant_v1_orders-post
    async function onPayButtonClick() {
        // Создание заказа...
        // и возврат URL на оплату вида 'https://pay.ya.ru/l/XXXXXX'
    }

    // Обработчик на ошибки при открытии формы оплаты
    function onFormOpenError(reason) {
        // Выводим информацию о недоступности оплаты в данный момент
        // и предлагаем пользователю другой способ оплаты.
        console.error(`Payment error — ${reason}`);
    }

    // Создаем платежную сессию
    YaPay.createSession(paymentData, {
        onPayButtonClick: onPayButtonClick,
        onFormOpenError: onFormOpenError,
    })
        .then(function (paymentSession) {
            // Показываем кнопку Яндекс Пэй на странице.
            paymentSession.mountButton(document.querySelector('#button_container'), {
                type: YaPay.ButtonType.Pay,
                theme: YaPay.ButtonTheme.Black,
                width: YaPay.ButtonWidth.Auto,
            });
        })
        .catch(function (err) {
            // Не получилось создать платежную сессию.
        });
}


