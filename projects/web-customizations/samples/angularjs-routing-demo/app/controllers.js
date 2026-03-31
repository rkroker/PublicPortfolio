app.controller('HomeController', function($scope) {
    $scope.message = "Welcome to my routing demo! Click the links to be routed to other pages!";
});

app.controller('ProjectsController', function($scope, ProjectService) {
    // Define the hardcoded projects
    $scope.projects = [
        { title: 'Hardcoded Project 1', description: 'First Hardcoded Project 1' },
        { title: 'Hardcoded Project 2', description: 'Second Hardcoded Project 2' }
    ];
    
    // Fetch the projects from projects.json and combine them with the hardcoded ones
    ProjectService.getProjects().then(function(response) {
        if (response.data && response.data.length > 0) {
            // Combine the hardcoded projects with the fetched projects
            $scope.projects = $scope.projects.concat(response.data);
        }
    }).catch(function(error) {
        console.error('Error fetching projects:', error);
    });
});



app.controller('ContactController', function($scope) {
    $scope.contactInfo = {
        name: '',
        email: '',
        message: ''
    };

    $scope.sendMessage = function() {
        alert("Message sent by " + $scope.contactInfo.name);
    };
});
