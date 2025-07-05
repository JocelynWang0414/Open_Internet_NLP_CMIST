from bertopic import BERTopic
import pandas as pd
from sklearn.feature_extraction.text import CountVectorizer
from bertopic.vectorizers import ClassTfidfTransformer
import numpy as np
from bertopic import BERTopic

def create_guided_topic_model():
    """
    Create a BERTopic model with guided topics for internet governance analysis.
    
    Returns:
        BERTopic: Configured topic model with seed topics
    """
    
    seed_topic_list = [
    # open
    ["open", "openness", "free", "freedom", "access", "universal"], 
    ["privacy", "democratic", "human rights", "civil", "liberties", "expression"],
    # mixed
    ["international", "cooperation", "global", "shared", "responsibility", "inclusive", 
        "collaboration", "borderless", "connectivity", "transparency", "neutrality"],
    ["laws", "legal", "enforcement", "infrastructure", "standards", "framework", 
        "accountability", "governance", "regulation", "compliance"],
    # ["competition", "innovation", "entrepreneurship", "investment", "economic development"]
    # close
    ["sovereignty", "national", "territory", "foreign", "ideological", "subversion", "cultural", "stability"],
    ["control", "safeguard", "protect", "prevent", "surveillance", "firewall"]]
    
    # Create vectorizer with better n-gram range for phrase detection
    vectorizer_model = CountVectorizer(
        ngram_range=(1, 3),  # Include unigrams, bigrams, and trigrams
        stop_words="english",
        min_df=2,  # Minimum document frequency 
        # adjusted min_df to 1 when analyzing china2016 due to the bug "raise ValueError("max_df corresponds to < documents than min_df")"
        max_df=0.95  # Maximum document frequency
    )
    
    # Create TF-IDF transformer
    ctfidf_model = ClassTfidfTransformer(reduce_frequent_words=True)
    
    # Initialize BERTopic model with guided topics
    topic_model = BERTopic(
        seed_topic_list=seed_topic_list,
        vectorizer_model=vectorizer_model,
        ctfidf_model=ctfidf_model,
        verbose=True,
        calculate_probabilities=True
    )
    
    return topic_model

def fit_and_analyze_topics(docs, topic_model):
    """
    Fit the topic model and return analysis results.
    
    Args:
        docs (list): List of documents to analyze
        topic_model (BERTopic): Configured topic model
        
    Returns:
        tuple: (topics, probabilities, topic_model)
    """
    
    print("Fitting topic model...")
    topics, probs = topic_model.fit_transform(docs)
    
    print(f"Number of topics found: {len(set(topics))}")
    print(f"Number of documents: {len(docs)}")
    
    return topics, probs, topic_model

def analyze_results(topic_model, topics, docs):
    """
    Analyze and display topic modeling results.
    
    Args:
        topic_model (BERTopic): Fitted topic model
        topics (list): Topic assignments for each document
        docs (list): Original documents
    """
    
    # Get topic information
    topic_info = topic_model.get_topic_info()
    print("\nTopic Information:")
    print(topic_info)
    
    # Show top words for each topic
    print("\nTop words per topic:")
    for topic_id in topic_info['Topic']:
        if topic_id != -1:  # Skip outlier topic
            words = topic_model.get_topic(topic_id)
            print(f"\nTopic {topic_id}:")
            print([word for word, _ in words[:]])
    
    print('******* Print topics: ')

    topic_info = topic_model.get_topic_info()
    print(topic_info)
    topic_names = [
        topic_info.loc[topic_info['Topic'] == topic, 'Name'].values[0]
        if topic in topic_info['Topic'].values else 'Outlier'
        for topic in topics
    ]
    
    # Create document-topic dataframe
    doc_topic_df = pd.DataFrame({
        'Document': docs,
        'Topic': topics,
        'Topic_Name': topic_names
    })
    
    # Show topic distribution
    topic_counts = doc_topic_df['Topic'].value_counts().sort_index()
    print("\nTopic Distribution:")
    print(topic_counts)
    
    return doc_topic_df

def save_results(topic_model, doc_topic_df):
    """
    Save topic modeling results to files.
    
    Args:
        topic_model (BERTopic): Fitted topic model
        doc_topic_df (pd.DataFrame): Document-topic assignments
        output_path (str): Base path for output files
    """
    output_path = 'guided_topic_modeling'
    # Save topic information
    topic_info = topic_model.get_topic_info()
    topic_info.to_csv(f"{output_path}_topic_info.csv", index=False)
    
    # Save document-topic assignments
    doc_topic_df.to_csv(f"{output_path}_doc_topics.csv", index=False)
    
    # Save detailed topic words
    with open(f"{output_path}_topic_words.txt", "w") as f:
        for topic_id in topic_info['Topic']:
            if topic_id != -1:
                words = topic_model.get_topic(topic_id)
                f.write(f"Topic {topic_id}:\n")
                f.write(", ".join([f"{word} ({score:.3f})" for word, score in words]))
                f.write("\n\n")
    
    print(f"Results saved to files with prefix: {output_path}")

def main_pipeline(docs):
    """
    Main pipeline function to run guided topic modeling.
    
    Args:
        docs (list): List of documents to analyze
        save_outputs (bool): Whether to save results to files
        
    Returns:
        tuple: (topic_model, topics, probabilities, doc_topic_df)
    """
    
    # Create topic model
    topic_model = create_guided_topic_model()
    
    # Fit model and get results
    topics, probs, fitted_model = fit_and_analyze_topics(docs, topic_model)
    
    # Analyze results
    doc_topic_df = analyze_results(fitted_model, topics, docs)
    
    # Save results if requested
    save_results(fitted_model, doc_topic_df)

    #return fitted_model, topics, probs
    return fitted_model, topics, probs, doc_topic_df

# Example usage (uncomment when you have your documents):

# Assuming you have your documents in a variable called 'docs'
# Run the pipeline

filenames = ['india2013', 'china2016_cleaned', 'southafrica2015', 'netherland2011']
docs = pd.read_csv('netherland2011.csv')['text'].tolist()
# topic_model, topics, probabilities = main_pipeline(docs)
topic_model, topics, probabilities, results_df = main_pipeline(docs)

# Optional: Generate visualizations
# topic_model.visualize_topics()
# topic_model.visualize_hierarchy()
# topic_model.visualize_barchart()