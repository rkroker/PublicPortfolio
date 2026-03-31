app.controller('MyController', function($scope, NameService) {
    // Initialize the name variable from the service
    $scope.name = NameService.getName();
});
