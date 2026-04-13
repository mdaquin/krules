% Iris classification rules
big(X)       :- wide(X), long(X).
small(X)     :- narrow(X), short(X).
long(X)      :- elongated(X).
wide(X)      :- rounded(X).
versicolor(X) :- elongated(X), smooth(X).
setosa(X)    :- elongated(X), rough(X), small(X).
versicolor(X) :- elongated(X), rough(X), big(X).
versicolor(X) :- rounded(X), rough(X).
versicolor(X) :- rounded(X), smooth(X), small(X).
virginica(X)  :- rounded(X), smooth(X), big(X).

% Sample 1: rounded, smooth, long -> virginica
rounded(sample1).
smooth(sample1).
long(sample1).

% Sample 2: elongated, rough, narrow, short -> setosa
elongated(sample2).
rough(sample2).
narrow(sample2).
short(sample2).
