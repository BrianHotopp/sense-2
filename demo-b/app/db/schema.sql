drop table if exists plaintexts;
create table plaintexts (
    id integer primary key autoincrement,
    name varchar not null,
    description varchar not null,
    -- path to the original plaintext
    p_path varchar not null,
    -- path to the scrubbed plaintext
    s_path varchar not null,
    -- path to the tokenized plaintext 
    t_path varchar not null,
    occ_path varchar not null

);

drop table if exists embeddings;
create table embeddings (
  id integer primary key autoincrement,
  name varchar not null,
  description varchar not null,
  pt_id integer not null,
  -- path to the embedding
  wv_path varchar not null,
  -- foreign key constraint, if we delete plaintext delete associated embeddings
  foreign key (pt_id) references plaintexts(id) on delete cascade
);

drop table if exists alignments;
create table alignments (
  id integer primary key autoincrement,
  name string not null,
  description varchar not null,
  e1_id integer not null,
  e2_id integer not null,
  -- path to common words
  c_path varchar not null,
  -- path to the first aligned embedding
  v1_path varchar not null,
  -- path to the secondn aligned embeddings
  v2_path varchar not null,
  -- path to shifts
  s_path varchar not null,
  -- path to dists
  d_path varchar not null,
  -- path to q
  q_path varchar not null,
  -- foreign key constraints, on delete cascade
  foreign key (e1_id) references embeddings(id) on delete cascade
  foreign key (e2_id) references embeddings(id) on delete cascade
);