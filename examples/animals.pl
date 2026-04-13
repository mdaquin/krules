% Animal identification knowledge base
% Inspired by the classic AI expert system example (Bratko, Nilsson)

% --- Intermediate categories ---

% A mammal has hair or gives milk
mammal(X) :- has_hair(X).
mammal(X) :- gives_milk(X).

% A bird has feathers, or flies and lays eggs
bird(X) :- has_feathers(X).
bird(X) :- flies(X), lays_eggs(X).

% A carnivore is a mammal that eats meat,
% or an animal with pointed teeth, claws and forward-facing eyes
carnivore(X) :- mammal(X), eats_meat(X).
carnivore(X) :- has_pointed_teeth(X), has_claws(X), forward_eyes(X).

% An ungulate is a mammal with hooves, or a mammal that chews cud
ungulate(X) :- mammal(X), has_hooves(X).
ungulate(X) :- mammal(X), chews_cud(X).

% --- Species ---

cheetah(X)   :- carnivore(X), tawny(X), black_spots(X).
tiger(X)     :- carnivore(X), tawny(X), black_stripes(X).
giraffe(X)   :- ungulate(X), long_neck(X), tawny(X), dark_spots(X).
zebra(X)     :- ungulate(X), black_stripes(X).
ostrich(X)   :- bird(X), long_neck(X), long_legs(X), black_and_white(X).
penguin(X)   :- bird(X), swims(X), black_and_white(X).
albatross(X) :- bird(X), long_wings(X), soars_at_sea(X).
