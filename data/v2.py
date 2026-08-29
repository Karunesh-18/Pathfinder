import pandas as pd
import numpy as np
import re
import os
import time
from collections import defaultdict
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.metrics.pairwise import cosine_similarity

# Dynamically locate the data_set folder relative to the script location
script_dir = os.path.dirname(os.path.abspath(__file__))
if os.path.isdir(os.path.join(script_dir, 'c215051c-6-Archive 4')):
    TRAIN_PATH = os.path.join(script_dir, 'c215051c-6-Archive 4', 'train.csv')
    TEST_PATH = os.path.join(script_dir, 'c215051c-6-Archive 4', 'test.csv')
elif os.path.isdir(os.path.join(script_dir, 'data_set')):
    TRAIN_PATH = os.path.join(script_dir, 'data_set', 'train.csv')
    TEST_PATH = os.path.join(script_dir, 'data_set', 'test.csv')
else:
    parent_dir = os.path.dirname(script_dir)
    TRAIN_PATH = os.path.join(parent_dir, 'data_set', 'train.csv')
    TEST_PATH = os.path.join(parent_dir, 'data_set', 'test.csv')

OUT_PATH = os.path.join(script_dir, 'submission.csv')

print(f"Dataset paths:\n - Train: {TRAIN_PATH}\n - Test: {TEST_PATH}\n - Output: {OUT_PATH}")

print("Loading data...")
train = pd.read_csv(TRAIN_PATH)
test = pd.read_csv(TEST_PATH)

def get_sentences(text):
    sents = [s.strip() for s in re.split(r'\.\s+', text) if s.strip()]
    cleaned = []
    for s in sents:
        if s.endswith('.'):
            s = s[:-1].strip()
        if s:
            cleaned.append(s)
    return cleaned

print("Building deterministic sentence-to-course mapping...")
t0 = time.time()
sent_to_courses = defaultdict(set)
for idx, row in train.iterrows():
    review = row['Reviews']
    course = row['Course']
    sents = get_sentences(review)
    if len(sents) > 1:
        # Exclude the first sentence because it contains the course name in train,
        # but is masked in the test set.
        for s in sents[1:]:
            sent_to_courses[s].add(course)
    else:
        for s in sents:
            sent_to_courses[s].add(course)

unique_sents_map = {s: list(courses)[0] for s, courses in sent_to_courses.items() if len(courses) == 1}
print(f"Mapped {len(unique_sents_map)} course-unique sentences in {time.time() - t0:.2f}s")

# Clean/mask both train and test reviews to unify first-sentence templates
print("Preprocessing reviews to align templates...")
def mask_course_name(row):
    review = row['Reviews']
    course = row['Course']
    pattern = re.compile(re.escape(course), re.IGNORECASE)
    masked = pattern.sub('this course', review)
    return masked

def normalize_test_review(text):
    text = text.replace('this learning path', 'this course')
    text = text.replace('this program', 'this course')
    return text

train['masked_reviews'] = train.apply(mask_course_name, axis=1)
test['normalized_reviews'] = test['Reviews'].apply(normalize_test_review)

# Fit vectorizer for similarity on masked/normalized reviews
print("Fitting main TF-IDF vectorizer for similarity ranking...")
t0 = time.time()
vectorizer_sim = TfidfVectorizer(ngram_range=(1, 2), stop_words="english", sublinear_tf=True, min_df=2)
X_train_sim = vectorizer_sim.fit_transform(train['masked_reviews'])
X_test_sim = vectorizer_sim.transform(test['normalized_reviews'])
print(f"Vectorized reviews in {time.time() - t0:.2f}s")

# Pre-map indices and vectors by course
train_indices_by_course = {}
train_rows_by_course = {}
train_index_arr = train['Index'].to_numpy()
for course in train['Course'].unique():
    mask = (train['Course'] == course).to_numpy()
    train_indices_by_course[course] = train_index_arr[mask]
    train_rows_by_course[course] = X_train_sim[mask]

print("Predicting and recommending...")
t0 = time.time()
results = []
dict_hits = 0
fallback_hits = 0

# Fallback classifier trained on same masked reviews (just in case)
clf_fb = LogisticRegression(C=1.0, max_iter=100, random_state=42)
clf_fb.fit(X_train_sim, train['Course'].values)

for i, row in test.iterrows():
    review = row['Reviews']
    sents = get_sentences(review)
    
    # Try dictionary mapping first
    pred_course = None
    for s in sents:
        if s in unique_sents_map:
            pred_course = unique_sents_map[s]
            break
            
    if pred_course is not None:
        dict_hits += 1
    else:
        fallback_hits += 1
        # Fallback to ML classifier
        test_vec_fb = X_test_sim[i]
        pred_course = clf_fb.predict(test_vec_fb)[0]
        
    # Get training reviews for the predicted course
    c_indices = train_indices_by_course[pred_course]
    c_vecs = train_rows_by_course[pred_course]
    
    # Compute similarity against the subset
    test_vec_sim = X_test_sim[i]
    sims = cosine_similarity(test_vec_sim, c_vecs).flatten()
    
    # Sort stably to preserve index order in case of floating-point ties
    top_k_local = np.argsort(-sims, kind='stable')[:10]
    top_k_global = c_indices[top_k_local].tolist()
    
    results.append(top_k_global)

print(f"Recommendation finished in {time.time() - t0:.2f}s")
print(f"Method statistics: Dictionary hits: {dict_hits}, Fallback hits: {fallback_hits}")

# Format and write submission
submission = pd.DataFrame({
    "Index": test["Index"],
    "Index_list": [str(r) for r in results],
})
submission.to_csv(OUT_PATH, index=False)
print(f"Wrote submission file to {OUT_PATH}")