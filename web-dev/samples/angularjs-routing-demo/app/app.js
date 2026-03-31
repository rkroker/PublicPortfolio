var app = angular.module('portfolioApp', ['ngRoute']);

app.config(function($routeProvider) {
    $routeProvider
        .when('/', {
            templateUrl: 'app/templates/home.html',
            controller: 'HomeController'
        })
        .when('/projects', {
            templateUrl: 'app/templates/projects.html',
            controller: 'ProjectsController'
        })
        .when('/contact', {
            templateUrl: 'app/templates/contact.html',
            controller: 'ContactController'
        })
        .otherwise({
            redirectTo: '/'
        });
});
