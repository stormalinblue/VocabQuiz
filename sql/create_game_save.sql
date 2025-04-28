create table users (
    id integer primary key autoincrement,
    user_name text,
    unique (user_name)
) strict;

create table mcq_log (
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

create table mcq_log_responses (
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