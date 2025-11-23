# Lilly Technical Challenge Documentation Template

## Approach

- Initially, I went over the existing code base and gauged how much time I should allocate to where.
- API was mostly finished just a few validation checks and http best practices to be implemented so I decided I would spend 20 mins on it and com back if time allowed.
- Frontend was completely bare so i dedicated the most time there.

## Objectives
- One thing I noticed was the URLs contained both nouns and verbs which is not best practice for HTTP so I made the quick change e.g. @app.delete(/delete) -> @app.delete(/medicines)
- Another thing was that there was no input validation which was relatively straighforward to implement. I did make some assumptions as there was no openAPI specification.

## Problems Faced
- I had not used fastAPI before but a lot of the code was already written which meant I only had to use normal python for validation, imports etc.
- I did have to read some documentation regarding things like app.delete app.get Path Body.
- Had to deal with edge cases regarding null prices or empty medicine names already existing in the database due to the data migration issues.

## Evaluation
- RESTful best practices implemented e.g. /create -> /medicines method: "POST"
- I was quite familiar with both python, js, html, css, and http/api practices which I feel gave me a leg up.
- Overall, the API handles most requests well including misconfigured requests by giving detailed error codes and reasons for them.
- created a helper method to prevent code duplication e.g. does_med_exist()
- Module testing for the API was done via Postman which achieved 100% coverage
- Added pydantic models for better api documentation and just generally better for consistency and type safety
- Added quite a lot of logging involved which would help with debugging, production monitoring, maintainability
- name="" or price=null cases are handled in the front end to avoid errors. Important because those values exist in the database for some reason
- average was implemented both in front and back end


### Improvements
- If I had the time I would have implemented some sort of database class / object with appropriate methods to abstract database features allowing for better maintainability, reduced code duplication, and seperation of concern especially in relation to the handlers as everything has relatively low cohesion.
- I would improve the file structure to adhere to the fastAPI best practices in order to improve codebase navigation, maintainability, seperation of business logic and handlers etc
- I had no time to do unit testing which I had to make the difficult decision to leave out due to time. To improve I would definitely implement it in the backend and frontend js.
- One large thing is that I return a lot of the http codes in the body rather than doing something like raise HTTPException which would greatly help
- Potential race conditions using fastAPI to access data.json
- Could improve the underlying datastructure for database JSON file -> hashmap which leads to O(n) -> O(1)
- Could just keep the data in memory then write to a file during shutdown
- Inconsistent error handling e.g. HTTPException and body response codes. If I was more familiar with fastAPI I could have kept things the same throughout.
- no errors shown in UI apart from missing fields.