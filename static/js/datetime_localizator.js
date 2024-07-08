document.addEventListener('htmx:afterRequest', function() {
    const timeStampElements = document.querySelectorAll('[data-timestamp]');

    timeStampElements.forEach(function(element) {
        const utcTimestamp = element.getAttribute('data-timestamp');
        if (utcTimestamp) {
            const localDate = new Date(utcTimestamp);

            const dateOptions = { year: 'numeric', month: '2-digit', day: '2-digit' };
            const timeOptions = { hour: '2-digit', minute: '2-digit' };
            
            const formattedDate = localDate.toLocaleDateString('ru', dateOptions);
            const formattedTime = localDate.toLocaleTimeString('ru', timeOptions);
            const weekDay = localDate.toLocaleDateString('ru', { weekday: 'short' });
            
            element.textContent = `${formattedTime} ${formattedDate}, ${weekDay}`;
        }
    });

});
