/* jQuery full build: the slim distribution does not include AJAX. */
$(function () {
    $('.toggle-details').on('click', function () {
        const expanded = $(this).attr('aria-expanded') === 'true';
        $('#' + $(this).attr('aria-controls')).prop('hidden', expanded);
        $(this).attr('aria-expanded', String(!expanded)).text(expanded ? 'Show details' : 'Hide details');
    });
    let generation = 0;
    let pending;
    const status = $('#availability');
    $('#booking-form :input').on('input change', function () {
        generation += 1;
        if (pending) pending.abort();
        status.text('Values changed. Check availability again.');
        $('#check-availability').prop('disabled', false);
    });
    $('#check-availability').on('click', function () {
        const token = ++generation;
        const button = $(this).prop('disabled', true);
        status.text('Checking…');
        pending = $.ajax({
            url: $('#booking-form').data('availability-url'), dataType: 'json', timeout: 10000,
            data: {space: $('#id_space').val(), start: $('#id_start').val(), end: $('#id_end').val()}
        }).done(function (data) {
            if (token === generation) status.text(data.available ? 'Available — saving checks again.' : 'Already booked.');
        }).fail(function (xhr, reason) {
            if (token === generation && reason !== 'abort') status.text(xhr.status === 400 ? 'Choose a space and a valid interval of at most 12 hours.' : 'Could not check availability. Please retry.');
        }).always(function () { if (token === generation) button.prop('disabled', false); });
    });
});
