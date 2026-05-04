"""Module 2: Hybrid Search — BM25 (Vietnamese) + Dense + RRF."""

import os, sys
from dataclasses import dataclass

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from config import (QDRANT_HOST, QDRANT_PORT, COLLECTION_NAME, EMBEDDING_MODEL,
                    EMBEDDING_DIM, BM25_TOP_K, DENSE_TOP_K, HYBRID_TOP_K)


@dataclass
class SearchResult:
    text: str
    score: float
    metadata: dict
    method: str  # "bm25", "dense", "hybrid"


def segment_vietnamese(text: str) -> str:
    """Segment Vietnamese text into words."""
    try:
        # 1. Thử import underthesea để tách từ
        from underthesea import word_tokenize
        
        # 2. Thực hiện tách từ với định dạng "text" (nối các từ bằng dấu gạch dưới)
        # Ví dụ: "nghỉ phép năm" -> "nghỉ_phép năm"
        return word_tokenize(text, format="text")
        
    except (ImportError, Exception):
        # Fallback: Nếu không có thư viện hoặc lỗi, trả về text gốc 
        # (Chuyển về lowercase để đồng bộ hóa cho BM25)
        return text.lower()


class BM25Search:
    def __init__(self):
        self.corpus_tokens = []
        self.documents = []
        self.bm25 = None

    def index(self, chunks: list[dict]) -> None:
        """Build BM25 index from chunks."""
        # 1. Lưu trữ chunks để truy xuất sau này
        self.documents = chunks
        
        # 2. Xử lý từng chunk: tách từ tiếng Việt và chia thành list các token
        # Ví dụ: "Tôi đi nghỉ phép" -> ["tôi", "đi", "nghỉ_phép"]
        self.corpus_tokens = [
            segment_vietnamese(chunk["text"]).split() 
            for chunk in chunks
        ]
        
        # 3. Khởi tạo mô hình BM25Okapi[cite: 2]
        try:
            from rank_bm25 import BM25Okapi
            self.bm25 = BM25Okapi(self.corpus_tokens)
        except ImportError:
            # Fallback: Nếu thiếu thư viện, bạn cần log cảnh báo 
            # và có thể dùng một bộ scorer đơn giản dựa trên token overlap[cite: 2]
            print("Warning: rank_bm25 not installed. Search may fail.")
            self.bm25 = None

    def search(self, query: str, top_k: int = BM25_TOP_K) -> list[SearchResult]:
        """Search using BM25."""
        if not self.bm25 or not self.documents:
            return []

        # 1. Tokenize câu truy vấn tương tự như lúc index[cite: 2]
        tokenized_query = segment_vietnamese(query).split()
        
        # 2. Tính toán điểm số mức độ liên quan cho toàn bộ corpus[cite: 2]
        scores = self.bm25.get_scores(tokenized_query)
        
        # 3. Lấy ra top_k vị trí có điểm cao nhất[cite: 2]
        top_indices = sorted(
            range(len(scores)), 
            key=lambda i: scores[i], 
            reverse=True
        )[:top_k]
        
        # 4. Đóng gói kết quả vào đối tượng SearchResult[cite: 2]
        results = []
        for i in top_indices:
            # Tối ưu: Bỏ qua các tài liệu có score = 0 nếu không cần thiết[cite: 2]
            if scores[i] > 0 or len(results) < top_k:
                results.append(SearchResult(
                    text=self.documents[i]["text"],
                    score=float(scores[i]),
                    metadata=self.documents[i].get("metadata", {}),
                    method="bm25" # Định danh để RRF phân biệt[cite: 2]
                ))
                
        return results


class DenseSearch:
    def __init__(self):
        from qdrant_client import QdrantClient
        self.client = QdrantClient(host=QDRANT_HOST, port=QDRANT_PORT)
        self._encoder = None

    def _get_encoder(self):
        if self._encoder is None:
            from sentence_transformers import SentenceTransformer
            self._encoder = SentenceTransformer(EMBEDDING_MODEL)
        return self._encoder

    def index(self, chunks: list[dict], collection: str = COLLECTION_NAME) -> None:
        """Index chunks into Qdrant."""
        from qdrant_client.models import Distance, VectorParams, PointStruct
        
        # 1. Khởi tạo/Làm mới collection trong Qdrant
        # Sử dụng khoảng cách COSINE để đo lường sự tương đồng giữa các vector
        self.client.recreate_collection(
            collection_name=collection,
            vectors_config=VectorParams(size=EMBEDDING_DIM, distance=Distance.COSINE)
        )
        
        # 2. Trích xuất nội dung văn bản và tạo embedding
        texts = [c["text"] for c in chunks]
        vectors = self._get_encoder().encode(texts, show_progress_bar=True)
        
        # 3. Đóng gói dữ liệu thành các "điểm" (Points) để upsert vào Qdrant
        points = []
        for i, (vector, chunk) in enumerate(zip(vectors, chunks)):
            points.append(PointStruct(
                id=i,
                vector=vector.tolist(),
                # Payload lưu cả nội dung text và metadata để truy xuất sau này
                payload={
                    **chunk.get("metadata", {}), 
                    "text": chunk["text"]
                }
            ))
        
        # 4. Đẩy dữ liệu lên Qdrant
        self.client.upsert(collection_name=collection, points=points)

    def search(self, query: str, top_k: int = DENSE_TOP_K, collection: str = COLLECTION_NAME) -> list[SearchResult]:
        """Search using dense vectors."""
        # 1. Chuyển đổi câu truy vấn thành vector[cite: 2]
        query_vector = self._get_encoder().encode(query).tolist()
        
        # 2. Thực hiện tìm kiếm top_k kết quả gần nhất trong Qdrant.
        # qdrant-client < 1.10 exposes search(), newer versions use query_points().
        if hasattr(self.client, "search"):
            hits = self.client.search(
                collection_name=collection,
                query_vector=query_vector,
                limit=top_k
            )
        else:
            response = self.client.query_points(
                collection_name=collection,
                query=query_vector,
                limit=top_k,
                with_payload=True,
            )
            hits = response.points
        
        # 3. Chuyển đổi kết quả từ Qdrant sang định dạng SearchResult của hệ thống[cite: 2]
        results = [
            SearchResult(
                text=hit.payload["text"],
                score=hit.score,
                metadata={k: v for k, v in hit.payload.items() if k != "text"},
                method="dense" # Định danh quan trọng cho bước RRF[cite: 2]
            )
            for hit in hits
        ]
        
        return results


def reciprocal_rank_fusion(results_list: list[list[SearchResult]], k: int = 60,
                           top_k: int = HYBRID_TOP_K) -> list[SearchResult]:
    """Merge ranked lists using RRF: score(d) = Σ 1/(k + rank)."""
    # 1. Khởi tạo dictionary để lưu trữ điểm số RRF và đối tượng SearchResult tương ứng
    # Dùng text của tài liệu làm khóa (key) để nhận diện các tài liệu trùng nhau
    rrf_scores = {}  # text -> {"score": float, "result": SearchResult}

    # 2. Duyệt qua từng danh sách kết quả (ví dụ: danh sách từ BM25, danh sách từ Dense)
    for result_list in results_list:
        for rank, result in enumerate(result_list):
            if result.text not in rrf_scores:
                # Nếu tài liệu chưa có trong dict, khởi tạo với score = 0
                # Lưu lại một bản sao của result để giữ metadata
                rrf_scores[result.text] = {"score": 0.0, "result": result}
            
            # Cộng dồn điểm RRF theo công thức: 1 / (k + rank + 1)[cite: 2]
            # rank + 1 vì rank trong enumerate bắt đầu từ 0[cite: 2]
            rrf_scores[result.text]["score"] += 1.0 / (k + rank + 1)

    # 3. Chuyển dict thành list và sắp xếp theo điểm số giảm dần[cite: 2]
    sorted_items = sorted(
        rrf_scores.values(), 
        key=lambda x: x["score"], 
        reverse=True
    )

    # 4. Trả về top_k SearchResult với định danh phương pháp là "hybrid"[cite: 2]
    hybrid_results = []
    for item in sorted_items[:top_k]:
        res = item["result"]
        hybrid_results.append(SearchResult(
            text=res.text,
            score=item["score"],
            metadata=res.metadata,
            method="hybrid"  # Định danh bắt buộc cho kết quả hợp nhất[cite: 2]
        ))
    
    return hybrid_results


class HybridSearch:
    """Combines BM25 + Dense + RRF. (Đã implement sẵn — dùng classes ở trên)"""
    def __init__(self):
        self.bm25 = BM25Search()
        self.dense = DenseSearch()

    def index(self, chunks: list[dict]) -> None:
        self.bm25.index(chunks)
        self.dense.index(chunks)

    def search(self, query: str, top_k: int = HYBRID_TOP_K) -> list[SearchResult]:
        bm25_results = self.bm25.search(query, top_k=BM25_TOP_K)
        dense_results = self.dense.search(query, top_k=DENSE_TOP_K)
        return reciprocal_rank_fusion([bm25_results, dense_results], top_k=top_k)


if __name__ == "__main__":
    print(f"Original:  Nhân viên được nghỉ phép năm")
    print(f"Segmented: {segment_vietnamese('Nhân viên được nghỉ phép năm')}")
