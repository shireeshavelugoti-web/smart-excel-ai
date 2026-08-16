from typing import List, Tuple, Optional
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from fuzzywuzzy import fuzz

def match_column_name(query_term: str, available_columns: List[str]) -> Tuple[Optional[str], float]:
    """
    Matches a query term (e.g., 'department', 'salary', 'phone') to available columns
    using a hybrid approach: Exact Match > Fuzzy Match > TF-IDF Cosine Similarity.
    
    Returns (best_matched_column, confidence_score_between_0_and_1).
    """
    if not query_term or not available_columns:
        return None, 0.0
    
    query_clean = query_term.strip().lower()
    
    ABBREVIATIONS = {
        "dept": "department",
        "sal": "salary",
        "phone": "phone number",
        "mob": "mobile",
        "gpa": "gpa",
        "id": "id"
    }
    
    if query_clean in ABBREVIATIONS:
        query_clean = ABBREVIATIONS[query_clean]
        
    # 1. Exact or Substring match
    for col in available_columns:
        col_clean = str(col).strip().lower()
        if query_clean == col_clean or query_clean in col_clean or col_clean in query_clean:
            return col, 0.95
    
    # 2. Fuzzy Wuzzy Matching (Token Set Ratio & Partial Ratio)
    best_fuzzy_col = None
    best_fuzzy_score = 0.0
    
    for col in available_columns:
        col_clean = str(col).strip().lower()
        score_ratio = fuzz.ratio(query_clean, col_clean)
        score_partial = fuzz.partial_ratio(query_clean, col_clean)
        score_token = fuzz.token_set_ratio(query_clean, col_clean)
        
        composite_score = max(score_ratio, score_partial, score_token) / 100.0
        if composite_score > best_fuzzy_score:
            best_fuzzy_score = composite_score
            best_fuzzy_col = col
            
    # 3. TF-IDF + Cosine Similarity
    best_tfidf_col = None
    best_tfidf_score = 0.0
    try:
        corpus = [str(col).lower() for col in available_columns]
        vectorizer = TfidfVectorizer(analyzer="char_wb", ngram_range=(2, 4))
        tfidf_matrix = vectorizer.fit_transform(corpus + [query_clean])
        
        query_vec = tfidf_matrix[-1]
        cols_vec = tfidf_matrix[:-1]
        
        sims = cosine_similarity(query_vec, cols_vec)[0]
        max_idx = sims.argmax()
        best_tfidf_score = float(sims[max_idx])
        best_tfidf_col = available_columns[max_idx]
    except Exception:
        pass

    # Compare Fuzzy vs TFIDF
    if best_fuzzy_score >= best_tfidf_score and best_fuzzy_score > 0.4:
        return best_fuzzy_col, round(best_fuzzy_score, 2)
    elif best_tfidf_score > 0.4:
        return best_tfidf_col, round(best_tfidf_score, 2)
    elif best_fuzzy_col and best_fuzzy_score > 0.3:
        return best_fuzzy_col, round(best_fuzzy_score, 2)
    
    return available_columns[0] if available_columns else None, 0.5
