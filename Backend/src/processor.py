import logging
import nltk
import re
from nltk.corpus import stopwords
from nltk.stem import WordNetLemmatizer
from nltk.corpus import wordnet

logger = logging.getLogger(__name__)

def setup_nltk():
    """
    Ensures that required NLTK datasets/models are downloaded.
    Specifically checks for the 'stopwords', 'wordnet', 'omw-1.4', 'punkt', and 'averaged_perceptron_tagger' corpora.
    """
    resources = [
        ('corpora/stopwords', 'stopwords'),
        ('corpora/wordnet', 'wordnet'),
        ('corpora/omw-1.4', 'omw-1.4'),
        ('taggers/averaged_perceptron_tagger', 'averaged_perceptron_tagger'),
        ('taggers/averaged_perceptron_tagger_eng', 'averaged_perceptron_tagger_eng')
    ]
    
    for path, pkg in resources:
        try:
            nltk.data.find(path)
        except (LookupError, OSError):
            logger.info(f"Downloading NLTK {pkg} corpus...")
            nltk.download(pkg, quiet=True)

def get_wordnet_pos(treebank_tag):
    """
    Maps NLTK Treebank POS tags to WordNet POS tags.
    """
    if treebank_tag.startswith('J'):
        return wordnet.ADJ
    elif treebank_tag.startswith('V'):
        return wordnet.VERB
    elif treebank_tag.startswith('N'):
        return wordnet.NOUN
    elif treebank_tag.startswith('R'):
        return wordnet.ADV
    else:
        return None

def load_known_words(filepath: str) -> set:
    """
    Reads a list of known words from a text file.
    Each word should be on a new line.
    
    Args:
        filepath (str): Path to the text file containing known words.
        
    Returns:
        set: A set of lowercase known words.
    """
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            known_words = {line.strip().lower() for line in f if line.strip()}
        logger.info(f"Loaded {len(known_words)} known words from {filepath}.")
        return known_words
    except FileNotFoundError:
        logger.warning(f"{filepath} not found. Starting with an empty blacklist.")
        return set()
    except Exception as e:
        logger.error(f"Error reading {filepath}: {e}. Starting with an empty blacklist.")
        return set()

def process_data(article_data: dict, known_words_file: str = "known_words.txt") -> dict:
    """
    Processes the raw tokenized article data to extract target vocabulary.
    
    Filters applied:
    - Lowercase normalization
    - Strip punctuation and allow accented characters (e.g., café, résumé)
    - POS Tagging for context-aware lemmatization and definition lookup
    - Lemmatization (base form reduction)
    - Remove standard English stop words
    - Keep only words with length >= 5
    - Skip words in the "Known Words Blacklist"
    
    Args:
        article_data (dict): The output from the scraper module, containing sentences and words.
        known_words_file (str): Path to the blacklist file. Defaults to "known_words.txt".
    
    Returns:
        dict: A dictionary mapping unique target words to their context and POS.
              Example: {"prodigy": {"context": "...", "pos": "n"}}
    """
    setup_nltk()
    
    lemmatizer = WordNetLemmatizer()
    stop_words = set(stopwords.words('english'))
    known_words = load_known_words(known_words_file)
    
    # Regex to allow accented characters
    accented_regex = re.compile(r'^[a-zA-ZÀ-ỹ]+$')
    
    unique_vocabulary = {}
    
    data_list = article_data.get('data', [])
    
    for item in data_list:
        original_sentence = item.get('sentence', '')
        tokens = item.get('words', [])
        
        # 1. POS Tagging
        tagged_tokens = nltk.pos_tag(tokens)
        
        for token, tag in tagged_tokens:
            # 2. Normalization
            word_lower = token.lower()
            
            # 3. Cleaning: Allow alphabetic and accented characters
            if not accented_regex.match(word_lower):
                continue
            
            # 4. Map POS tag for lemmatization
            wn_pos = get_wordnet_pos(tag)
            
            # 5. Lemmatization
            # If we have a specific POS, use it. Otherwise, perform triple-pass as fallback
            if wn_pos:
                word_lemma = lemmatizer.lemmatize(word_lower, pos=wn_pos)
            else:
                word_lemma = lemmatizer.lemmatize(lemmatizer.lemmatize(lemmatizer.lemmatize(word_lower, pos='v'), pos='n'), pos='a')
                
            # 6. Length constraint
            if len(word_lemma) < 5:
                continue
                
            # 7. Stop-words removal
            if word_lemma in stop_words:
                continue
            
            # 8. Known words blacklist removal
            if word_lemma in known_words:
                continue
                
            # 9. Deduplication & Context mapping
            if word_lemma not in unique_vocabulary:
                unique_vocabulary[word_lemma] = {
                    "context": original_sentence,
                    "pos": wn_pos  # Store for dictionary lookup
                }
                
    logger.info(f"NLP Processing complete. Found {len(unique_vocabulary)} unique target words after filtering.")
    
    return unique_vocabulary
