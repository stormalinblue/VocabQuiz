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
    word_definitions wd ON wp.id = wd.word_pos_id;