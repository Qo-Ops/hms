from app import get_db

from flask_login import UserMixin


class User(UserMixin):

    def __init__(self, id, is_owner):
        self.id = id
        # If is_owner == false the user is an administrator
        self.is_owner = is_owner

    def manages(self, location_id):
        if self.is_owner:
            return False
        try:
            db = get_db()
            c = db.cursor()
            # TODO: query for getting location by location_id and admin_id
            c.execute('')
            result = c.fetchone()
            db.commit()
            if result is None:
                return False
            else:
                return True
        except Exception as e:
            from app import app
            app.logger.error(str(e))

    def get_managed_location(self):
        if self.is_owner:
            return None
        try:
            db = get_db()
            c = db.cursor()
            # TODO: get location of administrator by his id
            c.execute('')
            location = c.fetchone()
            db.commit()
            return location
        except Exception as e:
            from app import app
            app.logger.error(str(e))

    def get_owned_chains(self):
        if not self.is_owner:
            return None
        try:
            db = get_db()
            c = db.cursor()
            # TODO: get location of administrator by his id
            c.execute("SELECT hotel_id, chain_name FROM hotel_chains WHERE owner_id=%s",
                      (self.id,))
            chains = c.fetchall()
            db.commit()
            return chains
        except Exception as e:
            from app import app
            app.logger.error(str(e))

    def owns(self, chain_name):
        if not self.is_owner:
            return False
        try:
            db = get_db()
            c = db.cursor()
            # TODO: query for getting location by owner_id and chain_name
            c.execute('')
            result = c.fetchone()
            db.commit()
            if result is None:
                return False
            else:
                return True
        except Exception as e:
            from app import app
            app.logger.error(str(e))


    def is_authenticated(self):
        return True

    def is_active(self):
        return True

    def is_anonymous(self):
        return False

    def get_id(self):
        return str(self.id)
