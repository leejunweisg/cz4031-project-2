# cz4031-project-2

## Database Setup
1. Clone the repository.
    ```
    git clone git@github.com:leejunweisg/cz4031-project-2.git
    ```

2. Change the working directory to the `database` folder.
    ```
    cd cz4031-project-2/database
    ```

3. Download the `database-dump.sql` file from junwei's onedrive, save it in the database folder in Step 2.

4. Use `docker-compose` to bring up the containers. During first creation, the database dump will be imported to the database automatically.
    ```
    docker-compose up -d
    ```

5. The database is accessible on port `5432` and pgadmin is accessible at port `8080`.