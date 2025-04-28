SELECT
    w.id,
    p.id,
    w.word,
    p.name as part_of_speech,
    dr.definition_text
    -- p.name as part_of_speech, 
    -- dr.definition_text
FROM
    latest_definitions as dr
inner join
    word_definitions as wd
    on wd.id = dr.id
inner join
    word_parts_of_speech as wp
    on wp.id = wd.word_pos_id
inner join
    words as w, parts_of_speech as p
    on w.id = wp.word_id and p.id = wp.part_of_speech_id
ORDER BY
    w.word, p.name
;