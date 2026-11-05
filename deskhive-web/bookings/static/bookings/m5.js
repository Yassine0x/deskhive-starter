/* M5 lab 3: use the supplied local jQuery full build. */
$(function () {
    $('.toggle-details').on('click', function () {
        var $toggle = $(this);
        var $details = $('#' + $toggle.attr('aria-controls'));
        var opening = $details.prop('hidden');
        $details.prop('hidden', !opening);
        $toggle.attr('aria-expanded', opening ? 'true' : 'false');
        $toggle.text(opening ? 'Hide details' : 'Show details');
    });

    var $form = $('#booking-form');
    var $check = $('#check-availability');
    var $status = $('#availability');
    var generation = 0;
    var pending = null;

    function abortPending() {
        if (pending) {
            pending.abort();
            pending = null;
        }
    }

    // Any change makes the previous result obsolete.
    $('#id_space, #id_start, #id_end').on('input change', function () {
        generation += 1;
        abortPending();
        $check.prop('disabled', false);
        $status.text('Values changed. Check availability again.');
    });

    $check.on('click', function () {
        generation += 1;
        var current = generation;
        abortPending();
        $check.prop('disabled', true);
        $status.text('Checking…');
        pending = $.ajax({
            url: $form.data('availability-url'),
            type: 'GET',
            dataType: 'json',
            timeout: 8000,
            data: {
                space: $('#id_space').val(),
                start: $('#id_start').val(),
                end: $('#id_end').val()
            }
        }).done(function (data) {
            if (current !== generation) { return; }
            $status.text(data.available ? 'Available — saving checks again.' : 'Already booked.');
        }).fail(function (xhr, textStatus) {
            if (current !== generation || textStatus === 'abort') { return; }
            $status.text(xhr.status === 400
                ? 'Choose a space and a valid interval of at most 12 hours.'
                : 'Could not check availability. Please retry.');
        }).always(function () {
            // Only the request for the current values may restore the button.
            if (current !== generation) { return; }
            pending = null;
            $check.prop('disabled', false);
        });
    });
});
