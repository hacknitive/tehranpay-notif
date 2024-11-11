# Tehran Payment (Code Challenge - Notification Service)

This service is one of two services implemented for Tehran Payment - code challenge. This service depends on *Authentication service* to work properly.


## How to Deploy:
To deploy this service you need to create an external docker network with name code_challenge by utilizing this command:
```
docker network create code_challenge
```
now you should see this network in docker networks by this command:
```
docker network ls | grep code_challenge
```
now you can bring the web app by this command:
```
docker compose up
```
# Note:
- Do not use -d with the last command in order to be able to see the OTP codes sent to Celery, which help you to validate the 'verify-otp' route.
# Good to Know
- The swagger is on this address: http://127.0.0.1:8001/swagger/
- You can change some configuration by `.env` file
- To know how to fill the public keys refer to *Authentication service* documentation.


