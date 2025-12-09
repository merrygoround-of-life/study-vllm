# vLLM HuggingFace Model Server

텍스트 생성(vLLM)과 이미지 생성(diffusers)을 지원하는 통합 서버

## 기능

- **텍스트 생성**: vLLM을 통한 고성능 언어 모델 추론
- **이미지 생성**: diffusers를 통한 Stable Diffusion 모델 추론  
- **스트리밍**: 실시간 토큰 생성
- **멀티 플랫폼**: CUDA, MPS(Apple Silicon), CPU 자동 감지

## 설치

```bash
pip install -r requirements.txt
```

## 사용법

### 서버 실행

```bash
# 텍스트만 (기존과 동일)
python simple_server.py --model microsoft/DialoGPT-medium

# 텍스트 + 이미지 생성
python simple_server.py --model microsoft/DialoGPT-medium --image-model nota-ai/bk-sdm-tiny

# 포트 변경
python simple_server.py --model microsoft/DialoGPT-medium --image-model nota-ai/bk-sdm-tiny --port 8080
```

### 클라이언트 사용

#### 텍스트 생성
```bash
# 일반 응답
python simple_client.py --message "Hello"

# 스트리밍 응답  
python simple_client.py --message "Hello" --stream
```

#### 이미지 생성
```bash
# 기본 이미지 생성 (20 steps)
python simple_client.py --prompt "a cat sitting on a table"

# 고품질 이미지 생성 (더 많은 steps)
python simple_client.py --prompt "a beautiful sunset over mountains" --steps 50
```

## 지원 모델

### 텍스트 모델 (vLLM)
- `microsoft/DialoGPT-medium` - 대화형 모델
- 기타 vLLM 호환 모델

### 이미지 모델 (diffusers)
- `nota-ai/bk-sdm-tiny` - 컴팩트 Stable Diffusion (0.50B 파라미터)
- `OFA-Sys/small-stable-diffusion-v0` - 소형 Stable Diffusion
- 기타 Stable Diffusion 호환 모델

## API 엔드포인트

- `POST /chat` - 텍스트 생성
  - `{message: str, stream: bool}`
  - 반환: JSON 또는 Server-Sent Events
  
- `POST /image` - 이미지 생성  
  - `{prompt: str, steps: int}`
  - 반환: base64 인코딩된 PNG 이미지