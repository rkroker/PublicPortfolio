var app = angular.module('testApp', ['ngRoute']);

app.config(function($routeProvider) {
    $routeProvider
        .when('/', {
            template: '<h1>Home</h1>'
        })
        .when('/projects', {
            template: '<h1>Projects</h1>'
        })
        .when('/contact', {
            template: '<h1>Contact</h1>'
        })
        .otherwise({
            redirectTo: '/'
        });
});
