// Define the AngularJS module
var app = angular.module('myApp', []);

// Define a service (optional, for this simple example)
app.factory('NameService', function() {
    var name = 'Ryan';
    
    return {
        getName: function() {
            return name;
        },
        setName: function(newName) {
            name = newName;
        }
    };
});
