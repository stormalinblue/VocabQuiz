select
    word_parts_of_speech.id as word_pos_id,
    response_wd.word_pos_id = mcq_questions.context as correct,
    mcq_log.presentation_date as response_date
from
mcq_log_responses as mcq_log_responses
join mcq_log
    on mcq_log.id = mcq_log_responses.mcq_log_id
join mcq_questions
    on mcq_log.question_id = mcq_questions.id
join word_parts_of_speech
    on mcq_questions.context = word_parts_of_speech.id
join mcq_responses
    on mcq_responses.response_index = mcq_log_responses.response_index
    and mcq_responses.question_id = mcq_log_responses.question_id
join word_definitions as response_wd
    on mcq_responses.response_id = response_wd.id
where
mcq_log.user_id = 1
order by word_pos_id

