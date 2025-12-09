# vLLM HuggingFace Model Server

## 설치

```bash
pip install -r requirements.txt
```

## 사용법

### 서버 실행
```bash
python simple_server.py --model microsoft/DialoGPT-medium
```

### 클라이언트 테스트
```bash
# 일반 응답
python simple_client.py --message "Hello"

# 스트리밍 응답  
python simple_client.py --message "Hello" --stream
```