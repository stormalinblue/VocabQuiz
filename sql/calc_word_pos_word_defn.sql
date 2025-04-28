create view word_pos_word_defn_selectedness as select
    mcq_log.user_id as user_id,
    mcq_questions.context as word_pos_id,
    mcq_responses.response_id as wd_id,
    mcq_log.presentation_date as response_date,
    mcq_log_responses.response_index is not null as selected
from
    (select * from mcq_log
        join (
            select distinct mcq_log_responses.mcq_log_id
            from mcq_log_responses)
            on mcq_log_id = mcq_log.id) as mcq_log
    inner join mcq_questions
        on mcq_questions.id = mcq_log.question_id
    inner join mcq_responses
        on mcq_responses.question_id = mcq_log.question_id
    left join mcq_log_responses
        on mcq_log.id = mcq_log_responses.mcq_log_id
        and mcq_responses.response_index = mcq_log_responses.response_index
order by user_id, word_pos_id, wd_id;