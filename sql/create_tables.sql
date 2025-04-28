begin transaction;

create table words (
    id integer primary key AUTOINCREMENT,
    word text not null unique) strict;

create table parts_of_speech (
    id integer primary key AUTOINCREMENT,
    name text not null unique) strict;

create table word_parts_of_speech (
    id integer primary key AUTOINCREMENT,
    word_id integer not null,
    part_of_speech_id integer not null,
    foreign key (word_id) references words(id) on delete cascade,
    foreign key (part_of_speech_id) references part_of_speech(id) on delete cascade,
    unique (word_id, part_of_speech_id)) strict;

create table word_definitions (
    id integer primary key AUTOINCREMENT,
    word_pos_id integer not null,
    foreign key (word_pos_id) references word_part_of_speech(id) on delete cascade) strict;

create table definition_revisions (
    id integer primary key AUTOINCREMENT,
    definition_id integer not null,
    definition_text text not null,
    source text,
    license text,
    add_date text not null,
    foreign key (definition_id) references word_definitions(id) on delete cascade
) strict;

create table synonym_groups (
    id integer primary key AUTOINCREMENT
) strict;

create table synonymous_definitions (
    group_id integer not null,
    definition_id integer not null,
    foreign key (group_id) references synonym_groups(id) on delete cascade,
    foreign key (definition_id) references word_definitions(id) on delete cascade,
    primary key (group_id, definition_id)
) strict;

create table synonymous_word_pos (
    group_id integer not null,
    word_pos_id integer not null,
    foreign key (group_id) references synonym_groups(id) on delete cascade,
    foreign key (word_pos_id) references word_parts_of_speech(id) on delete cascade,
    primary key (group_id, word_pos_id)
) strict;

create table synonymous_words (
    group_id integer not null,
    word_id integer not null,
    foreign key (group_id) references synonym_groups(id) on delete cascade,
    foreign key (word_id) references words(id) on delete cascade,
    primary key (group_id, word_id)
) strict;

commit;