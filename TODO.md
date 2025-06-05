# What's next to do

## Bigger plans
- [ ] Remove dumb DTO layer and replace it with real domain model
- [X] Restructure product configurations db model
- [ ] Move product specifications to MongoDB (for better customization)
- [ ] Add caching for delivery data (Redis or Valkey)


## Smaller plans
- [ ] Remove dumb DTO layer and replace it with real domain model
    - [X] Rename package containing sqlalchemy models to "db_models"
    - [X] Rename db models to have appendix "DbModel"
    - [X] Create domain models in package "models"
    - [ ] Rewrite repository tests to use domain models
        - [X] Rewrite configuration repository tests
        - [X] Rewrite product repository tests
        - [X] Write banner repository tests
        - [X] Write user repository tests
        - [ ] Write cart repository tests
        - [X] Write manufacturer repository tests
        - [ ] Write order repository tests
        - [ ] Write payment repository tests
    - [ ] Rewrite Repositories, Services and ViewModels to use domain models
        - [ ] Rewrite Repositories
            - [X] Rewrite product repository
            - [X] Rewrite configuration repository
            - [X] Rewrite banner repository
            - [X] Rewrite user repository
            - [ ] Rewrite cart repository
            - [X] Rewrite manufacturer repository
            - [ ] Rewrite order repository
            - [ ] Rewrite payment repository
    - [ ] Get rid of this dumb "dto" layer
- [ ] Remove unused methods from Repositories, Services, ViewModels and Routes

- [X] Restructure product configurations db model
    - [X] Write tests for product repository to get full coverage
    - [X] Write tests for configuration repository to get full coverage
    - [X] Create new db model for category types
    - [X] Change all relations to configuration model according to new db schema
    - [X] Rewrite product configurations and product repositories to use new db models

