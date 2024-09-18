# Lazada crawler

## Mô tả

Lấy dữ liệu thô bình luận và đánh giá mặt hàng cho bài tập lớn môn Học sâu và ứng dụng.

## Cách chạy

1. Cài đặt các thư viện cần thiết

```bash
pip install -r requirements.txt
```

2. Chạy crawler để lấy các đường dẫn sản phẩm (đã chạy sẵn và lưu vào file `urls.txt`)

```bash
python CrawlLinks.py
```

3. Chạy scraper để lấy dữ liệu bình luận và đánh giá


```bash
python scraper.py
```
Mỗi lần chạy batch 5 url, dữ liệu tạm thời được ghi vào products.json và từ đó ghi ra file `reviews.csv` theo format: `rating, review`
> Lưu ý:
> - Thỉnh thoảng cần xác nhận CAPTCHA để tiếp tục crawl
> - Khi chạy đôi khi có popup "Giao hàng từ nước ngoài", nếu để yên thì sẽ không crawl được bình luận cho sản phẩm đó thôi

4. Sau khi chạy hết file `urls.txt`, xóa file `last_processed_url.txt` và chạy lại `CrawlLinks.py` để lấy loạt url tiếp theo. Lặp lại bước 3.
