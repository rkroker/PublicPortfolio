<script>
/*
    MBA Attendance Monitor Custom Button Override
    ---------------------------------------------
    Purpose:
    Replace MBA's default "Mark as Notified and Print" button with a custom button
    that performs the following sequence:

    1. Removes unwanted MBA dropdown options:
       - "Mark as Notified and Print"
       - "Print Only"

    2. Replaces the main visible MBA button with a custom button:
       - "Select, Notify, and Open RC Builder"

    3. When clicked, the custom button:
       a. Finds and clicks MBA's built in "Make Current Selection" option
       b. Waits for MBA to finish processing
       c. Finds and clicks MBA's built in "Mark as Notified Only" option
       d. Waits again
       e. Redirects the user to RC Builder

    Why this approach works:
    We are not rebuilding MBA's logic ourselves.
    We are calling MBA's own built in actions by locating the matching buttons
    in the DOM and triggering their native click events.

    Notes:
    - This script assumes the MBA dropdown still contains:
        "Make Current Selection"
        "Mark as Notified Only"
    - This script intentionally removes:
        "Mark as Notified and Print"
        "Print Only"
    - The MutationObserver is used because MBA may redraw portions of the page
      after filtering, paging, or loading data.
*/

document.addEventListener('DOMContentLoaded', function () {

    function customizeMBAButtons() {

        /*
            These are the dropdown options we do NOT want users to see or click.
            They will be removed from the MBA dropdown menu if found.
        */
        var labelsToRemove = [
            'Mark as Notified and Print',
            'Print Only'
        ];

        /*
            Target page after MBA actions complete.
        */
        var targetUrl = '/admin/reports/rcBuilder/home.html';

        /*
            Based on page inspection, MBA renders the dropdown options inside:
            #rulesReport-mba-dropdown-menu
        */
        var menu = document.getElementById('rulesReport-mba-dropdown-menu');

        /*
            If the dropdown menu exists, loop through its button elements and
            remove any whose label matches one of the unwanted options.
        */
        if (menu) {
            menu.querySelectorAll('button').forEach(function (btn) {
                var text = btn.textContent.trim();

                if (labelsToRemove.includes(text)) {
                    btn.remove();
                }
            });
        }

        /*
            Find all buttons in the MBA grid header area.

            We are specifically looking for the visible main button with text:
            "Mark as Notified and Print"

            That is the button we want to replace with our own custom button.
        */
        var headerButtons = document.querySelectorAll('#rulesReport .mba-grid-header-row button');

        headerButtons.forEach(function (btn) {
            var text = btn.textContent.trim();

            if (text === 'Mark as Notified and Print') {

                /*
                    Prevent duplicate custom buttons.

                    Because MBA may redraw the page and this function may run again,
                    we first check whether our custom button already exists.
                    If it does, we remove the MBA button and stop here.
                */
                if (document.getElementById('custom-current-selection-button')) {
                    btn.remove();
                    return;
                }

                /*
                    Create the replacement custom button.
                */
                var newBtn = document.createElement('button');
                newBtn.id = 'custom-current-selection-button';
                newBtn.type = 'button';
                newBtn.textContent = 'Select, Notify, and Open RC Builder';
                newBtn.style.margin = '0px';

                /*
                    When the custom button is clicked, perform MBA's built in actions
                    in sequence, then redirect.
                */
                newBtn.addEventListener('click', function () {

                    /*
                        Re-locate the menu at click time.
                        This is safer than relying on the earlier reference because
                        MBA may have re-rendered the DOM since page load.
                    */
                    var menu = document.getElementById('rulesReport-mba-dropdown-menu');

                    if (!menu) {
                        alert('Could not find the MBA dropdown menu.');
                        return;
                    }

                    /*
                        Step 1:
                        Find MBA's "Make Current Selection" option by reading the
                        visible text of each dropdown button.
                    */
                    var matchSelect = Array.from(menu.querySelectorAll('button')).find(function (b) {
                        return b.textContent.trim() === 'Make Current Selection';
                    });

                    /*
                        Stop if that option cannot be found.
                    */
                    if (!matchSelect) {
                        alert('Could not find the Make Current Selection option.');
                        return;
                    }

                    /*
                        Trigger MBA's built in "Make Current Selection" behavior
                        exactly as if the user clicked it manually.
                    */
                    matchSelect.click();

                    /*
                        Wait briefly to allow MBA time to process the selection.
                        The delay can be increased if MBA responds slowly.
                    */
                    setTimeout(function () {

                        /*
                            Re-locate the dropdown menu again after the first action.

                            This is important because MBA may have refreshed or rebuilt
                            the DOM after "Make Current Selection" runs.
                        */
                        var menuAfterSelect = document.getElementById('rulesReport-mba-dropdown-menu');

                        if (!menuAfterSelect) {
                            alert('Could not find the MBA dropdown menu after making current selection.');
                            return;
                        }

                        /*
                            Step 2:
                            Find MBA's "Mark as Notified Only" option by label.
                        */
                        var matchNotify = Array.from(menuAfterSelect.querySelectorAll('button')).find(function (b) {
                            return b.textContent.trim() === 'Mark as Notified Only';
                        });

                        /*
                            Stop if the notify option cannot be found.
                        */
                        if (!matchNotify) {
                            alert('Could not find the Mark as Notified Only option.');
                            return;
                        }

                        /*
                            Trigger MBA's built in notification action.
                        */
                        matchNotify.click();

                        /*
                            Wait again to give MBA time to complete the notify action,
                            then redirect the user to RC Builder.
                        */
                        setTimeout(function () {
                            window.location.href = targetUrl;
                        }, 1000);

                    }, 1000);
                });

                /*
                    Insert the new custom button into the same location as the old one,
                    then remove the original MBA button.
                */
                btn.parentNode.insertBefore(newBtn, btn);
                btn.remove();
            }
        });
    }

    /*
        Run once on initial page load.
    */
    customizeMBAButtons();

    /*
        Watch for DOM changes and re-apply the customization if MBA redraws the page.

        This helps preserve the custom behavior across filtering, refreshing, paging,
        or other dynamic page updates.
    */
    var observer = new MutationObserver(customizeMBAButtons);
    observer.observe(document.body, {
        childList: true,
        subtree: true
    });
});
</script>