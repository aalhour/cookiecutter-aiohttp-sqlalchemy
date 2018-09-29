# example_web_app

## Usage:

First step, setup the virtual environment and install the requirements 
```
$ cd /path/to/this/example
$ make install
```

Second step, copy the config file template over to `~/.config/example_web_app.conf` and customize it:
```
$ cp config/example.conf ~/.config/config/example_web_app.conf
```

Make sure to setup the database host, name, user and port in the config file or the example won't work
```
$ cat ~/.config/config/example_web_app.conf

[db]
host = localhost
port = 5432
name = <database_name>
schema = <schema_name>
user = <database_user>
```

Third step, initialize the example's database table:
```
$ venv/bin/init_example
```

Fourth step, run the application server:
```
$ venv/bin/run_example_web_app
```

## API Routes:

 * `localhost:9999/api/-/aliveness`: Dummy Aliveness endpoint
 * `localhost:9999/api/examples`: Get All Examples
 * `localhost:9999/api/examples/1`: Get Example by ID
 * `localhost:9999/api/v1.0/docs`: SwaggerUI-Powered API Documentation
