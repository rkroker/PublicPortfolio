app.directive('taskList', function() {
    return {
        restrict: 'E',
        templateUrl: 'task-list-template.html',
        controller: 'TaskController'
    };
});
