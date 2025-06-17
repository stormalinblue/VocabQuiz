import math
import random
import sqlite3
from typing import Callable, Iterable, Any

import pandas as pd
import numpy as np

from ..common import exceptions
from ..user.model import User

LAMBDA: float = math.log(1 - 0.02)
PRIOR_CORRECT: float = 0.25
PRIOR_INCORRECT: float = 0.75
SECONDS_IN_DAY = 86400

def decay_sum(table: pd.DataFrame, current_time: float, decay_factor: float) -> float:
    return np.sum(np.exp(decay_factor * (current_time - table) / SECONDS_IN_DAY))

def decay_sum_wp(table: pd.DataFrame, current_time: float, decay_factor: float) -> pd.DataFrame:
    return table.groupby('word_pos_id').aggregate(lambda x: decay_sum(x, current_time, decay_factor))

def decay_sum_wd(table: pd.DataFrame, current_time: float, decay_factor: float):
    return table.groupby('definition_id').aggregate(lambda x: decay_sum(x, current_time, decay_factor))

def word_weight_table(
        connection: sqlite3.Connection,
        user_id: int,
        timestamp: int,
        decay_factor: float = LAMBDA,
        prior_correct: float = PRIOR_CORRECT,
        prior_incorrect: float = PRIOR_INCORRECT):
    word_definition_query = '''
    select
        wp.id as word_pos_id, ? as correct, ? as incorrect
        from word_parts_of_speech as wp
    order by wp.id'''
    word_weight_table = pd.read_sql(
        word_definition_query,
        params=(0.0, 0.0),
        con=connection,
        index_col='word_pos_id')

    correct_query = '''
    select
        word_pos_id, response_date as weight
        from word_pos_correctness
    where
        user_id = ?
        and correct'''
    correct_table = pd.read_sql(
        correct_query,
        params=(user_id,),
        con=connection)
    correct_sum = decay_sum_wp(correct_table, timestamp, decay_factor)

    incorrect_query = '''
    select
        word_pos_id, response_date as weight
        from word_pos_correctness
    where
        user_id = ?
        and not correct'''
    incorrect_table = pd.read_sql(
        incorrect_query,
        params=(user_id,),
        con=connection)
    incorrect_sum = decay_sum_wp(incorrect_table, timestamp, decay_factor)

    word_weight_table['correct'] = np.maximum(
        word_weight_table['correct'].add(
            correct_sum['weight'],
            fill_value=0
        ).subtract(
            incorrect_sum['weight'],
            fill_value=0
        ), prior_correct)
    word_weight_table['incorrect'] = np.maximum(word_weight_table['incorrect'].add(
        incorrect_sum['weight'],
        fill_value=0), prior_incorrect)
    return word_weight_table


class GameModel(object):
    def __init__(self, connection: sqlite3.Connection):
        self.connection = connection
    
    def _get_question_id(self, user: User, timestamp: int):
        word_table = word_weight_table(self.connection, user.user_id, timestamp)
        word_weights = word_table.apply(
            lambda x: random.betavariate(x[0], x[1]),
            raw=True,
            axis=1)
        word_id = word_weights.idxmin()
        print('word weight table')
        print(word_table.loc[word_id])
        print('word weight', word_weights.loc[word_id])
        return int(word_id)

    def _get_choices(
            self,
            user: User,
            word_pos_id: int,
            timestamp: int,
            decay_factor: float = LAMBDA,
            prior_correct: float = PRIOR_CORRECT,
            prior_incorrect: float = PRIOR_INCORRECT,
            num_options: int=4):
        src_defn_query = '''
        select
            wd.id as definition_id, ? as selected, ? as not_selected
        from word_definitions as wd
        where wd.word_pos_id = (?)
        order by definition_id
        '''
        src_defn_weight_table = pd.read_sql_query(
            src_defn_query,
            params=(prior_correct, prior_incorrect, word_pos_id,),
            con=self.connection,
            index_col='definition_id')
        
        src_selected_query = '''
        select
            src.id as definition_id, response_date as weight
        from
            word_definitions as src
            inner join word_pos_word_defn_selectedness as selectedness
                on selectedness.wd_id = src.id
                and src.word_pos_id = selectedness.word_pos_id
        where selectedness.selected
            and selectedness.user_id = ?
            and src.word_pos_id = ?
        order by definition_id
        '''
        src_selected_weight_table = pd.read_sql(
            src_selected_query,
            params=(user.user_id, word_pos_id),
            con=self.connection)
        src_selected_sum = decay_sum_wd(src_selected_weight_table, timestamp, decay_factor)

        src_not_selected_query = '''
        select
            src.id as definition_id, response_date as weight
        from
            word_definitions as src
            inner join word_pos_word_defn_selectedness as selectedness
                on selectedness.wd_id = src.id
                and src.word_pos_id = selectedness.word_pos_id
        where not selectedness.selected
            and selectedness.user_id = ?
            and src.word_pos_id = ?
        order by definition_id
        '''
        src_not_selected_weight_table = pd.read_sql(
            src_not_selected_query,
            params=(user.user_id, word_pos_id),
            con=self.connection)
        src_not_selected_sum = decay_sum_wd(src_not_selected_weight_table, timestamp, decay_factor)

        src_defn_weight_table['selected'] = src_defn_weight_table['selected'].add(
            src_selected_sum['weight'],
            fill_value=0)
        src_defn_weight_table['not_selected'] = src_defn_weight_table['not_selected'].add(
            src_not_selected_sum['weight'],
            fill_value=0)
        
        src_defn_id = int(src_defn_weight_table.apply(
            lambda x: random.betavariate(x['selected'], x['not_selected']),
            axis=1).idxmin())

        alt_defn_id_query = '''
        select alt_defn_id as definition_id, ? as selected, ? as not_selected
        from definition_alternatives
        where source_defn_id = ?
        order by definition_id
        '''
        alt_defn_weight_table = pd.read_sql(
            alt_defn_id_query,
            params=(prior_correct, prior_incorrect, src_defn_id,),
            con=self.connection,
            index_col='definition_id')
        if alt_defn_weight_table.shape[0] != 0:
            alt_selected_query = '''
            select
                alt_defn_id as definition_id, response_date as weight
            from
                definition_alternatives as alt
                inner join word_pos_word_defn_selectedness as selectedness
                    on selectedness.wd_id = alt.alt_defn_id
            where selectedness.selected
                and selectedness.user_id = ?
                and selectedness.word_pos_id = ?
                and alt.source_defn_id = ?
            order by definition_id
            '''
            alt_selected_weight_table = pd.read_sql(
                alt_selected_query,
                params=(user.user_id, word_pos_id, src_defn_id),
                con=self.connection,
                index_col='definition_id')
            alt_selected_sum = decay_sum_wd(alt_selected_weight_table, timestamp, decay_factor)
            
            alt_not_selected_query = '''
            select
                alt_defn_id as definition_id, response_date as weight
            from
                definition_alternatives as alt
                inner join word_pos_word_defn_selectedness as selectedness
                    on selectedness.wd_id = alt.alt_defn_id
            where not selectedness.selected
                and selectedness.user_id = ?
                and selectedness.word_pos_id = ?
                and alt.source_defn_id = ?
            order by definition_id
            '''
            alt_not_selected_weight_table = pd.read_sql(
                alt_not_selected_query,
                params=(user.user_id, word_pos_id, src_defn_id),
                con=self.connection,
                index_col='definition_id')
            alt_not_selected_sum = decay_sum_wd(alt_not_selected_weight_table, timestamp, decay_factor)

            alt_defn_weight_table['selected'] = alt_defn_weight_table['selected'].add(
                alt_selected_sum['weight'],
                fill_value=0)
            alt_defn_weight_table['not_selected'] = alt_defn_weight_table['not_selected'].add(
                alt_not_selected_sum['weight'],
                fill_value=0)
            
            # TODO: Sample and choose min
            beta_sample: Callable[[Any], float] = lambda x: random.betavariate(x['selected'], x['not_selected'])
            # print('alt defn weight table shape', alt_defn_weight_table.shape)
            # if alt_defn_weight_table.shape[0] == 0:
            #     print('word_pos_id', word_pos_id, 'src_defn_id', src_defn_id, 'has empty weight table')
            rewards = alt_defn_weight_table.apply(
                beta_sample,
                axis=1)
            best_alternates: pd.Index[int] = rewards.sort_values(ascending=True).index.get_level_values('definition_id')[:num_options - 1]

            alternate_options = [int(defn_id) for defn_id in best_alternates]
        else:
            alternate_options = []

        all_options = [src_defn_id] + alternate_options
        random.shuffle(all_options)
        return all_options

    def create_question(self, user: User, now_timestamp: int):
        cur = self.connection.cursor()

        timestamp = now_timestamp
        word_pos_id = self._get_question_id(user, timestamp)
        presented_options = self._get_choices(user, word_pos_id, timestamp)

        question = {
            'word_pos_id': word_pos_id,
            'presented_options': presented_options,
        }

        question_id = self._register_question(cur, question, timestamp)
        presentation_id = self._create_presentation(cur, user, question_id, timestamp)
        self.connection.commit()

        return presentation_id

    def _register_question(self, cur: sqlite3.Cursor, question, timestamp: int) -> int:
        cur = self.connection.cursor()
        question_id = cur.execute('''
            insert into mcq_questions
                (context, generated_date)
                values (?, ?)
                returning mcq_questions.id
            ''', (question['word_pos_id'], timestamp)).fetchone()[0]
    
        for list_index, definition_id in enumerate(question['presented_options']):
            cur.execute('''
                insert into mcq_responses
                    (response_index, question_id, response_id)
                    values (?, ?, ?)
                ''', (list_index, question_id, definition_id))
        
        return question_id
    
    def _create_presentation(self, cur: sqlite3.Cursor, user: User, question_id: int, timestamp: int) -> int:
        return cur.execute('''
            insert into mcq_log
                (user_id, question_id, presentation_date)
                values (?, ?, ?) returning id''', (user.user_id, question_id, timestamp)).fetchone()[0]

    def get_presentation_info(self, user: User, presentation_id: int):
        cur = self.connection.cursor()
        word, part_of_speech = cur.execute(
        '''
        select words.word as word, pos.name as part_of_speech
        from mcq_log
            join mcq_questions on mcq_questions.id = mcq_log.question_id
            join word_parts_of_speech as word_pos on word_pos.id = mcq_questions.context
            join words on words.id = word_pos.word_id
            join parts_of_speech as pos on pos.id = word_pos.part_of_speech_id
        where mcq_log.user_id = ?
            and mcq_log.id = ?
        ''', (user.user_id, presentation_id)).fetchone()
        
        option_query = '''
        select
            response_index as option_index,
            ld.definition_id as definition_id,
            ld.definition_text as text,
            words.word as word,
            pos.name as part_of_speech
        from mcq_log
            join mcq_responses on mcq_responses.question_id = mcq_log.question_id
            join latest_definitions as ld on ld.definition_id = mcq_responses.response_id
            join word_parts_of_speech as word_pos on word_pos.id = ld.word_pos_id
            join words on words.id = word_pos.word_id
            join parts_of_speech as pos on pos.id = word_pos.part_of_speech_id
        where mcq_log.user_id = ?
            and mcq_log.id = ?
        order by option_index
        '''
        options_table = pd.read_sql(
            option_query,
            params=(user.user_id, presentation_id),
            con=self.connection,
            index_col='option_index')
        
        return {
            'question': {
                'word': word,
                'part_of_speech': part_of_speech
            },
            'options': options_table}
    
 

    def re_presentation(self, user: User, presentation_id: int, now_timestamp: int):
        with self.connection:
            cur = self.connection.cursor()
            results = cur.execute('''
                select question_id from mcq_log where
                    mcq_log.id = ? and mcq_log.user_id = ?''', (presentation_id, user.user_id)).fetchall()
            
            if not results:
                raise exceptions.NotFound

            question_id = results[0][0]

            new_presentation_id: int = cur.execute('''
                insert into mcq_log
                    (user_id, question_id, presentation_date)
                    values (?, ?, ?)
                    returning id''',
                    (user.user_id, question_id, now_timestamp)).fetchone()[0]

            return new_presentation_id

    def _is_authorized_for_presentation(self, cur: sqlite3.Cursor, user: User, presentation_id: int):
        authorized = cur.execute(
            '''
            select count(*) from mcq_log where id = ? and user_id = ?''',
            (presentation_id, user.user_id)
        ).fetchone()[0] == 1
        return authorized

    def is_correct_answer(self, user: User, presentation_id: int, response_index: int) -> bool:
        cur = self.connection.cursor()
        if not self._is_authorized_for_presentation(cur, user, presentation_id):
            raise exceptions.NotAuthorized
    
        result = cur.execute(
            '''
            select
                case when
                    count(*) > 0 then 1
                    else 0
                end as is_correct
            from
                mcq_log as log
                inner join
                    mcq_questions as q
                    on q.id = log.question_id
                inner join mcq_responses as r
                    on q.id = r.question_id
                inner join word_definitions as wd
                    on wd.id = r.response_id
            where
                log.id = ?
                and r.response_index = ?
                and q.context = wd.word_pos_id
            ''',
            (presentation_id, response_index)
        ).fetchone()[0]
        return result

    def create_user_response(self, user: User, presentation_id: int, responses: Iterable[int]):
        cur = self.connection.cursor()
        if not self._is_authorized_for_presentation(cur, user, presentation_id):
            raise exceptions.NotAuthorized
        
        question_id: int = cur.execute(
            '''select question_id from mcq_log where mcq_log.id = ?''', (presentation_id,)).fetchone()[0]

        for response_index in responses:
            cur.execute('''
                insert into mcq_log_responses
                    (mcq_log_id, question_id, response_index)
                    values (?, ?, ?)''',
                (presentation_id, question_id, response_index))
        
        self.connection.commit()
