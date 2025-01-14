# ======================================================================================================================
# CompareRatingDistributions.py visualises the difference in rating distributions between two specified clubs in the
# selected format. Written by ZenPossum :)
# ======================================================================================================================

from chessdotcom import client, get_player_stats
from FilterFunctions import get_all_members
import time
import numpy as np
import pandas as pd
from matplotlib import pyplot as plt

# Set up user agent
client.Client.request_config['headers']['User-Agent'] = (
    'TeamAustraliaAdminScripts '
    'Contact me at aidan.cash93@gmail.com'
)

# Set up clubs and the format for ratings to compare
club1 = 'team-australia'
club2 = 'team-of-the-czech-republic'
format = 'chess_daily'

# Get members of both clubs
print(f'Program started. Downloading club members from "{club1}" and "{club2}".')
club_members = {club1: get_all_members(club1),
                club2: get_all_members(club2)}
club_ratings = {club1: [], club2: []}

# Set looping variables
N = len(club_members[club1] + club_members[club2])
n = 1
last_time = time.time()
print(f'Members downloaded. Processing {N} combined members.')

# Loop through clubs and members
for club, member_list in club_members.items():
    for member in member_list:
        if n % 50 == 0:
            # Display estimated time every 50 members
            current_time = time.time()
            estimated_time_remaining = (N - n) * (current_time - last_time) / 50 / 60
            last_time = current_time
            print(f'Processing member {n} of {N}. Estimated time remaining: '
                  f'{pd.Timedelta(estimated_time_remaining, "min").round(freq="s")}.')
        try:
            # Get member's rating from API
            rating = get_player_stats(member).json['stats'][format]['last']['rating']
            club_ratings[club].append(rating)
        except KeyError:
            # If they don't have a rating in the format specified
            pass
        n += 1

# Print average ratings
for club in [club1, club2]:
    print(f'{club} average rating: {round(np.mean(club_ratings[club]))}')

# Plot back-to-back histograms. Adapted from code by Boris Gorelik
# (https://stackoverflow.com/questions/1340338/back-to-back-histograms-in-matplotlib}
h0 = plt.hist(club_ratings[club1]+club_ratings[club2], orientation='horizontal', rwidth=0.8, )
plt.close()
hN = plt.hist(club_ratings[club2], bins=h0[1], orientation='horizontal', rwidth=0.8, label=club2)
hS = plt.hist(club_ratings[club1], bins=hN[1], orientation='horizontal', rwidth=0.8, label=club1)
for p in hS[2]:
    p.set_width(- p.get_width())
x_min = min([min(w.get_width() for w in hS[2]),
             min([w.get_width() for w in hN[2]])])
x_min = np.floor(x_min)
x_max = max([max(w.get_width() for w in hS[2]),
             max([w.get_width() for w in hN[2]])])
x_max = np.ceil(x_max)
range = x_max - x_min
delta = 0.0 * range
plt.xlim([x_min - delta, x_max + delta])
xt = plt.xticks()
n = xt[0]
s = ['%.1f' % abs(i) for i in n]
plt.xticks(n, s)
plt.legend(loc='best')
plt.axvline(0.0, lw=1, alpha=0.6, color='k')
plt.title('Rating distributions')
plt.xlabel('Count')
plt.ylabel('Rating')
plt.show()
