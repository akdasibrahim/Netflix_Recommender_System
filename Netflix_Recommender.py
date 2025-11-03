import pandas as pd


pd.set_option('display.max_columns', None)
pd.set_option('display.width', 500)
pd.set_option('display.expand_frame_repr', False)


movie = pd.read_csv("datasets/Netflix_Dataset_Movie.csv")
ratings = pd.read_csv("datasets/Netflix_Dataset_Rating.csv")

df = ratings.merge(movie, how='left', on='Movie_ID')

df['User_ID'].nunique()
df['Movie_ID'].nunique()

df['Movie_ID'].value_counts().min()
df['Name'].value_counts().max()

users_movie_df = df.pivot_table(index=['User_ID'], columns=['Movie_ID'], values='Rating')

random_user = int(pd.Series(users_movie_df.index).sample(1, random_state=67))
random_user_df = users_movie_df[users_movie_df.index == random_user]
movies_wacthed = users_movie_df.columns[random_user_df.notna().any().tolist()]

len(movies_wacthed)

## 175 filmi izleyen kullancıların ID'si ile yeni bir dataframe oluşturuyoruz

same_movie_wacthed = users_movie_df[movies_wacthed]
same_movie_count = same_movie_wacthed.T.notnull().sum().sort_values(ascending=False)
same_movie_count = same_movie_count.reset_index()
perc = len(movies_wacthed) *65 / 100
same_movie_count.columns = ['User_ID', 'Movie_Count']
same_movie_count = same_movie_count[same_movie_count['Movie_Count'] >= perc]['User_ID']

# aynı filmlerin %65 ini izleyen kullanıcıların ID'lerine ulaştık

final_df = users_movie_df[users_movie_df.index.isin(same_movie_count)]

corr_df = final_df.T.corr().unstack().drop_duplicates().sort_values(ascending=False)

corr_df = pd.DataFrame(corr_df, columns=["corr"])
corr_df.index.names = ['user_id_1', 'user_id_2']
corr_df = corr_df.reset_index()

top_users = corr_df[(corr_df["corr"]>0.55) & (corr_df['user_id_1'] == random_user)][['user_id_2', 'corr']]
top_users.columns = ['User_ID', 'Corr']
top_users_rating = top_users.merge(ratings, how='left', on='User_ID')
top_users_rating.reset_index( inplace=True)
top_users_rating['weighted_rating'] = top_users_rating['Corr'] * top_users_rating['Rating']

top_users_rating = top_users_rating.sort_values(by=['weighted_rating'], ascending=False)

top_users_rating.head(10)

recommendation_df = top_users_rating.groupby('Movie_ID').agg({'weighted_rating': 'mean'}).sort_values(by=['weighted_rating'], ascending=False)

recommendation_top_5 = (recommendation_df[~recommendation_df.index.isin(movies_wacthed)]
    .head(5)
    .reset_index())

recommended_titles = movie[movie['Movie_ID'].isin(recommendation_top_5['Movie_ID'])]['Name'].tolist()
for title in recommended_titles:
    print(title)

