"""
간단한 클라이언트 - 텍스트/이미지 생성 지원
"""
import requests
import argparse
import base64
import os
from datetime import datetime

def test_normal(url: str, message: str):
    """일반 응답 테스트"""
    response = requests.post(f"{url}/chat", json={
        "message": message,
        "stream": False
    })
    result = response.json()
    print(f"💬 일반 응답: '{result['response']}'")

def test_streaming(url: str, message: str):
    """스트리밍 응답 테스트"""
    response = requests.post(f"{url}/chat", json={
        "message": message,
        "stream": True
    }, stream=True)
    
    print("🔄 스트리밍 응답:")
    chunk_count = 0
    
    for line in response.iter_lines():
        if line:
            line = line.decode('utf-8')
            if line.startswith('data: '):
                data = line[6:]
                if data == '[DONE]':
                    print("\n✅ 완료")
                    break
                chunk_count += 1
                print(f"[{chunk_count:02d}] '{data}'")

def test_image_generation(url: str, prompt: str, steps: int = 20):
    """이미지 생성 테스트"""
    print(f"🎨 이미지 생성 중... ('{prompt}', {steps} steps)")
    
    response = requests.post(f"{url}/image", json={
        "prompt": prompt,
        "steps": steps
    })
    
    result = response.json()
    
    if "error" in result:
        print(f"❌ 에러: {result['error']}")
        return
    
    # base64 이미지 디코딩 및 저장
    image_data = result["image"]
    if image_data.startswith("data:image/png;base64,"):
        image_data = image_data[len("data:image/png;base64,"):]
    
    image_bytes = base64.b64decode(image_data)
    
    # 파일명 생성 (타임스탬프 포함)
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"generated_image_{timestamp}.png"
    
    with open(filename, "wb") as f:
        f.write(image_bytes)
    
    print(f"✅ 이미지 저장됨: {filename}")
    print(f"   프롬프트: '{result['prompt']}'")
    print(f"   스텝: {result['steps']}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--url", default="http://localhost:8000")
    parser.add_argument("--message", help="Text message for chat")
    parser.add_argument("--prompt", help="Image generation prompt")
    parser.add_argument("--stream", action="store_true", help="Use streaming for chat")
    parser.add_argument("--steps", type=int, default=20, help="Number of inference steps for image generation")
    args = parser.parse_args()
    
    if args.prompt:
        # 이미지 생성 모드
        test_image_generation(args.url, args.prompt, args.steps)
    elif args.message:
        # 텍스트 채팅 모드
        if args.stream:
            test_streaming(args.url, args.message)
        else:
            test_normal(args.url, args.message)
    else:
        print("--message 또는 --prompt 중 하나를 제공해야 합니다.")
        print("텍스트 채팅: --message 'Hello'")
        print("이미지 생성: --prompt 'a cat sitting on a table'")