import pandas as pd

# Pandas ayarları: Tablo gösterimini iyileştirmek için
pd.set_option('display.max_columns', None)    # Tüm sütunları göster
pd.set_option('display.width', 500)           # Tablo genişliği
pd.set_option('display.expand_frame_repr', False)  # Tablonun alt satıra taşınmasını engelle

# Veri setlerini yükleme
movie = pd.read_csv("datasets/Netflix_Dataset_Movie.csv")      # Film bilgileri
ratings = pd.read_csv("datasets/Netflix_Dataset_Rating.csv")   # Kullanıcı değerlendirmeleri

# Film ve değerlendirme verilerini birleştirme
df = ratings.merge(movie, how='left', on='Movie_ID')

# Temel istatistikler
print("Benzersiz kullanıcı sayısı:", df['User_ID'].nunique())
print("Benzersiz film sayısı:", df['Movie_ID'].nunique())
print("En az izlenen film sayısı:", df['Movie_ID'].value_counts().min())
print("En çok izlenen film sayısı:", df['Movie_ID'].value_counts().max())

# Kullanıcı-Film matrisi oluşturma (Pivot table)
# Her kullanıcının her filme verdiği puanları gösteren matris
users_movie_df = df.pivot_table(index=['User_ID'], columns=['Movie_ID'], values='Rating')

# Rastgele bir kullanıcı seçme (örneklem için)
random_user = int(pd.Series(users_movie_df.index).sample(1, random_state=67))
print(f"Seçilen rastgele kullanıcı ID: {random_user}")

# Seçilen kullanıcının izlediği filmleri bulma
random_user_df = users_movie_df[users_movie_df.index == random_user]
movies_watched = users_movie_df.columns[random_user_df.notna().any().tolist()]
print(f"Seçilen kullanıcının izlediği film sayısı: {len(movies_watched)}")

# AYNI FİLMLERİ İZLEYEN KULLANICILARI BULMA

# Seçilen kullanıcının izlediği tüm filmleri izleyen diğer kullanıcılar
same_movie_watched = users_movie_df[movies_watched]

# Her kullanıcının seçilen kullanıcıyla kaç ortak film izlediğini hesaplama
same_movie_count = same_movie_watched.T.notnull().sum().sort_values(ascending=False)
same_movie_count = same_movie_count.reset_index()
same_movie_count.columns = ['User_ID', 'Movie_Count']

# Seçilen kullanıcının izlediği filmlerin en az %65'ini izleyen kullanıcıları filtreleme
perc = len(movies_watched) * 65 / 100
same_movie_count = same_movie_count[same_movie_count['Movie_Count'] >= perc]['User_ID']
print(f"Benzer izleme alışkanlığı olan kullanıcı sayısı: {len(same_movie_count)}")

# Filtrelenmiş kullanıcılar için final dataframe oluşturma
final_df = users_movie_df[users_movie_df.index.isin(same_movie_count)]

# KORELASYON HESAPLAMA

# Kullanıcılar arası korelasyon matrisi oluşturma
corr_df = final_df.T.corr().unstack().drop_duplicates().sort_values(ascending=False)

# Korelasyon verisini düzenli dataframe formatına çevirme
corr_df = pd.DataFrame(corr_df, columns=["corr"])
corr_df.index.names = ['user_id_1', 'user_id_2']
corr_df = corr_df.reset_index()

# Seçilen kullanıcıyla yüksek korelasyonu (>0.55) olan kullanıcıları bulma
top_users = corr_df[(corr_df["corr"] > 0.55) & (corr_df['user_id_1'] == random_user)][['user_id_2', 'corr']]
top_users.columns = ['User_ID', 'Corr']
print(f"Yüksek korelasyonlu kullanıcı sayısı: {len(top_users)}")

# TAVSİYE SİSTEMİ OLUŞTURMA

# Benzer kullanıcıların değerlendirmelerini getirme
top_users_rating = top_users.merge(ratings, how='left', on='User_ID')
top_users_rating.reset_index(inplace=True)

# Ağırlıklı puan hesaplama: Korelasyon × Rating
top_users_rating['weighted_rating'] = top_users_rating['Corr'] * top_users_rating['Rating']

# Ağırlıklı puana göre sıralama
top_users_rating = top_users_rating.sort_values(by=['weighted_rating'], ascending=False)

print("\nEn yüksek ağırlıklı puan alan 10 değerlendirme:")
print(top_users_rating.head(10))

# FİLM TAVSİYELERİNİ HAZIRLAMA

# Film bazında ortalama ağırlıklı puanları hesaplama
recommendation_df = top_users_rating.groupby('Movie_ID').agg({'weighted_rating': 'mean'}).sort_values(by=['weighted_rating'], ascending=False)

# Seçilen kullanıcının izlemediği filmlerden en iyi 5 tavsiyeyi seçme
recommendation_top_5 = (recommendation_df[~recommendation_df.index.isin(movies_watched)]
                        .head(5)
                        .reset_index())

# Tavsiye edilen film isimlerini getirme
recommended_titles = movie[movie['Movie_ID'].isin(recommendation_top_5['Movie_ID'])]['Name'].tolist()

print("\n📽️ TAVSİYE EDİLEN FİLMLER:")
for i, title in enumerate(recommended_titles, 1):
    print(f"{i}. {title}")
