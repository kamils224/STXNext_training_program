# STXNext_training_program

Perform makemigrations:

`sudo docker-compose run app python manage.py makemigrations`

Perform migration:

`sudo docker-compose run app python manage.py migrate`

Create superuser:

`sudo docker-compose run app python manage.py createsuperuser`

Run docker:

`docker-compose up` or `docker-compose up --build`

If migration errors occur, remove your database volumes and try again.

*TODO*
