# What's next to do

## Bigger plans
- [ ] Remove dumb DTO layer and replace it with real domain model
- [ ] Restructure product configurations db model
- [ ] Move product specifications to MongoDB (for better customization)
- [ ] Add caching for delivery data (Redis or Valkey)


## Smaller plans
- [ ] Remove dumb DTO layer and replace it with real domain model
    - [X] Rename package containing sqlalchemy models to "db_models"
    - [X] Rename db models to have appendix "DbModel"
    - [X] Create domain models in package "models"
    - [ ] Rewrite Repositories, Services and ViewModels to use domain models
    - [ ] Get rid of this dumb "dto" layer

- [ ] Restructure product configurations db model
    - [ ] Write tests for product repository to get full coverage
    - [ ] Write tests for configuration repository to get full coverage
    - [ ] Create new db model for category types
    - [ ] Change all relations to configuration model according to new db schema
    - [ ] Rewrite product configurations and product repositories to use new db models

