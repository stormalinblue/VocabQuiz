select
        source_defns.id as source_defn_id, alt_defns.id as alt_defn_id
        from word_parts_of_speech as alt_word_pos
        inner join word_parts_of_speech as source_word_pos
            on (source_word_pos.part_of_speech_id = alt_word_pos.part_of_speech_id)
            and (source_word_pos.id <> alt_word_pos.id)
        inner join word_definitions as source_defns
            on source_defns.word_pos_id = source_word_pos.id
        inner join word_definitions as alt_defns
            on alt_defns.word_pos_id = alt_word_pos.id
where source_defn_id = 33;