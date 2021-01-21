# STXNext_training_program
Create .env.dev file based on .env-template

Perform makemigrations:

`sudo docker-compose run app python manage.py makemigrations accounts api_projects`

Perform migration:

`sudo docker-compose run app python manage.py migrate`

Create superuser:

`sudo docker-compose run app python manage.py createsuperuser`

Run docker:

`docker-compose up` or `docker-compose up --build`

If migration errors occur, remove your database volumes and try again.

`sudo docker-compose down --rmi all --volumes`

*TODO*
