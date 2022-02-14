import pickle as pkl
import pandas as pd
import matplotlib.pyplot as plt


# ---------------------
#    load pkl file
# ---------------------


with open("/Users/jonas/python/old/challengers.pkl", "rb") as f:
    object = pkl.load(f)
df = pd.DataFrame(object)


# ------------------------------------------
#   make lists with relevant, decoded data
# ------------------------------------------


help_challenge = []
help_challenger = []

for y in df["args"]:
    help_challenge.append(y['checkName'].decode('utf-8').rstrip('\x00'))
    help_challenger.append(y['user'])

list_challenge = pd.Series(help_challenge).tolist()
list_challenger = pd.Series(help_challenger).tolist()


# -----------------------------------------------------------
#       merge lists into df and format for readability
# -----------------------------------------------------------


clean_df = pd.DataFrame(zip(list_challenger, list_challenge), columns=['user_address',
                        'challenge'])

REMAP_CLASS = {
    'poap': 'challenge1',
    'sybilList': 'challenge2',
    'bankless': 'challenge4',
    'govVoters': 'challenge3',
    'communityCalls': 'challenge4',
    'highInvolvement': 'challenge4',
    "additionalPOAPs": 'challenge4',
    'github': 'challenge6-github',
    'phone': 'challenge6-phone',
    'twitter': 'challenge6-twitter',
    'discord1': 'invalid',
    'privacyPolicy': 'privPolicy',
    'stackOvFl': 'challenge7-stack',
    'githubFollowers': 'challenge7-git',
    'discord-challenge-1': 'challenge5',
    'twitterFollowers': 'challenge7-twitter',
    'instagram': 'challenge7-ig',
    'reddit': 'challenge7-reddit',
    'fb': 'challenge7-fb',
    'twitter-standardised': 'challenge6-twitter',
    'github-standardised': 'challenge6-github',
    'coinbase': 'challenge8-coinbase',
    'discord': 'challenge8-contributors',
    'megaWhitelist': 'challenge8-defiwl',
    'minecraft': 'challenge7-minecraft',
    'goldfinchKYC': 'challenge8-goldfinch'}

clean_df['challenge'] = clean_df['challenge'].map(REMAP_CLASS)


# -------------------------------------------------------------------
#       group challenges by address
# -------------------------------------------------------------------


grouped_df = clean_df.groupby('user_address')['challenge'].apply(
    list).reset_index(name='passed_challenges')


# -------------------------------------------------------------------
#       count challenges by address
# -------------------------------------------------------------------


def count_challenges(df: pd.DataFrame):

    counted_df = {'address': [], 'ch_1': [], 'ch_2': [], 'ch_3': [], 'ch_4': [
    ], 'ch_5': [], 'ch_6_twitter': [], 'ch_6_github': [
    ], 'ch_6_phone': [], 'ch_7_stack': [], 'ch_7_git': [], 'ch_7_twitter': [], 'ch_7_reddit': [], 'ch_7_minecraft': [
    ], 'ch_8_goldfinch': [], 'ch_8_defiwl': [], 'ch_8_contributors': [], 'ch_8_coinbase': [], 'privPolicy': []}

    for i, item in enumerate(grouped_df.iloc):

        counted_df['address'].append(item['user_address'])
        challenges = item['passed_challenges']
        # append counts into df
        counted_df['ch_1'].append(challenges.count('challenge1'))
        counted_df['ch_2'].append(challenges.count('challenge2'))
        counted_df['ch_3'].append(challenges.count('challenge3'))
        counted_df['ch_4'].append(challenges.count('challenge4'))
        counted_df['ch_5'].append(challenges.count('challenge5'))
        counted_df['ch_6_twitter'].append(
            challenges.count('challenge6-twitter'))
        counted_df['ch_6_github'].append(challenges.count('challenge6-github'))
        counted_df['ch_6_phone'].append(challenges.count('challenge6-phone'))
        counted_df['ch_7_stack'].append(challenges.count('challenge7-stack'))
        counted_df['ch_7_git'].append(challenges.count('challenge7-git'))
        counted_df['ch_7_twitter'].append(
            challenges.count('challenge7-twitter'))
        counted_df['ch_7_reddit'].append(challenges.count('challenge7-reddit'))
        counted_df['ch_7_minecraft'].append(
            challenges.count('challenge7-minecraft'))

        counted_df['ch_8_goldfinch'].append(
            challenges.count('challenge8-goldfinch'))
        counted_df['ch_8_defiwl'].append(challenges.count('challenge8-defiwl'))
        counted_df['ch_8_contributors'].append(
            challenges.count('challenge8-contributors'))
        counted_df['ch_8_coinbase'].append(
            challenges.count('challenge8-coinbase'))

        counted_df['privPolicy'].append(challenges.count('privPolicy'))

    return pd.DataFrame(counted_df)


# ------------------------------------------
#        apply weights
# ------------------------------------------


def apply_weights(df: pd.DataFrame):
    weighted_df = {}
    weights = {'address': [], 'w1': 3, 'w2': 2, 'w3': 2, 'w4': 1, 'w5': 3,
               'w6_twitter': 2, 'w6_github': 2, 'w6_phone': 3, 'w7_stack': 3,
               'w7_git': 2, 'w7_twitter': 2, 'w7_reddit': 2, 'w7_minecraft': 1,
               'w8_goldfinch': 3, 'w8_defiwl': 2, 'w8_contributors': 2, 'w8_coinbase': 3, 'wprivPolicy': 1}

    weighted_df['address'] = df['address']
    weighted_df['w_ch_1'] = df['ch_1']*weights['w1']
    weighted_df['w_ch_2'] = df['ch_2']*weights['w2']
    weighted_df['w_ch_3'] = df['ch_3']*weights['w3']
    weighted_df['w_ch_4'] = df['ch_4']*weights['w4']
    weighted_df['w_ch_5'] = df['ch_5']*weights['w5']

    weighted_df['w_ch_6_twitter'] = df['ch_6_twitter']*weights['w6_twitter']
    weighted_df['w_ch_6_github'] = df['ch_6_github']*weights['w6_github']
    weighted_df['w_ch_6_phone'] = df['ch_6_phone']*weights['w6_phone']

    weighted_df['w_ch_7_stack'] = df['ch_7_stack']*weights['w7_stack']
    weighted_df['w_ch_7_git'] = df['ch_7_git']*weights['w7_git']
    weighted_df['w_ch_7_twitter'] = df['ch_7_twitter']*weights['w7_twitter']
    weighted_df['w_ch_7_reddit'] = df['ch_7_reddit']*weights['w7_reddit']
    weighted_df['w_ch_7_minecraft'] = df['ch_7_minecraft'] * \
        weights['w7_minecraft']

    weighted_df['w_ch_8_goldfinch'] = df['ch_8_goldfinch'] * \
        weights['w8_goldfinch']
    weighted_df['w_ch_8_defiwl'] = df['ch_8_defiwl']*weights['w8_defiwl']
    weighted_df['w_ch_8_contributors'] = df['ch_8_contributors'] * \
        weights['w8_contributors']
    weighted_df['w_ch_8_coinbase'] = df['ch_8_coinbase']*weights['w8_coinbase']

    weighted_df['wprivPolicy'] = df['privPolicy']*weights['wprivPolicy']

    return pd.DataFrame(weighted_df)


# ------------------------------------------
#        score address
# ------------------------------------------


def score_addresses(df: pd.DataFrame):
    scored_df = {}
    col_list = list(df)

    col_list.remove('wprivPolicy')
    scored_df['address'] = df['address']
    col_list.remove('address')
    scored_df['score'] = df[col_list].sum(axis=1)

    return pd.DataFrame(scored_df)


def main_function(df: pd.DataFrame):
    counted_df = count_challenges(df)
    weighted_df = apply_weights(counted_df)
    scored_df = score_addresses(weighted_df)

# ------------------------------------------------------
#       edit threshold & 'activate' below snippet
# ------------------------------------------------------

    # score_threshold = 3

    # scored_df.loc[scored_df['score'] >= score_threshold, 'passed'] = True
    # scored_df.loc[scored_df['score'] < score_threshold, 'passed'] = False

    return pd.DataFrame(scored_df)

# --------------------------
#       export results
# --------------------------

if __name__ == '__main__':
    result = main_function(grouped_df)
    # print(result)
    # result.to_csv("/Users/jonas/Workspace/Local/Drop/channel-progression-stats.csv")

# pivot table with scores by address count
    overview = result.pivot_table(columns=['score'], aggfunc='size')

# plotted pivot table
    overview.plot.hist(grid=True, bins=20, rwidth=0.9,
             color='#607c8e')
    plt.title('Sybil score distribution')
    plt.ylabel('Sybil score')
    plt.xlabel('Address count')
    plt.grid(axis='y', alpha=0.75)
    
    plt.show()