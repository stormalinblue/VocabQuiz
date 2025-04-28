
CREATE TABLE words (
    id integer primary key AUTOINCREMENT,
    word text not null unique) strict;

CREATE TABLE parts_of_speech (
    id integer primary key AUTOINCREMENT,
    name text not null unique) strict;
CREATE TABLE word_parts_of_speech (
    id integer primary key AUTOINCREMENT,
    word_id integer not null,
    part_of_speech_id integer not null,
    foreign key (word_id) references words(id) on delete cascade,
    foreign key (part_of_speech_id) references part_of_speech(id) on delete cascade,
    unique (word_id, part_of_speech_id)) strict;
CREATE TABLE word_definitions (
    id integer primary key AUTOINCREMENT,
    word_pos_id integer not null,
    foreign key (word_pos_id) references word_part_of_speech(id) on delete cascade) strict;
CREATE TABLE definition_revisions (
    id integer primary key AUTOINCREMENT,
    definition_id integer not null,
    definition_text text not null,
    source text,
    license text,
    add_date text not null,
    foreign key (definition_id) references word_definitions(id) on delete cascade
) strict;
CREATE TABLE synonym_groups (
    id integer primary key AUTOINCREMENT
) strict;
CREATE TABLE synonymous_definitions (
    group_id integer not null,
    definition_id integer not null,
    foreign key (group_id) references synonym_groups(id) on delete cascade,
    foreign key (definition_id) references word_definitions(id) on delete cascade,
    primary key (group_id, definition_id)
) strict;
CREATE TABLE synonymous_word_pos (
    group_id integer not null,
    word_pos_id integer not null,
    foreign key (group_id) references synonym_groups(id) on delete cascade,
    foreign key (word_pos_id) references word_parts_of_speech(id) on delete cascade,
    primary key (group_id, word_pos_id)
) strict;
CREATE TABLE synonymous_words (
    group_id integer not null,
    word_id integer not null,
    foreign key (group_id) references synonym_groups(id) on delete cascade,
    foreign key (word_id) references words(id) on delete cascade,
    primary key (group_id, word_id)
) strict;
CREATE TABLE mcq_questions (
    id integer primary key autoincrement,
    context integer not null,
    generated_date integer not null,
    foreign key (context) references word_part_of_speech(id) on delete cascade
) strict;
CREATE TABLE mcq_responses (
    response_index integer not null,
    question_id integer not null,
    response_id integer not null,
    foreign key (question_id)
        references mcq_questions(id)
        on delete cascade,
    foreign key (response_id)
        references word_definitions(id)
        on delete cascade,
    primary key (question_id, response_index),
    unique (question_id, response_index)
) strict;
CREATE TABLE users (
    id integer primary key autoincrement,
    user_name text,
    unique (user_name)
) strict;
CREATE TABLE mcq_log (
    id integer primary key autoincrement,
    user_id integer not null,
    question_id integer not null,
    presentation_date integer not null,
    constraint fk_users
        foreign key (user_id)
        references users
        on delete cascade,
    foreign key (question_id) references mcq_questions(id) on delete cascade,
    unique (id, question_id)
) strict;
CREATE VIEW latest_definitions
as 
    select word_pos_id, dr.* from (
        select wd.word_pos_id as word_pos_id, max(dr.id) as latest_definition_id
        from definition_revisions as dr
        inner join word_definitions as wd on wd.id = dr.definition_id
        group by dr.definition_id)
    inner join
        definition_revisions as dr
        on dr.id == latest_definition_id
/* latest_definitions(word_pos_id,id,definition_id,definition_text,source,license,add_date) */;
CREATE VIEW definition_groups AS
/* definitions */
SELECT 
    sd.definition_id,
    sd.group_id
FROM 
    synonymous_definitions sd

UNION ALL

/* words */
SELECT 
    wd.id,
    sw.group_id
FROM 
    words w
JOIN 
    synonymous_words sw ON w.id = sw.word_id
JOIN 
    word_parts_of_speech wp ON w.id = wp.word_id
JOIN 
    word_definitions wd ON wp.id = wd.word_pos_id

UNION ALL

SELECT 
    wd.id,
    swp.group_id
FROM 
    word_parts_of_speech wp
JOIN 
    synonymous_word_pos swp ON wp.id = swp.word_pos_id
JOIN 
    word_definitions wd ON wp.id = wd.word_pos_id
/* definition_groups(definition_id,group_id) */;
CREATE TABLE mcq_log_responses (
    mcq_log_id integer not null,
    question_id integer not null,
    response_index integer not null,
    constraint fk_mcq_logs
        foreign key (mcq_log_id, question_id)
        references mcq_log(id, question_id)
        on delete cascade,
    foreign key (question_id, response_index)
        references mcq_responses(question_id, response_index)
        on delete cascade
) strict;
