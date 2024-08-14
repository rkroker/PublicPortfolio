View (HTML)
	The view binds to the controller's scope using ng-model and {{ }} expressions.
	ng-controller="MyController" attaches the controller to the view.
Service (NameService)
	The NameService manages the name variable. It provides a getName method to retrieve the name and a setName method to update it.
	This service can be expanded to include more complex logic or additional data management tasks.
Controller (MyController)
	The controller initializes the name variable by retrieving it from NameService.
	It watches for changes in the name variable and updates the service accordingly.

Directory Structure:
/my-app
  |-- index.html
  |-- app.js
  |-- controller.js
