# What's next to do

## Bigger plans
- [ ] Remove dumb DTO layer and replace it with real domain model
- [ ] Move product configurations to MongoDB (for better customization)
- [ ] Move product specifications to MongoDB (for better customization)
- [ ] Add caching for delivery data (Redis or Valkey)


## Smaller plans
- [ ] Remove dumb DTO layer and replace it with real domain model
    - [X] Rename package containing sqlalchemy models to "db_models"
    - [X] Rename db models to have appendix "DbModel"
    - [X] Create domain models in package "models"
    - [ ] Rewrite Repositories, Services and ViewModels to use domain models
    - [ ] Get rid of this dumb "dto" layer

- [ ] Move product configurations to MongoDB (for better customization)
    - [ ] Write tests for product repository to get full coverage
    - [ ] Write tests for configuration repository to get full coverage
    - [ ] Create MongoDB structure for product configurations
    - [ ] Create MongoDB structure for product specifications
    - [ ] Rewrite product configurations repository to use MongoDB
    - [ ] Rewrite product configurations repository to use MongoDB

