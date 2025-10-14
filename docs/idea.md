# Top reqiurements of the project OHSteack:Open Heap Stack Team Manager

## General Idea
The way a team entering a competition produces results is similar to how a program runs in a computer: keep reusable
inputs on a stack and iterate on outputs in the heap. In OHSteack the workspace is intentionally reduced to two clear
objects:

- **User profile** — surfaces personal data, security controls, contribution statistics, and recent iterations.
- **Team space** — exposes each team's resource stack and result heap side by side, alongside member allocation so
  everyone understands current responsibilities.

With this structure every action stays in context: resources feed the stack, iterations build the heap, and members see
their impact without navigating redundant layers.


## Technique Stack
- Flask as backend
- Html(including javascript for automation and service handling) as frontend 
- Flask-Migrate
- gunicorn    
- markdown2    
- nginx for deployment
- supervisorctl for runtime supervision
- mysql for database


*If there are other packages needed add them in the requirements.txt(which is editable) and provided descriptions here*      


## Design Principles
- The functionality should be powerful and can solve the problems in this scenario.
- The UI should be simple, direct and beautiful with a calm, minimal aesthetic so the stack/heap metaphor stays clear.
- Ensure the project is runnable, better passing in production mode test.
- Quality is the very criteria. Make everything perfect despite the effort and time put in it.
- Add friendly comments that facilitates human reading and afterward maintenance.
- Don't modify **.gitignore** when you work on the project. That file is for deployment use.


## Framework
The framework:    
Follow the classic flask framework which has  
- **instance** directory for database. 
- **static** directory to store static data. 
- **templates** directory to store page htmls.
- **app** to handle backend affairs.


## Deployment
The project should also be ready to be put into production.       
Specifically, 
- Use **migration** directory to handle database modification.  
- Use a **venv** directory to create virtual environment on deployment server side.
- Use nginx and supervisor for deployment.
- Provided bash scripts for setting up and deployment and so on...
- Generate markdown as instructions for deployment:what I should do to deploy it in my own server? Try to be frank and      
pack as many procedures as possible into scripts to avoid mistakes. 
- Generate markdown as instructions for further-on maintenance, including the explanation on all aspects and tips when maintenance. 
- You can create more than one markdown files.
- Make it runnable.
