create view latest_definitions
as 
    select word_pos_id, dr.* from (
        select wd.word_pos_id as word_pos_id, max(dr.id) as latest_definition_id
        from definition_revisions as dr
        inner join word_definitions as wd on wd.id = dr.definition_id
        group by dr.definition_id)
    inner join
        definition_revisions as dr
        on dr.id == latest_definition_id;