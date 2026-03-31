app.filter('statusFilter', function() {
    return function(tasks, status) {
        if (!status) return tasks; // Show all tasks if no status is selected
        return tasks.filter(function(task) {
            return task.status === status;
        });
    };
});
