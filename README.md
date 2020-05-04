# mood

Hi! Welcome to **mood**. This app has been created for NeuroFlow as an interview assessment.


# How to run mood

1. Clone this repo with `git clone https://github.com/stevenmettler/mood` and navigate on your local machine to the cloned folder
2. Run `docker build -t moodapp .` on the `mood` working directory to build the docker container
3. Run `docker run -it -p 5000:5000 moodapp` on the `mood` working directory to then run the app!

## Endpoints
#### In the mood app, three endpoints are exposed to the user running the app.
- `/login`
		- `GET` requests to this, along with Basic Auth username and password that is in the DB, will return a token to be used as an `x-access-token` header on postman to verify other requests to the mood app.
- `/user`
	- `POST` requests to the `/user` endpoint that include a username and password will create a new user in the DB.
		- Example: `{ "name": "steven", "password": "abc123" }`
		- NOTE: for assessment purposes, this does not require authentication.
	- `GET` requests to the `/user` endpoint will return a list of all users registered along with their streak information.
	- Additionally, there are `PUT`, `DELETE`, and `GET` requests for `/user/<public_id>` that will promote a user to an admin, delete a user from the DB, or get a specific user's streaks.
-  `/mood`
	- `POST` requests to the `/mood` endpoint that include a feeling will persist a new mood for the logged in user and change the user's streak accordingly.
		- Example: `{ "feeling": "happy" }`
	- `GET` requests to the `/mood` endpoint will return all of a user's past moods, along with the user's current streak and maximal streak included in the body of each mood.
	



## What I would have done differently if this wasn't an assessment?

Firstly, I'll say that I had a lot of fun working on this. Prior to this I hadn't had much experience working with Flask, so it was a joy to be able to see its capabilities and tools. With that being said, I acknowledge that if this wasn't an assessment, I would put a lot more time into researching Flask best practices, including structuring my code in a more organized manner.

If I had worked on this as a story or a series of stories, I'd ask more questions before working. A lot of the instructuions on the prompt given were clear, but there were a few that didn't give me full confidence in the product I was building if I built it out according to the instructions given. One example: the instruction `Update the '/mood' endpoint with a GET method, so it only returns values submitted by the logged-in user.` is one that I wrestled with. Do you want me to return all of the moods that have been submitted, or just the last one? Along with that, where should I put the streak information? On all of the moods returned, or just one of them?

**IF** this were production code, it would need a better structure according to best practices. Testing would be required to ensure that the code indeed works as intended. The code would need to be running on something like Amazon EC2 with the database in the background running on something like Amazon RDS to ensure that the app will grow with the amount of requests coming in.