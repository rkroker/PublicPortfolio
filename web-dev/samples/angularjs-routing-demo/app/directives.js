app.directive('projectCard', function() {
    return {
        restrict: 'E',
        scope: {
            project: '='
        },
        templateUrl: 'app/templates/project-card.html'  // Correct path to the template
    };
});
