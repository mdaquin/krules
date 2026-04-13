dog(Y) :- parent(X,Y), dog(X).
dog(suzette).
dog(pepper).
female(cider).
female(suzette).
male(ace).
male(pepper).
mother(X,Y) :- parent(X,Y), female(X).
daughter(Y,X) :- parent(X,Y), female(Y).
father(X,Y) :- parent(X,Y), male(X).
son(Y,X) :- parent(X,Y), male(Y).
parent(pepper, cider).
parent(suzette, cider).
parent(pepper, ace).
parent(suzette, ace).
