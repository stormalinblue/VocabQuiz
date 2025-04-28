select
    user.id as user_id,
    question_id as context_id,
    sum(does_match) as matches_weight,
    count(*) - sum(does_match) as does_not_match_weight,
from
    select ()
    