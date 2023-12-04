This is an example of Genetic Algorythm implementation in AWS with Lambda functions, SQS and DynamoDB. It can be modified to work with your task.
There are two DynamoDB tables - one with Genes and one with Population and main Lambda function GA-Initiate-Actions that allows to generate random indiviuals for population, mutate individuals or cross them. After that new individual is evaluated by Lambda function GA-Evaluate and then added to Population table. With growing Population the score of the top Individuals will get higher and higher and eventually you should get acceptable score for your task.

### Template example task:
Find string consisting of 10 digits with maximum sum of all digits.

Steps:
1. Deploy Cloudformation template.
2. Run Lambda GA-Add-To-Genes to fill Genes table.
3. Run Lambda GA-Initiate-Actions to create initial population. For that you can use GA-Initiate-Actions_InitiatePopulation test event parameters.
3. Run Lambda GA-Initiate-Actions to create new individs based on your current population. For that you can use GA-Initiate-Actions_EvolvePopulation test event parameters.
4. Repeat step 3 until you get individuals with acceptable score in Population table.


### How to use your own task:
1. Deploy Cloudformation template.
2. Modify and Run Lambda GA-Add-To-Genes function to populate Genes table with your set of Genes. Or use any other way to populate Genes table.
3. Modify GA-Evaluate to calculate score based on your task and Genes properties.
4. Example task assume that Genes can duplicate in different positions. If your task require them to be unique or there are additional requirements you will have to modify Lmbda functions GA-Add-Random-Individual, GA-Mutate-Individual, GA-Cross-Individuals to satisfy them.
5. Adjust Lambda parameters:
GA_INDIVIDUAL_GENES - number of genes that one individual has.
GA_MUTATE_RATE_PERCENT - percent rate of probabilty of changed gene in mutated individual.
GA_POPULATION_SIZE_FOR_MUTATE - number of top score individuals used for mutation.
GA_POPULATION_SIZE_FOR_CROSSING - number of top score individuals used for crossing.

### Component diagram:

![Component diagram](/img/AWS-Genetic-Algorythm.jpg?raw=true "Component diagram")