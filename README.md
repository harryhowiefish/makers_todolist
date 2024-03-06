# Maker's Todo List
Adam Savage Inspired Todo List


### Functions
- list in list
- half marked
- filter empty and mark


### action list (test first)
- add tests for
    - add routing test
- complete functionality


- create views
    - Task listing
        - add task
    - single task view for delete and edit

- add docstrings and type hints

### additional function
- time based
    - reoccurence task
    - weekly view



### Tools
flask
vanilla js
sqlite


### Current issues
- self parenting (i.e. id = parent_id) and recursive parenting (i.e. "id=1,parent_id=2","id=2,parent_id=1") are not check during insert and update in DB due to sqlite constraint. Both issues currently are only prevented from the frontend UI.