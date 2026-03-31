Project Goals:
1. Utilize AngularJS components to build a modular and maintainable structure.
2. Showcase two-way data binding and how changes in the model are reflected in the view.
3. Implement routing to navigate between different sections of the portfolio (e.g., Home, Projects, Contact).
4. Use services to handle data and business logic.
5. Create custom directives to encapsulate reusable functionality.
6. Implement filters to format or transform data displayed in the view.

Explanation:

The app uses AngularJS's $routeProvider to manage navigation between the home, projects, and contact pages. Each view has a corresponding controller that manages the data and logic. The ProjectsController fetches project data using the ProjectService. The ProjectService is an AngularJS service that handles fetching data, demonstrating how to abstract business logic away from the controllers. A custom projectCard directive is used to display individual projects, showcasing the ability to create reusable components. The capitalize filter capitalizes the first letter of the project titles, demonstrating data manipulation within the view.