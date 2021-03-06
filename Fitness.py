# IMPORT
from sklearn import svm
from sklearn.metrics import f1_score
from sklearn.model_selection import StratifiedKFold
from sklearn.model_selection import cross_val_predict

# Function calculating fitness score
def fitnessCalculation(X, y, population, 
    cv_n=4, cv_shuffle=False, cv_n_jobs=15):

    scores = []
    classifier = svm.SVC(kernel='linear', C = 1)
    stratifiedKFold = StratifiedKFold(n_splits=cv_n, shuffle=cv_shuffle, random_state=0)
    for p in population: 
        y_pred = cross_val_predict(classifier, X[:,p], y, cv=stratifiedKFold, n_jobs=cv_n_jobs)
        score_weighted = f1_score(y, y_pred, average ="weighted")
        score_macro = f1_score(y, y_pred, average ="macro")
        scores.append([score_weighted, score_macro])
    return scores

