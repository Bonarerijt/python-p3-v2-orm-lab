from __init__ import CURSOR, CONN
from department import Department
from employee import Employee


class Review:

    # Dictionary of objects saved to the database.
    all = {}

    def __init__(self, year, summary, employee_id, id=None):
        self.id = id
        self.year = year
        self.summary = summary
        self.employee_id = employee_id

    def __repr__(self):
        return (
            f"<Review {self.id}: {self.year}, {self.summary}, "
            + f"Employee: {self.employee_id}>"
        )

    @classmethod
    def create_table(cls):
        """ Create a new table to persist the attributes of Review instances """
        sql = """
            CREATE TABLE IF NOT EXISTS reviews (
            id INTEGER PRIMARY KEY,
            year INT,
            summary TEXT,
            employee_id INTEGER,
            FOREIGN KEY (employee_id) REFERENCES employee(id))
        """
        CURSOR.execute(sql)
        CONN.commit()

    @classmethod
    def drop_table(cls):
        """ Drop the table that persists Review  instances """
        sql = """
            DROP TABLE IF EXISTS reviews;
        """
        CURSOR.execute(sql)
        CONN.commit()

    def save(self):
        """ Insert a new row with the year, summary, and employee id values of the current Review object.
        Update object id attribute using the primary key value of new row.
        Save the object in local dictionary using table row's PK as dictionary key"""
        if self.id is None:
            CURSOR.execute(
                "INSERT INTO reviews (year, summary, employee_id) VALUES (?, ?, ?)",
                (self.year, self.summary, self.employee_id)
            )
            CONN.commit()
            self.id = CURSOR.lastrowid
        else:
            self.update()
        Review.all[self.id] = self


    @classmethod
    def create(cls, year, summary, employee_id):
        """ Initialize a new Review instance and save the object to the database. Return the new instance. """
        review = cls(year, summary, employee_id)
        review.save()
        return review


    @classmethod
    def instance_from_db(cls, row):
        """Return a Review object having the attribute values from the table row."""

        review_id = row[0]

        # Check cache first
        if review_id in cls.all:
            review = cls.all[review_id]
            # Update attributes from row in case the cached object was modified
            review.year = row[1]
            review.summary = row[2]
            review.employee_id = row[3]
        else:
            # Create a new Review instance from the row
            review = cls(
                year=row[1],
                summary=row[2],
                employee_id=row[3],
                id=review_id
            )
            cls.all[review_id] = review

        return review

    @classmethod
    def find_by_id(cls, id):
        """Return a Review instance having the attribute values from the table row."""
        CURSOR.execute("SELECT * FROM reviews WHERE id=?", (id,))
        row = CURSOR.fetchone()
        if row:
            return cls.instance_from_db(row)
        return None

    def update(self):
        """Update the table row corresponding to the current Review instance."""
        CURSOR.execute(
            "UPDATE reviews SET year=?, summary=?, employee_id=? WHERE id=?",
            (self.year, self.summary, self.employee_id, self.id)
        )
        CONN.commit()
        Review.all[self.id] = self

    def delete(self):
        """Delete the table row corresponding to the current Review instance,
        delete the dictionary entry, and reassign id attribute"""
        CURSOR.execute("DELETE FROM reviews WHERE id=?", (self.id,))
        CONN.commit()
        if self.id in Review.all:
            del Review.all[self.id]
        self.id = None

    @classmethod
    def get_all(cls):
        """Return a list containing one Review instance per table row"""
        CURSOR.execute("SELECT * FROM reviews")
        rows = CURSOR.fetchall()
        return [cls.instance_from_db(row) for row in rows]
    
    @property
    def year(self):
        return self._year

    @year.setter
    def year(self, value):
        if not isinstance(value, int) or value < 2000:
            raise ValueError("Year must be an integer >= 2000")
        self._year = value

    @property
    def summary(self):
        return self._summary

    @summary.setter
    def summary(self, value):
        if not isinstance(value, str) or not value.strip():
            raise ValueError("Summary must be a non-empty string")
        self._summary = value

    @property
    def employee_id(self):
        return self._employee_id

    @employee_id.setter
    def employee_id(self, value):
        # Lazy import to avoid circular imports
        from lib.employee import Employee
        if not isinstance(value, int) or Employee.find_by_id(value) is None:
            raise ValueError("employee_id must be a valid Employee id")
        self._employee_id = value


