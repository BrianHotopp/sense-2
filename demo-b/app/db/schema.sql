drop table if exists plaintexts;
create table plaintexts (
    id integer primary key autoincrement,
    name varchar not null,
    description varchar not null,
    p_path varchar not null,
    s_path varchar not null
);
drop table if exists embeddings;
create table embeddings (
  id integer primary key autoincrement,
  name varchar not null,
  description varchar not null,
  pt_id integer not null,
  -- foreign key constraint, if we delete plaintext delete associated embeddings
  foreign key (pt_id) references plaintexts(id) on delete cascade
);
drop table if exists e_vectors;
create table e_vectors (
  e_id integer not null,
  word varchar not null,
  vector blob not null,
  -- primary key on e_id and word
  primary key (e_id, word)
  -- foreign key constraints, if we delete the associated embedding delete its vectors
  foreign key (e_id) references embeddings(id) on delete cascade
);
drop table if exists alignments;
create table alignments (
  id integer primary key autoincrement,
  name string not null,
  description varchar not null,
  e1_id integer not null,
  e2_id integer not null,
  -- foreign key constraints, on delete cascade
  foreign key (e1_id) references embeddings(id) on delete cascade
  foreign key (e2_id) references embeddings(id) on delete cascade
);
drop table if exists a_vectors;
create table a_vectors (
  a_id integer not null,
  -- foreign key constraints, on delete cascade
  first boolean not null,
  word varchar not null,
  vector blob not null,
  primary key (a_id, first, word)
  foreign key (a_id) references alignments(id) on delete cascade
);
drop table if exists dists;
create table dists (
  a_id integer not null,
  word1 varchar not null,
  word2 varchar not null,
  dist float not null,
  primary key (a_id, word1, word2)
  -- foreign key constraints, on delete cascade
  foreign key (a_id) references alignments(id) on delete cascade
);
drop table if exists shifts;
create table shifts (
  a_id integer not null,
  word varchar not null,
  shift float not null,
  primary key (a_id, word)
  -- foreign key constraints, on delete cascade
  foreign key (a_id) references alignments(id) on delete cascade

);
