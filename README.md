# SH-RandomReadMe
Get a random README from github and send it to a Bioinformatics Classifier Model

# Code Implementation
The `generate_top2vec_model.py` script uses two JSON dictionaries as input, both of which contain a list of GitHub repository URLs, referencing its plaintext READ.me string, to train the model, one of the JSON contains only repositories of the bioinformatics domain, where the other only includes repositories that are confirmed not be anywhere related to bioinformatics.

`train_top2vec_on_bioinformatics` : Trains multiple top2vec model, saves the best one based on the highest accuracy score for correctly categorizing bioinformatics.

# Code Execution

To run `train_top2vec_on_bioinformatics` please execute the following command:

`python3 code/generate_top2vec_model.py -ib data/bio-topic-with-readme.json -in data/non-bio-topic-with-readme.json -o data/top2vec.model -a 10`