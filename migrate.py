from flask_migrate import Migrate, MigrateCommand
from flask_script import Manager
from models import db, app



migrate = Migrate(app, db)
manager = Manager(app)
manager.add_command('db', MigrateCommand)

if __name__ == '__main__':
    manager.run()


# python migrate.py db init  - to create migrations folders 

# when any changes in model run these command

# python migrate.py db migrate
# python migrate.py db upgrade