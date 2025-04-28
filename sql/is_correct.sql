select
        log.id, log.question_id, q.context, r.response_index, r.response_id
    from
        mcq_log as log
        inner join
            mcq_questions as q
            on q.id = log.question_id
        inner join mcq_responses as r
            on q.id = r.question_id
        inner join word_definitions as wd
            on wd.id = r.response_id
    -- where
        -- log.id = 3
        -- and r.response_index = 1
        -- and q.context = wd.word_pos_id