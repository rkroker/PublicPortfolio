app.controller('TaskController', function($scope, TaskService) {
    $scope.tasks = TaskService.getTasks();
    $scope.newTask = {};

    $scope.addTask = function() {
        if ($scope.newTask.title) {
            TaskService.addTask($scope.newTask);
            $scope.newTask = {}; // Reset the form
        }
    };

    $scope.editTask = function(task) {
        task.isEditing = true;
    };

    $scope.saveTask = function(task) {
        task.isEditing = false;
    };

    $scope.deleteTask = function(task) {
        TaskService.deleteTask(task);
    };
});
