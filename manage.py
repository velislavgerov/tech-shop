import os
from flask_script import Manager # class for handling a set of commands
from flask_migrate import Migrate, MigrateCommand

from app import db, create_app
from app import login_manager
from app import models

app = create_app(config_name=os.getenv('APP_CONFIG'))
db.init_app(app)
login_manager.init_app(app)


migrate = Migrate(app, db)
manager = Manager(app)

manager.add_command('db', MigrateCommand)

if __name__ == '__main__':
    manager.run()
