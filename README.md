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

3. Use `docker-compose` to bring up the containers. During first creation, the database dump will be imported to the database automatically.
    ```
    docker-compose up -d
    ```

4. The database is accessible on port `5432` and pgadmin is accessible at port `8080`.