import sys
import argparse

def train_top2vec_on_bioinformatics(bioinformatics_readme_path: str, not_bioinformatics_readme_path: str, model_output_path: str, attempts_count: int):
    """
    Trains top2vec models on READ.me pages of GitHub repositories.
    It repeats the training multiple times and saves the best performing model.
    The accuracy score is based on correctly identifying the bioinformatics topic.

    Parameters
    ----------
    bioinformatics_readme_path : str
        Path to the json dict containing repository urls and their associated READ.me contents
        of repostiroies known to be of the bioinformatics domain.
    not_bioinformatics_readme_path : str.
        Path to the json dict containing repository urls and their associated READ.me contents
        of repostiroies known to not be of the bioinformatics domain.
    model_output_path : str.
        The output path of the resulting top2vec model.
    attempts_count : str.
        Number of times the model should be generated.
    """
    if attempts_count < 1:
        sys.exit("attempts_count needs to be greater than 0.")
    else:
        from top2vec import Top2Vec
        import json

        # Load data and keep track of bioinformatics topic.

        readme_list = []
        is_bioinformatics = []

        with open(not_bioinformatics_readme_path) as json_file:
            not_bio_topics = json.load(json_file)
            if len(not_bio_topics) < 1:
                sys.exit("READ.me list for non-bioinformatics repositories is empty")
        for repository in not_bio_topics:
            readme_list.append(not_bio_topics[repository])
            is_bioinformatics.append(False)
        with open(bioinformatics_readme_path) as json_file:
            bio_topics = json.load(json_file)
            if len(bio_topics) < 1:
                sys.exit("READ.me list for bioinformatics repositories is empty")
        for repository in bio_topics:
            readme_list.append(bio_topics[repository])
            is_bioinformatics.append(True)
        
        highest_accuracy = 0

        for attempt in range(attempts_count):
            model = Top2Vec(readme_list, speed="learn", workers=8) # Train model

            topic_sizes, topic_nums = model.get_topic_sizes()
            try:
                topic_words, word_scores, topic_scores, topic_nums_bioinformatics = model.search_topics(keywords=["bioinformatics"], num_topics=len(topic_nums))
                bioinformatics_topic = topic_nums_bioinformatics[0]

                topic_sizes, topic_nums = model.get_topic_sizes()

                negative_documents = []
                positive_documents = []
                for topic_num in topic_nums:
                    documents, document_scores, document_ids = model.search_documents_by_topic(topic_num, num_docs=topic_sizes[topic_num])
                    if topic_num == bioinformatics_topic:
                        positive_documents.extend(document_ids)
                    else:
                        negative_documents.extend(document_ids)
                TP = 0
                FP = 0
                TN = 0
                FN = 0
                FP_Docs = []
                for document_id in positive_documents:
                    if is_bioinformatics[document_id]:
                        TP += 1
                    else:
                        FP_Docs.append(document_id)
                        FP += 1
                for document_id in negative_documents:
                    if is_bioinformatics[document_id]:
                        FN += 1
                    else:
                        TN += 1

                accuracy = (TP + TN) / ((TP + FN) + (FP + TN))

                if accuracy > highest_accuracy:
                    # Save well-performing model, overwrites any existing model.
                    highest_accuracy = accuracy 
                    model.save(model_output_path)
            except:

                # Presumably the bioinformatics keyword was not listed and no topic for bioinformatics has been created for this attempt.
                continue

        if highest_accuracy == 0:
            sys.exit("Fatal issue with model creation, no suitable model could be created.")

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument('-ib', '--input_bioinformatics', type=str,
        help="Path to the json dict containing repository data related to bioinformatics.")
    parser.add_argument('-in', '--input_not_bioinformatics', type=str,
        help="Path to the json dict containing repository data not related to bioinformatics.")
    parser.add_argument('-o', '--output', type=str, help="Output path of top2vec model")
    parser.add_argument('-a', '--attempts', type=int, help="Number of repeated attempts for top2vec model generation")
    args = parser.parse_args()

    
    train_top2vec_on_bioinformatics(args.input_bioinformatics, args.input_not_bioinformatics, args.output, args.attempts)