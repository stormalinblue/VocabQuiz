create view candidate_mcq_false_options as
    select
        wp.id as action_id,
        d.id as response_id
    from
        word_parts_of_speech as wp
        inner join
            latest_definitions as d
            on d.word_pos_id != wp.id;