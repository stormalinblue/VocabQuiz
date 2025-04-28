begin transaction;

create table mcq_questions (
    id integer primary key autoincrement,
    context integer not null,
    generated_date integer not null,
    foreign key (context) references word_part_of_speech(id) on delete cascade
) strict;

create table mcq_responses (
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

end transaction;