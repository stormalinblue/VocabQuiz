import numpy as np
import pandas as pd

from word_database import load_definition_table



class ThompsonSampler(object):
    '''
    Best = recommended for the user to find it easy to choose
           a matching action
    Worst = recommended for the user to find it easy to choose
            a mismatching action
    '''

    def __init__(self, index):
        num_items = index.shape[0]
        self.matches = pd.DataFrame(
            np.ones((num_items * num_items, 2)),
            index=pd.MultiIndex.from_product(
                [index, index],
                names=['context', 'action']),
            columns=['match', 'mismatch'])
    
    def add_match(self, context_index, action_index, weight=1):
        print('before', self.matches.loc[(context_index, action_index)])
        self.matches.loc[(context_index, action_index), 'match'] += weight
        print('after', self.matches.loc[(context_index, action_index)])

    def add_mismatch(self, context_index, action_index, weight=1):
        print('before', self.matches.loc[(context_index, action_index)])
        self.matches.loc[(context_index, action_index), 'mismatch'] += weight
        print('after', self.matches.loc[(context_index, action_index)])
    
    def recommend_worst_context(self, rng):
        # Find the parameters of the beta distribution of
        # the probability of choosing the correct action for the context.
        matches_index = self.matches.index
        self_matches = self.matches[
            matches_index.get_level_values('context')
            == matches_index.get_level_values('action')]
        # We are rewarding mismatches with 0 and matches with 1
        rewards = self_matches.apply(
            lambda x: rng.beta(x[0], x[1]),
            raw=True,
            axis=1)
        worst_context_index = rewards.idxmin()

        return worst_context_index[0], rewards.loc[worst_context_index] 

    def recommend_best_actions_for_context(self, rng, context_id, allowed_action_mask):
        action_set = self.matches.loc[(context_id, slice(None)), :].droplevel('context')
        # TODO: apply action mask
        masked_action_set = action_set[allowed_action_mask]
        rewards = masked_action_set.apply(
            lambda x: rng.beta(x[0], x[1]),
            raw=True,
            axis=1)
        return rewards.sort_values(
            ascending=False
        ).index.get_level_values('action')

class QuestionDB(object):
    def __init__(self, dict_filename):
        dictionary = load_definition_table(dict_filename)

        self.part_of_speech_groups = dictionary.groupby('partOfSpeech')
        parts_of_speech = self.part_of_speech_groups.groups.keys()

        self.samplers = {
            pos: ThompsonSampler(self.part_of_speech_groups.get_group(pos).index)
            for pos in parts_of_speech}

    def get_mcq(self, rng, recommended_size):
        min_reward = np.inf
        min_reward_pos = None
        min_reward_ctx = None
        
        for pos, sampler in self.samplers.items():
            ctx_id, reward = sampler.recommend_worst_context(rng)
            if reward < min_reward:
                min_reward = reward
                min_reward_pos = pos
                min_reward_ctx = ctx_id
        
        min_reward_group = (
            self.part_of_speech_groups
                .get_group(min_reward_pos))

        min_reward_row = min_reward_group.loc[min_reward_ctx]
        min_reward_word = min_reward_row['word']

        allowed_action_mask = min_reward_group['word'] != min_reward_word
        max_actions = self.samplers[
                min_reward_pos
            ].recommend_best_actions_for_context(
                rng,
                min_reward_ctx,
                allowed_action_mask)
    
        best_incorrect_answer_ids = max_actions[:recommended_size - 1]
        all_ids = np.concat([best_incorrect_answer_ids.values, [min_reward_ctx]])
        rng.shuffle(all_ids)
        return min_reward_pos, min_reward_ctx, min_reward_group.loc[all_ids]

    def register_mcq_response(self, pos, correct_id, chosen_id, all_option_ids):
        sampler = self.samplers[pos]
        
        for id in all_option_ids:
            print(id, chosen_id)
            if id == chosen_id:
                print('adding match')
                sampler.add_match(correct_id, chosen_id)
            else:
                print('adding mismatch')
                sampler.add_mismatch(correct_id, chosen_id)
        


if __name__ == '__main__':
    rng = np.random.default_rng()
    # index = np.arange(0, 10, dtype=np.int64)
    # gc = ThompsonSampler(index)

    # gc.add_match(0, 1)
    # gc.add_mismatch(0, 0)
    # print(gc.matches)
    # print(gc.recommend_worst_context(rng))
    # print(gc.recommend_best_actions_for_context(rng, 0))

    qdb = QuestionDB('words2.yaml')
    qdb.get_mcq(rng, 4)