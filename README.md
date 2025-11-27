# Film Tavsiye Sistemi

Bu proje, kullanıcı benzerliği temelli bir işbirlikçi filtreleme (collaborative filtering) algoritması kullanarak film tavsiyeleri üretir.

<img width="225" height="225" alt="image" src="https://github.com/user-attachments/assets/91edda2d-d94c-42aa-8d5f-13e194da375a" />

## 🎯 Çalışma Prensibi

1. **Veri Hazırlama**: Netflix veri setinden kullanıcı-film değerlendirme matrisi oluşturulur
2. **Benzer Kullanıcı Bulma**: Rastgele seçilen bir kullanıcıyla benzer izleme alışkanlıkları olan kullanıcılar bulunur
3. **Korelasyon Hesaplama**: Kullanıcılar arası benzerlik korelasyon ile ölçülür
4. **Ağırlıklı Puanlama**: Benzer kullanıcıların değerlendirmeleri korelasyon katsayılarıyla ağırlıklandırılır
5. **Tavsiye Üretme**: En yüksek ağırlıklı puana sahip filmler tavsiye edilir
