app.service('TaskService', function() {
    var tasks = [
        { title: 'Demo your AngularJS skills', status: 'In Progress', isEditing: false },
        { title: 'Technical Skills Interview', status: 'Pending', isEditing: false },
        { title: 'Get Job Offer', status: 'Pending', isEditing: false },
        { title: 'First Interview', status: 'Completed', isEditing: false }
    ];

    this.getTasks = function() {
        return tasks;
    };

    this.addTask = function(task) {
        tasks.push(task);
    };

    this.deleteTask = function(task) {
        var index = tasks.indexOf(task);
        if (index > -1) {
            tasks.splice(index, 1);
        }
    };
});
