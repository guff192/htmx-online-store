document.addEventListener('htmx:configRequest', function (event) {
    let request_path = event.detail.path;
    const request_target_str = event.detail.headers['HX-Target'].toString();
    const current_url = event.detail.headers['HX-Current-URL'];

    if (request_path.includes('/cart/add') || request_path.includes('/cart/remove')) {
        let product_id;
        let configuration_id;
        if (!current_url.includes('/cart')) {
            product_id = parseInt(request_target_str.match(/product(\d+)counter/)[1]);
            const selected_button = document.querySelector('button[aria-selected=true]');
            configuration_id = parseInt(selected_button.getAttribute('hx-get').match(/prices\/(\d+)/)[1]);

            console.log(selected_button);
            console.log(`product_id: ${product_id} configuration_id: ${configuration_id}`);
        } else {
            product_id = parseInt(request_target_str.match(/product(\d+)counter/)[1]);
            configuration_id = parseInt(request_target_str.match(/product\d+counter(\d+)/)[1]);
        }

        /*
        alert(configuration_id);
        alert(product_id);
        */

        request_path += '?configuration_id=' + configuration_id + '&product_id=' + product_id;
        event.detail.path = request_path;

    }
});

