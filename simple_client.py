"""
간단한 클라이언트 - 핵심 로직만
"""
import requests
import argparse

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

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--url", default="http://localhost:8000")
    parser.add_argument("--message", required=True)
    parser.add_argument("--stream", action="store_true")
    args = parser.parse_args()
    
    if args.stream:
        test_streaming(args.url, args.message)
    else:
        test_normal(args.url, args.message)