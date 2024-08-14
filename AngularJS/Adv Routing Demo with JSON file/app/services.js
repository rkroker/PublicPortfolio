app.factory('ProjectService', function($http) {
    return {
        getProjects: function() {
            return $http.get('data/projects.json'); // Mock JSON file containing project details
        }
    };
});
