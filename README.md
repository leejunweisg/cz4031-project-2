# cz4031-project-2 (for submission)

## Instructions
The following instructions applies to Windows systems with Python 3.x already installed.  
Note: Python 3.10 is not supported.

1. Navigate to the `app/` directory.

2. Create a Python virtual environment.
   ```
   python -m venv env
   ```
3. Activate virtual environment and install requirements.
    ```
    env\Scripts\activate
    pip install -r requirements.txt
    ```
4. Configure the database connection parameters to point to your Postgres instance in `app/preprocessing.py` (Lines 32-42)
   ```python
    # Lines 32-42 snippet from app/preprocessing.py
    @classmethod
    def get_conn(cls):
        if cls._conn is None:
            cls._conn = psycopg2.connect(
                host="localhost",
                database="TPC-H",
                user="postgres",
                password="password123",
                port="5432",
            )
        return cls._conn
   ```
5. Run the project.
    ```
    python project.py
    ```

6. The web app will be accessible at `http://localhost:5000/`
