var app = angular.module('taskManagerApp', []);

// Application Configuration
app.config(function($sceProvider) {
    // Disable SCE for demonstration purposes
    $sceProvider.enabled(false);
});
