# Directory Layout

~~~text
/clients/
- <name>/
  - php/
    - assets/
    - views/
  - python/
  config.json
/containers/
  - web_server/
    # Everything under wepci4app
  - ai_server/
    # Everything under rag
  docker-compose.yml
~~~

## Linking into Containers

### Linking for Web Server
~~~text
/clients/<name>/php/assets:/var/www/html/public/clients/<name>
/clients/<name>/php/views:/var/www/html/app/Views/clients/<name>
/clients/<name>/config.json:/var/www/html/app/Config/clients/<name>.json
~~~

### Linking for AI Server

~~~text
/clients/<name>/python:/app/clients/<name>
~~~
