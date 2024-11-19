function onCartUpdate(event) {
    let product_id;
    let configuration_id;

    let request_path = event.detail.path;
    const request_target_str = event.detail.headers['HX-Target'].toString();
    const current_url = event.detail.headers['HX-Current-URL'];

    if (request_path.includes('/cart/add') || request_path.includes('/cart/remove')) {
        const cart_count = parseInt(document.querySelector('#cart_count').textContent);
        if (!current_url.includes('/cart')) {
            product_id = parseInt(request_target_str.match(/product(\d+)counter/)[1]);
            const selected_ram_button = document.querySelector('button[aria-selected=true][ram-config]');
            const selected_ssd_button = document.querySelector('button[aria-selected=true][ssd-config]');
            console.log(previousSelectedRamButton, previousSelectedSsdButton);
            const configuration = getCommonSetup(previousSelectedRamButton, previousSelectedSsdButton);
            configuration_id = configuration.id;

            console.log(`product_id: ${product_id} configuration_id: ${configuration_id}`);
        } else {
            product_id = parseInt(request_target_str.match(/product(\d+)counter/)[1]);
            configuration_id = parseInt(request_target_str.match(/product\d+counter(\d+)/)[1]);
        }

        // change counter value
        if (request_path.includes('/cart/add')) {
            document.querySelector('#cart_count').textContent = cart_count + 1;
        } else {
            document.querySelector('#cart_count').textContent = cart_count - 1;
        }

        request_path += '?configuration_id=' + configuration_id + '&product_id=' + product_id;
        event.detail.path = request_path;

    }
}

if (typeof(cartUpdateListeners) === 'undefined') { var cartUpdateListeners = new Array(); }
cartUpdateListeners.push(onCartUpdate);
cartUpdateListeners.forEach(listener => document.removeEventListener('htmx:configRequest', listener));
document.addEventListener('htmx:configRequest', onCartUpdate);

